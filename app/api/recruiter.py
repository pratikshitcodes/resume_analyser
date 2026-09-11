import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Response, status
from sqlalchemy.orm import Session
from ..core.database import get_db, SessionLocal
from ..core.config import settings
from ..auth.deps import require_recruiter, get_current_user
from ..models import (
    User, Resume, ParsedProfile, ATSAnalysis, Job, 
    MatchResult, InterviewSlot, ChatSession, ChatMessage
)
from ..schemas import (
    JobCreate, JobResponse, MatchResultResponse, RankedCandidateResponse, 
    ChatRequest, ChatResponse, SlotCreate, SlotResponse, TaskStatusResponse
)
from ..services.parser import extract_text_from_file, parse_resume_content, parse_job_description_content
from ..services.ats import analyze_resume_ats
from ..services.matcher import match_candidate_to_job, rank_candidates_for_job
from ..services.export import generate_csv_export, generate_json_export, generate_pdf_report
from ..services.task_manager import task_manager
from ..services.ai.factory import get_ai_provider

router = APIRouter(prefix="/recruiter", tags=["Recruiter Mode"])

@router.post("/jobs", response_model=JobResponse)
def create_job(
    job_in: JobCreate,
    current_user: User = Depends(require_recruiter),
    db: Session = Depends(get_db)
):
    # Auto-extract skills and structure from JD description
    parsed_jd = parse_job_description_content(job_in.description)

    job = Job(
        recruiter_id=current_user.id,
        title=job_in.title or parsed_jd.get("title", "Job Role"),
        company=job_in.company or parsed_jd.get("company", "Company"),
        description=job_in.description,
        required_skills=parsed_jd.get("required_skills", []),
        nice_to_have_skills=parsed_jd.get("nice_to_have_skills", []),
        qualifications=parsed_jd.get("qualifications", []),
        responsibilities=parsed_jd.get("responsibilities", []),
        experience_required=job_in.experience_required or parsed_jd.get("experience_required")
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

@router.get("/jobs", response_model=List[JobResponse])
def list_jobs(
    current_user: User = Depends(require_recruiter),
    db: Session = Depends(get_db)
):
    return db.query(Job).filter(Job.recruiter_id == current_user.id).order_by(Job.created_at.desc()).all()

@router.get("/jobs/{job_id}", response_model=JobResponse)
def get_job(
    job_id: str,
    current_user: User = Depends(require_recruiter),
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.id == job_id, Job.recruiter_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    return job

# Background batch resume processing worker coroutine
async def process_batch_resumes_task(task_id: str, job_id: str, file_paths: List[str]):
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise ValueError(f"Job {job_id} not found")

        job_data = {
            "title": job.title,
            "company": job.company,
            "required_skills": job.required_skills,
            "nice_to_have_skills": job.nice_to_have_skills,
            "experience_required": job.experience_required,
            "description": job.description
        }

        total_files = len(file_paths)
        processed = 0
        successful = 0
        failed = 0

        for idx, file_path in enumerate(file_paths):
            path_obj = Path(file_path)
            try:
                raw_text, links = extract_text_from_file(path_obj)
                profile_data = parse_resume_content(raw_text, links)
                ats_data = analyze_resume_ats(profile_data, raw_text)

                cand_name = profile_data.get("name") or path_obj.stem
                cand_email = profile_data.get("contact_info", {}).get("email") or f"applicant_{idx+1}@example.com"

                # Find or create candidate user
                cand_user = db.query(User).filter(User.email == cand_email).first()
                if not cand_user:
                    cand_user = User(
                        email=cand_email,
                        password_hash="batch_import",
                        full_name=cand_name,
                        role="candidate"
                    )
                    db.add(cand_user)
                    db.commit()
                    db.refresh(cand_user)

                # Save Resume
                resume = Resume(
                    candidate_id=cand_user.id,
                    file_url=str(file_path),
                    file_name=path_obj.name,
                    raw_text=raw_text,
                    parsed_json=profile_data
                )
                db.add(resume)
                db.commit()
                db.refresh(resume)

                # Save Profile & ATS
                parsed_profile = ParsedProfile(
                    resume_id=resume.id,
                    name=cand_name,
                    contact_info=profile_data.get("contact_info", {}),
                    skills=profile_data.get("skills", []),
                    experience=profile_data.get("experience", []),
                    education=profile_data.get("education", []),
                    projects=profile_data.get("projects", []),
                    certifications=profile_data.get("certifications", []),
                    achievements=profile_data.get("achievements", []),
                    total_experience_years=float(profile_data.get("total_experience_years", 0.0))
                )
                db.add(parsed_profile)

                ats_analysis = ATSAnalysis(
                    resume_id=resume.id,
                    ats_score=ats_data.get("ats_score", 75),
                    strengths=ats_data.get("strengths", []),
                    weaknesses=ats_data.get("weaknesses", []),
                    suggestions=ats_data.get("suggestions", []),
                    best_project_analysis=ats_data.get("best_project_analysis", "")
                )
                db.add(ats_analysis)

                # Match against Job
                match_data = match_candidate_to_job(profile_data, job_data)
                match_res = MatchResult(
                    job_id=job_id,
                    candidate_id=cand_user.id,
                    resume_id=resume.id,
                    match_score=match_data.get("match_score", 70),
                    matched_skills=match_data.get("matched_skills", []),
                    missing_skills=match_data.get("missing_skills", []),
                    classification=match_data.get("classification", "maybe"),
                    ranking_explanation=match_data.get("ranking_explanation", ""),
                    evidence_quotes=match_data.get("evidence_quotes", [])
                )
                db.add(match_res)
                db.commit()
                successful += 1
            except Exception as e:
                failed += 1
            finally:
                processed += 1
                progress = int((processed / max(total_files, 1)) * 100)
                task_manager.update_task(
                    task_id=task_id,
                    progress=progress,
                    message=f"Processed {processed}/{total_files} resumes ({successful} succeeded, {failed} failed)"
                )

        return {
            "total": total_files,
            "successful": successful,
            "failed": failed,
            "job_id": job_id
        }
    finally:
        db.close()

@router.post("/jobs/{job_id}/batch-upload", response_model=TaskStatusResponse)
async def batch_upload_resumes(
    job_id: str,
    files: List[UploadFile] = File(...),
    current_user: User = Depends(require_recruiter),
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.id == job_id, Job.recruiter_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    saved_file_paths = []
    batch_dir = settings.UPLOAD_DIR / f"batch_{job_id}_{int(datetime.now().timestamp())}"
    batch_dir.mkdir(parents=True, exist_ok=True)

    for file in files:
        file_path = batch_dir / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Check if zip archive
        if file.filename.endswith(".zip"):
            try:
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    extract_dir = batch_dir / "unzipped"
                    zip_ref.extractall(extract_dir)
                    for root, _, extracted_files in os.walk(extract_dir):
                        for ef in extracted_files:
                            if ef.lower().endswith(('.pdf', '.docx', '.txt')):
                                saved_file_paths.append(os.path.join(root, ef))
            except Exception:
                pass
        elif file.filename.lower().endswith(('.pdf', '.docx', '.txt')):
            saved_file_paths.append(str(file_path))

    if not saved_file_paths:
        raise HTTPException(status_code=400, detail="No valid resume files (.pdf, .docx, .txt) found.")

    # Dispatch to background task runner
    task_id = task_manager.run_async(process_batch_resumes_task, job_id, saved_file_paths)

    return TaskStatusResponse(
        task_id=task_id,
        status="processing",
        progress=0,
        message=f"Queued {len(saved_file_paths)} resumes for background extraction and matching"
    )

@router.get("/jobs/{job_id}/rankings", response_model=List[RankedCandidateResponse])
def get_job_rankings(
    job_id: str,
    classification: Optional[str] = None, # shortlist | maybe | reject
    current_user: User = Depends(require_recruiter),
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.id == job_id, Job.recruiter_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    query = db.query(MatchResult).filter(MatchResult.job_id == job_id)
    if classification:
        query = query.filter(MatchResult.classification == classification.lower())

    results = query.order_by(MatchResult.match_score.desc()).all()
    
    ranked_list = []
    for rank, m in enumerate(results, start=1):
        cand = m.candidate
        profile = m.resume.profile if m.resume else None
        
        ranked_list.append(RankedCandidateResponse(
            rank=rank,
            match_id=m.id,
            candidate_id=m.candidate_id,
            candidate_name=profile.name if profile and profile.name else (cand.full_name or "Candidate"),
            candidate_email=cand.email,
            resume_id=m.resume_id,
            match_score=m.match_score,
            classification=m.classification,
            matched_skills=m.matched_skills or [],
            missing_skills=m.missing_skills or [],
            total_experience_years=profile.total_experience_years if profile else 0.0,
            ranking_explanation=m.ranking_explanation or "Matched against core job competencies.",
            evidence_quotes=m.evidence_quotes or []
        ))
    return ranked_list

@router.post("/jobs/{job_id}/chat", response_model=ChatResponse)
def recruiter_chat(
    job_id: str,
    req: ChatRequest,
    current_user: User = Depends(require_recruiter),
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.id == job_id, Job.recruiter_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    # Fetch top candidates
    matches = db.query(MatchResult).filter(MatchResult.job_id == job_id).order_by(MatchResult.match_score.desc()).all()
    candidates_data = []
    for m in matches:
        profile = m.resume.profile if m.resume else None
        candidates_data.append({
            "candidate_id": m.candidate_id,
            "name": profile.name if profile else m.candidate.full_name,
            "email": m.candidate.email,
            "match_score": m.match_score,
            "classification": m.classification,
            "skills": profile.skills if profile else [],
            "experience_years": profile.total_experience_years if profile else 0,
            "matched_skills": m.matched_skills,
            "ranking_explanation": m.ranking_explanation
        })

    job_data = {
        "title": job.title,
        "company": job.company,
        "required_skills": job.required_skills,
        "nice_to_have_skills": job.nice_to_have_skills,
        "description": job.description
    }

    # Find or create chat session
    session = None
    if req.session_id:
        session = db.query(ChatSession).filter(ChatSession.id == req.session_id, ChatSession.user_id == current_user.id).first()
    if not session:
        session = ChatSession(
            user_id=current_user.id,
            role_context="recruiter",
            linked_job_id=job.id
        )
        db.add(session)
        db.commit()
        db.refresh(session)

    history = [{"role": msg.role, "content": msg.content} for msg in session.messages[-6:]]

    ai = get_ai_provider()
    ai_result = ai.chat_recruiter(req.message, candidates_data, job_data, history)

    # Save messages
    user_msg = ChatMessage(session_id=session.id, role="user", content=req.message)
    asst_msg = ChatMessage(
        session_id=session.id,
        role="assistant",
        content=ai_result.get("reply", ""),
        context_sources=ai_result.get("context_sources", [])
    )
    db.add(user_msg)
    db.add(asst_msg)
    db.commit()

    return ChatResponse(
        session_id=session.id,
        reply=ai_result.get("reply", ""),
        context_sources=ai_result.get("context_sources", [])
    )

@router.post("/jobs/{job_id}/slots", response_model=SlotResponse)
def create_interview_slot(
    job_id: str,
    slot_in: SlotCreate,
    current_user: User = Depends(require_recruiter),
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.id == job_id, Job.recruiter_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    slot = InterviewSlot(
        recruiter_id=current_user.id,
        job_id=job_id,
        start_time=slot_in.start_time,
        end_time=slot_in.end_time,
        status="available"
    )
    db.add(slot)
    db.commit()
    db.refresh(slot)
    return slot

@router.get("/jobs/{job_id}/slots", response_model=List[SlotResponse])
def list_interview_slots(
    job_id: str,
    current_user: User = Depends(require_recruiter),
    db: Session = Depends(get_db)
):
    return db.query(InterviewSlot).filter(InterviewSlot.job_id == job_id, InterviewSlot.recruiter_id == current_user.id).all()

# --- Export Endpoints ---
@router.get("/jobs/{job_id}/export/csv")
def export_csv(
    job_id: str,
    current_user: User = Depends(require_recruiter),
    db: Session = Depends(get_db)
):
    rankings = get_job_rankings(job_id=job_id, current_user=current_user, db=db)
    csv_data = generate_csv_export([r.model_dump() for r in rankings])
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=rankings_{job_id}.csv"}
    )

@router.get("/jobs/{job_id}/export/json")
def export_json(
    job_id: str,
    current_user: User = Depends(require_recruiter),
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.id == job_id, Job.recruiter_id == current_user.id).first()
    rankings = get_job_rankings(job_id=job_id, current_user=current_user, db=db)
    json_data = generate_json_export(
        [r.model_dump() for r in rankings],
        {"title": job.title, "company": job.company, "id": job.id} if job else {}
    )
    return Response(
        content=json_data,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=rankings_{job_id}.json"}
    )

@router.get("/jobs/{job_id}/export/pdf")
def export_pdf(
    job_id: str,
    current_user: User = Depends(require_recruiter),
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.id == job_id, Job.recruiter_id == current_user.id).first()
    job_title = job.title if job else "Job Role"
    rankings = get_job_rankings(job_id=job_id, current_user=current_user, db=db)
    pdf_bytes = generate_pdf_report(job_title, [r.model_dump() for r in rankings])
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=candidate_ranking_{job_id}.pdf"}
    )
