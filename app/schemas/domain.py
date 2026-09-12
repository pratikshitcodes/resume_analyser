from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

# --- Auth Schemas ---
class UserCreate(BaseModel):
    email: str
    password: str = Field(min_length=6)
    full_name: Optional[str] = None
    role: str = Field(default="candidate", pattern="^(candidate|recruiter|admin)$")

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: str
    user_id: str
    email: str
    full_name: Optional[str] = None

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    email: str
    full_name: Optional[str] = None
    role: str
    created_at: datetime

# --- Resume & Profile Schemas ---
class ExperienceItem(BaseModel):
    company: str
    role: str
    duration: Optional[str] = None
    description: Optional[str] = None

class EducationItem(BaseModel):
    degree: str
    university: Optional[str] = None
    cgpa: Optional[float] = None
    year: Optional[str] = None

class ProjectItem(BaseModel):
    name: str
    description: Optional[str] = None
    technologies: List[str] = Field(default_factory=list)
    link: Optional[str] = None
    impact: Optional[str] = None

class ParsedProfileSchema(BaseModel):
    name: Optional[str] = None
    contact_info: Dict[str, Any] = Field(default_factory=dict)
    skills: List[str] = Field(default_factory=list)
    experience: List[ExperienceItem] = Field(default_factory=list)
    education: List[EducationItem] = Field(default_factory=list)
    projects: List[ProjectItem] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    achievements: List[str] = Field(default_factory=list)
    total_experience_years: float = 0.0

class ATSAnalysisResponse(BaseModel):
    ats_score: int = Field(ge=0, le=100)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    best_project_analysis: Optional[str] = None

class ResumeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    candidate_id: str
    file_name: Optional[str] = None
    file_url: Optional[str] = None
    uploaded_at: datetime
    profile: Optional[ParsedProfileSchema] = None
    ats_analysis: Optional[ATSAnalysisResponse] = None

# --- Job & Matching Schemas ---
class JobCreate(BaseModel):
    title: str
    company: Optional[str] = "TechCorp"
    description: str
    experience_required: Optional[str] = "2+ years"

class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    recruiter_id: str
    title: str
    company: str
    description: str
    required_skills: List[str] = Field(default_factory=list)
    nice_to_have_skills: List[str] = Field(default_factory=list)
    qualifications: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    experience_required: Optional[str] = None
    created_at: datetime

class MatchResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    job_id: str
    candidate_id: str
    resume_id: str
    match_score: int
    matched_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    classification: str # shortlist, maybe, reject
    ranking_explanation: Optional[str] = None
    evidence_quotes: List[str] = Field(default_factory=list)
    created_at: datetime

class RankedCandidateResponse(BaseModel):
    rank: int
    match_id: str
    candidate_id: str
    candidate_name: str
    candidate_email: Optional[str] = None
    resume_id: str
    match_score: int
    classification: str
    matched_skills: List[str]
    missing_skills: List[str]
    total_experience_years: float
    ranking_explanation: str
    evidence_quotes: List[str]

# --- Interview Schemas ---
class QuestionSetResponse(BaseModel):
    technical: List[str] = Field(default_factory=list)
    project: List[str] = Field(default_factory=list)
    behavioral: List[str] = Field(default_factory=list)
    follow_up: List[str] = Field(default_factory=list)

class MockInterviewStartRequest(BaseModel):
    job_id: Optional[str] = None
    resume_id: Optional[str] = None
    num_questions: Optional[int] = 4

class MockInterviewStepRequest(BaseModel):
    session_id: str
    question_index: int
    user_answer: str

class MockInterviewStepResponse(BaseModel):
    session_id: str
    question_index: int
    next_question: Optional[str] = None
    is_completed: bool
    step_feedback: Optional[str] = None

class MockInterviewSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    candidate_id: str
    job_id: Optional[str] = None
    questions: List[str] = Field(default_factory=list)
    transcript: List[Dict[str, Any]] = Field(default_factory=list)
    scores: Dict[str, int] = Field(default_factory=dict)
    readiness_score: int = 0
    feedback: Optional[str] = None
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None

# --- Chat Schemas ---
class ChatMessageSchema(BaseModel):
    id: Optional[str] = None
    role: str
    content: str
    context_sources: List[str] = Field(default_factory=list)
    created_at: Optional[datetime] = None

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    linked_resume_id: Optional[str] = None
    linked_job_id: Optional[str] = None

class ChatResponse(BaseModel):
    session_id: str
    reply: str
    context_sources: List[str] = Field(default_factory=list)

class ChatSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    user_id: str
    role_context: str
    linked_resume_id: Optional[str] = None
    linked_job_id: Optional[str] = None
    messages: List[ChatMessageSchema] = Field(default_factory=list)

# --- Interview Slot Schemas ---
class SlotCreate(BaseModel):
    job_id: str
    start_time: datetime
    end_time: datetime

class SlotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    recruiter_id: str
    job_id: str
    candidate_id: Optional[str] = None
    start_time: datetime
    end_time: datetime
    status: str
    booked_at: Optional[datetime] = None

# --- Background Task Schemas ---
class TaskStatusResponse(BaseModel):
    task_id: str
    status: str # pending, processing, completed, failed
    progress: int = 0 # 0 - 100
    message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
