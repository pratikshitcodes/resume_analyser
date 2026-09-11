import os
from pathlib import Path
from typing import Tuple, List, Dict, Any
from docx import Document
from pypdf import PdfReader
import pymupdf # PyMuPDF
from .ai.factory import get_ai_provider
from ..schemas.models import ResumeModel, JobDescriptionModel

def extract_text_from_file(file_path: str | Path) -> Tuple[str, List[str]]:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    suffix = path.suffix.lower()
    text = ""
    links: List[str] = []

    if suffix == ".pdf":
        try:
            doc = pymupdf.open(str(path))
            for page in doc:
                text += page.get_text() + "\n\n"
                for link in page.get_links():
                    if "uri" in link:
                        links.append(link["uri"])
            doc.close()
        except Exception:
            pass

        if not text.strip():
            try:
                reader = PdfReader(str(path))
                for page in reader.pages:
                    text += (page.extract_text() or "") + "\n\n"
            except Exception as e:
                raise ValueError(f"Could not extract text from PDF: {e}")

    elif suffix == ".docx":
        try:
            doc = Document(str(path))
            paras = [p.text for p in doc.paragraphs if p.text.strip()]
            text = "\n".join(paras)
            for rel in doc.part.rels.values():
                if "hyperlink" in rel.reltype:
                    links.append(rel.target_ref)
        except Exception as e:
            raise ValueError(f"Could not extract text from DOCX: {e}")

    elif suffix in [".txt", ".md"]:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
    else:
        raise ValueError(f"Unsupported file format: {suffix}. Supported formats: .pdf, .docx, .txt")

    return text.strip(), list(set(links))

def parse_resume_content(raw_text: str, links: List[str] = None) -> Dict[str, Any]:
    ai = get_ai_provider()
    profile = ai.extract_profile(raw_text)
    
    # Merge extracted hyperlink URLs into contact_info / project links if available
    if links and "contact_info" in profile:
        for link in links:
            if "linkedin.com" in link and not profile["contact_info"].get("linkedin"):
                profile["contact_info"]["linkedin"] = link
            elif "github.com" in link and not profile["contact_info"].get("github"):
                profile["contact_info"]["github"] = link
            elif "leetcode.com" in link and not profile["contact_info"].get("leetcode"):
                profile["contact_info"]["leetcode"] = link

    return profile

def parse_job_description_content(raw_text: str) -> Dict[str, Any]:
    ai = get_ai_provider()
    return ai.parse_job_description(raw_text)

# Compatibility wrappers for legacy code
def parse_resume(path: str):
    raw_text, links = extract_text_from_file(path)
    data = parse_resume_content(raw_text, links)
    
    # Map to ResumeModel
    exp_objs = []
    for e in data.get("experience", []):
        exp_objs.append({"company": e.get("company", "Company"), "role": e.get("role", "Role"), "duration": e.get("duration"), "description": e.get("description")})
    
    edu_objs = []
    for ed in data.get("education", []):
        edu_objs.append({"degree": ed.get("degree", "Degree"), "university": ed.get("university"), "cgpa": ed.get("cgpa")})

    proj_objs = []
    for pr in data.get("projects", []):
        proj_objs.append({"name": pr.get("name", "Project"), "description": pr.get("description"), "technologies": pr.get("technologies", []), "link": pr.get("link")})

    contact = data.get("contact_info", {})
    return ResumeModel(
        name=data.get("name", "Candidate"),
        email=contact.get("email"),
        linkedin=contact.get("linkedin"),
        leetcode=contact.get("leetcode"),
        github=contact.get("github"),
        skills=data.get("skills", []),
        education=edu_objs,
        experience=exp_objs,
        projects=proj_objs,
        achievements=data.get("achievements", [])
    ), links

def parse_jd(path: str):
    raw_text, links = extract_text_from_file(path)
    data = parse_job_description_content(raw_text)
    return JobDescriptionModel(
        company=data.get("company", "Company"),
        role=data.get("title", "Role"),
        required_skills=data.get("required_skills", ["Python"]),
        preferred_skills=data.get("nice_to_have_skills", []),
        qualifications=data.get("qualifications", []),
        responsibilities=data.get("responsibilities", []),
        experience_required=data.get("experience_required")
    ), links
