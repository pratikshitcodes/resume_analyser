import os
import shutil
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..core.config import settings
from ..auth.deps import require_candidate, get_current_user
from ..models import (
    User, Resume, ParsedProfile, ATSAnalysis, Job, 
    MatchResult, InterviewQuestionSet, MockInterviewSession, 
    InterviewSlot, ChatSession, ChatMessage
)
from ..schemas import (
    ResumeResponse, ParsedProfileSchema, ATSAnalysisResponse, 
    MatchResultResponse, QuestionSetResponse, MockInterviewStartRequest,
    MockInterviewStepRequest, MockInterviewStepResponse, 
    MockInterviewSessionResponse, ChatRequest, ChatResponse, SlotResponse
)
from ..services.parser import extract_text_from_file, parse_resume_content, parse_job_description_content
from ..services.ats import analyze_resume_ats
from ..services.matcher import match_candidate_to_job
from ..services.interview import generate_questions, evaluate_interview_answer, finalize_mock_interview
from ..services.ai.factory import get_ai_provider

router = APIRouter(prefix="/candidate", tags=["Candidate Mode"])

@router.post("/upload-resume", response_model=ResumeResponse)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(require_candidate),
    db: Session = Depends(get_db)
):
    # Save file
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in [".pdf", ".docx", ".txt", ".md"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format. Please upload PDF, DOCX, or TXT."
        )

    saved_filename = f"{current_user.id}_{int(datetime.now().timestamp())}_{file.filename}"
    file_path = settings.UPLOAD_DIR / saved_filename
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract text & links
    try:
        raw_text, links = extract_text_from_file(file_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {e}")

    # Structured Profile Extraction
    profile_data = parse_resume_content(raw_text, links)
    
    # Compute ATS Analysis
    ats_data = analyze_resume_ats(profile_data, raw_text)

    # Save to Database
    resume = Resume(
        candidate_id=current_user.id,
        file_url=str(file_path),
        file_name=file.filename,
        raw_text=raw_text,
        parsed_json=profile_data
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)

    # Save Profile
    parsed_profile = ParsedProfile(
        resume_id=resume.id,
        name=profile_data.get("name") or current_user.full_name,
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

    # Save ATS Analysis
    ats_analysis = ATSAnalysis(
        resume_id=resume.id,
        ats_score=ats_data.get("ats_score", 80),
        strengths=ats_data.get("strengths", []),
        weaknesses=ats_data.get("weaknesses", []),
        suggestions=ats_data.get("suggestions", []),
        best_project_analysis=ats_data.get("best_project_analysis", "")
    )
    db.add(ats_analysis)
    db.commit()
    db.refresh(resume)

    return ResumeResponse(
        id=resume.id,
        candidate_id=resume.candidate_id,
        file_name=resume.file_name,
        file_url=resume.file_url,
        uploaded_at=resume.uploaded_at,
        profile=ParsedProfileSchema(**profile_data),
        ats_analysis=ATSAnalysisResponse(**ats_data)
    )

@router.get("/resume/latest", response_model=Optional[ResumeResponse])
def get_latest_resume(
    current_user: User = Depends(require_candidate),
    db: Session = Depends(get_db)
):
    resume = db.query(Resume).filter(Resume.candidate_id == current_user.id).order_by(Resume.uploaded_at.desc()).first()
    if not resume:
        return None
    
    profile_schema = None
    if resume.profile:
        profile_schema = ParsedProfileSchema(
            name=resume.profile.name,
            contact_info=resume.profile.contact_info or {},
            skills=resume.profile.skills or [],
            experience=resume.profile.experience or [],
            education=resume.profile.education or [],
            projects=resume.profile.projects or [],
            certifications=resume.profile.certifications or [],
            achievements=resume.profile.achievements or [],
            total_experience_years=resume.profile.total_experience_years or 0.0
        )

    ats_schema = None
    if resume.ats_analysis:
        ats_schema = ATSAnalysisResponse(
            ats_score=resume.ats_analysis.ats_score,
            strengths=resume.ats_analysis.strengths or [],
            weaknesses=resume.ats_analysis.weaknesses or [],
            suggestions=resume.ats_analysis.suggestions or [],
            best_project_analysis=resume.ats_analysis.best_project_analysis
        )

    return ResumeResponse(
        id=resume.id,
        candidate_id=resume.candidate_id,
        file_name=resume.file_name,
        file_url=resume.file_url,
        uploaded_at=resume.uploaded_at,
        profile=profile_schema,
        ats_analysis=ats_schema
    )

@router.post("/chat", response_model=ChatResponse)
def candidate_chat(
    req: ChatRequest,
    current_user: User = Depends(require_candidate),
    db: Session = Depends(get_db)
):
    # Retrieve candidate latest resume & profile
    resume = None
    if req.linked_resume_id:
        resume = db.query(Resume).filter(Resume.id == req.linked_resume_id, Resume.candidate_id == current_user.id).first()
    if not resume:
        resume = db.query(Resume).filter(Resume.candidate_id == current_user.id).order_by(Resume.uploaded_at.desc()).first()
    
    profile_data = resume.parsed_json if resume and resume.parsed_json else {}
    ats_data = {
        "ats_score": resume.ats_analysis.ats_score if resume and resume.ats_analysis else 80,
        "strengths": resume.ats_analysis.strengths if resume and resume.ats_analysis else [],
        "weaknesses": resume.ats_analysis.weaknesses if resume and resume.ats_analysis else [],
        "best_project": resume.ats_analysis.best_project_analysis if resume and resume.ats_analysis else ""
    }

    # Find or create session
    session = None
    if req.session_id:
        session = db.query(ChatSession).filter(ChatSession.id == req.session_id, ChatSession.user_id == current_user.id).first()
    if not session:
        session = ChatSession(
            user_id=current_user.id,
            role_context="candidate",
            linked_resume_id=resume.id if resume else None
        )
        db.add(session)
        db.commit()
        db.refresh(session)

    # Build history
    history = []
    for msg in session.messages[-6:]:
        history.append({"role": msg.role, "content": msg.content})

    ai = get_ai_provider()
    ai_result = ai.chat_candidate(req.message, profile_data, ats_data, history)

    # Save user message & assistant message
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

@router.post("/evaluate-jd", response_model=MatchResultResponse)
def evaluate_jd(
    job_id: Optional[str] = Form(None),
    jd_text: Optional[str] = Form(None),
    current_user: User = Depends(require_candidate),
    db: Session = Depends(get_db)
):
    resume = db.query(Resume).filter(Resume.candidate_id == current_user.id).order_by(Resume.uploaded_at.desc()).first()
    if not resume:
        raise HTTPException(status_code=400, detail="Please upload your resume first.")

    job_data = {}
    if job_id:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found.")
        job_data = {
            "title": job.title,
            "company": job.company,
            "required_skills": job.required_skills,
            "nice_to_have_skills": job.nice_to_have_skills,
            "experience_required": job.experience_required,
            "description": job.description
        }
    elif jd_text:
        job_data = parse_job_description_content(jd_text)
    else:
        raise HTTPException(status_code=400, detail="Must provide either job_id or jd_text.")

    profile_data = resume.parsed_json or {}
    match_data = match_candidate_to_job(profile_data, job_data)

    # If linked to actual job, save match result
    match_result_id = "eval_" + str(datetime.now().timestamp())
    if job_id:
        existing = db.query(MatchResult).filter(
            MatchResult.job_id == job_id,
            MatchResult.candidate_id == current_user.id,
            MatchResult.resume_id == resume.id
        ).first()
        if existing:
            existing.match_score = match_data.get("match_score", 70)
            existing.matched_skills = match_data.get("matched_skills", [])
            existing.missing_skills = match_data.get("missing_skills", [])
            existing.classification = match_data.get("classification", "maybe")
            existing.ranking_explanation = match_data.get("ranking_explanation", "")
            existing.evidence_quotes = match_data.get("evidence_quotes", [])
            db.commit()
            db.refresh(existing)
            match_res = existing
        else:
            match_res = MatchResult(
                job_id=job_id,
                candidate_id=current_user.id,
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
            db.refresh(match_res)
        match_result_id = match_res.id

    return MatchResultResponse(
        id=match_result_id,
        job_id=job_id or "custom_jd",
        candidate_id=current_user.id,
        resume_id=resume.id,
        match_score=match_data.get("match_score", 70),
        matched_skills=match_data.get("matched_skills", []),
        missing_skills=match_data.get("missing_skills", []),
        classification=match_data.get("classification", "maybe"),
        ranking_explanation=match_data.get("ranking_explanation", ""),
        evidence_quotes=match_data.get("evidence_quotes", []),
        created_at=datetime.now(timezone.utc)
    )

@router.get("/questions", response_model=QuestionSetResponse)
def get_custom_interview_questions(
    job_id: Optional[str] = None,
    current_user: User = Depends(require_candidate),
    db: Session = Depends(get_db)
):
    resume = db.query(Resume).filter(Resume.candidate_id == current_user.id).order_by(Resume.uploaded_at.desc()).first()
    if not resume:
        raise HTTPException(status_code=400, detail="Please upload your resume first.")

    job_data = {}
    if job_id:
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            job_data = {
                "title": job.title,
                "company": job.company,
                "required_skills": job.required_skills,
                "description": job.description
            }

    profile_data = resume.parsed_json or {}
    questions = generate_questions(profile_data, job_data)
    
    return QuestionSetResponse(
        technical=questions.get("technical", []),
        project=questions.get("project", []),
        behavioral=questions.get("behavioral", []),
        follow_up=questions.get("follow_up", [])
    )

@router.post("/mock-interview/start", response_model=MockInterviewSessionResponse)
def start_mock_interview(
    req: MockInterviewStartRequest,
    current_user: User = Depends(require_candidate),
    db: Session = Depends(get_db)
):
    resume = db.query(Resume).filter(Resume.candidate_id == current_user.id).order_by(Resume.uploaded_at.desc()).first()
    if not resume:
        raise HTTPException(status_code=400, detail="Please upload your resume first.")

    job_data = {}
    if req.job_id:
        job = db.query(Job).filter(Job.id == req.job_id).first()
        if job:
            job_data = {"title": job.title, "company": job.company, "required_skills": job.required_skills}

    profile_data = resume.parsed_json or {}
    q_set = generate_questions(profile_data, job_data)
    
    # Pick a balanced list of questions
    all_questions = []
    if q_set.get("technical"): all_questions.append(q_set["technical"][0])
    if q_set.get("project"): all_questions.append(q_set["project"][0])
    if q_set.get("behavioral"): all_questions.append(q_set["behavioral"][0])
    if q_set.get("follow_up"): all_questions.append(q_set["follow_up"][0])
    
    if not all_questions:
        all_questions = [
            "Can you tell me about your background and a technically challenging project you built?",
            "How do you design scalable backend systems and optimize database queries?",
            "Describe a difficult technical bug you solved and what you learned."
        ]

    session = MockInterviewSession(
        candidate_id=current_user.id,
        job_id=req.job_id,
        resume_id=resume.id,
        questions=all_questions,
        transcript=[],
        scores={},
        readiness_score=0,
        status="in_progress"
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return session

@router.post("/mock-interview/step", response_model=MockInterviewStepResponse)
def step_mock_interview(
    req: MockInterviewStepRequest,
    current_user: User = Depends(require_candidate),
    db: Session = Depends(get_db)
):
    session = db.query(MockInterviewSession).filter(
        MockInterviewSession.id == req.session_id,
        MockInterviewSession.candidate_id == current_user.id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Mock interview session not found.")

    questions = session.questions or []
    if req.question_index >= len(questions):
        raise HTTPException(status_code=400, detail="Invalid question index.")

    current_question = questions[req.question_index]
    
    # Evaluate step
    step_eval = evaluate_interview_answer(current_question, req.user_answer, {})

    # Update transcript
    transcript = list(session.transcript or [])
    transcript.append({
        "question": current_question,
        "answer": req.user_answer,
        "feedback": step_eval.get("feedback", ""),
        "score": step_eval.get("score", 80),
        "strengths": step_eval.get("strengths", []),
        "improvements": step_eval.get("improvements", [])
    })
    session.transcript = transcript

    # Check if more questions
    next_idx = req.question_index + 1
    is_completed = next_idx >= len(questions)
    next_question = questions[next_idx] if not is_completed else None

    if is_completed:
        # Finalize
        resume = db.query(Resume).filter(Resume.id == session.resume_id).first()
        profile_data = resume.parsed_json if resume else {}
        final_eval = finalize_mock_interview(transcript, profile_data)
        
        session.scores = final_eval.get("scores", {"technical": 85, "communication": 85, "projects": 80, "problem_solving": 85})
        session.readiness_score = final_eval.get("readiness_score", 85)
        session.feedback = final_eval.get("feedback", "Completed mock interview with strong results.")
        session.status = "completed"
        session.completed_at = datetime.now(timezone.utc)

    db.commit()

    return MockInterviewStepResponse(
        session_id=session.id,
        question_index=req.question_index,
        next_question=next_question,
        is_completed=is_completed,
        step_feedback=step_eval.get("feedback")
    )

@router.get("/mock-interview/{session_id}", response_model=MockInterviewSessionResponse)
def get_mock_interview_session(
    session_id: str,
    current_user: User = Depends(require_candidate),
    db: Session = Depends(get_db)
):
    session = db.query(MockInterviewSession).filter(
        MockInterviewSession.id == session_id,
        MockInterviewSession.candidate_id == current_user.id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Mock interview session not found.")
    return session

@router.get("/available-slots", response_model=List[SlotResponse])
def get_available_slots(
    job_id: Optional[str] = None,
    current_user: User = Depends(require_candidate),
    db: Session = Depends(get_db)
):
    query = db.query(InterviewSlot).filter(InterviewSlot.status == "available")
    if job_id:
        query = query.filter(InterviewSlot.job_id == job_id)
    return query.all()

@router.post("/book-slot/{slot_id}", response_model=SlotResponse)
def book_slot(
    slot_id: str,
    current_user: User = Depends(require_candidate),
    db: Session = Depends(get_db)
):
    slot = db.query(InterviewSlot).filter(InterviewSlot.id == slot_id).first()
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found.")
    if slot.status != "available":
        raise HTTPException(status_code=400, detail="This interview slot is already booked.")

    slot.status = "booked"
    slot.candidate_id = current_user.id
    slot.booked_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(slot)
    return slot
