import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Text, JSON, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from ..core.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(String(50), nullable=False, default="candidate")  # candidate, recruiter, admin
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    resumes = relationship("Resume", back_populates="candidate", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="recruiter", cascade="all, delete-orphan")
    match_results = relationship("MatchResult", back_populates="candidate", cascade="all, delete-orphan")
    mock_interviews = relationship("MockInterviewSession", back_populates="candidate", cascade="all, delete-orphan")
    booked_slots = relationship("InterviewSlot", back_populates="candidate", foreign_keys="InterviewSlot.candidate_id")
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    candidate_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    file_url = Column(String(500), nullable=True)
    file_name = Column(String(255), nullable=True)
    raw_text = Column(Text, nullable=True)
    parsed_json = Column(JSON, nullable=True)
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    candidate = relationship("User", back_populates="resumes")
    profile = relationship("ParsedProfile", back_populates="resume", uselist=False, cascade="all, delete-orphan")
    ats_analysis = relationship("ATSAnalysis", back_populates="resume", uselist=False, cascade="all, delete-orphan")
    match_results = relationship("MatchResult", back_populates="resume", cascade="all, delete-orphan")

class ParsedProfile(Base):
    __tablename__ = "parsed_profiles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    resume_id = Column(String(36), ForeignKey("resumes.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    name = Column(String(255), nullable=True)
    contact_info = Column(JSON, default=dict)  # email, phone, linkedin, github, leetcode, etc.
    skills = Column(JSON, default=list)        # list of skill strings
    experience = Column(JSON, default=list)    # list of experience dicts
    education = Column(JSON, default=list)     # list of education dicts
    projects = Column(JSON, default=list)       # list of project dicts
    certifications = Column(JSON, default=list)# list of certification strings/dicts
    achievements = Column(JSON, default=list)  # list of achievements
    total_experience_years = Column(Float, default=0.0)

    resume = relationship("Resume", back_populates="profile")

class ATSAnalysis(Base):
    __tablename__ = "ats_analyses"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    resume_id = Column(String(36), ForeignKey("resumes.id", ondelete="CASCADE"), unique=True, nullable=False)
    ats_score = Column(Integer, default=0) # 0 - 100
    strengths = Column(JSON, default=list)
    weaknesses = Column(JSON, default=list)
    suggestions = Column(JSON, default=list)
    best_project_analysis = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    resume = relationship("Resume", back_populates="ats_analysis")

class Job(Base):
    __tablename__ = "jobs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    recruiter_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    company = Column(String(255), default="Company")
    description = Column(Text, nullable=False)
    jd_file_url = Column(String(500), nullable=True)
    
    required_skills = Column(JSON, default=list)
    nice_to_have_skills = Column(JSON, default=list)
    qualifications = Column(JSON, default=list)
    responsibilities = Column(JSON, default=list)
    experience_required = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    recruiter = relationship("User", back_populates="jobs")
    match_results = relationship("MatchResult", back_populates="job", cascade="all, delete-orphan")
    interview_slots = relationship("InterviewSlot", back_populates="job", cascade="all, delete-orphan")

class MatchResult(Base):
    __tablename__ = "match_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    job_id = Column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    candidate_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    resume_id = Column(String(36), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    
    match_score = Column(Integer, default=0) # 0 - 100
    matched_skills = Column(JSON, default=list)
    missing_skills = Column(JSON, default=list)
    classification = Column(String(50), default="maybe") # shortlist, maybe, reject
    ranking_explanation = Column(Text, nullable=True)
    evidence_quotes = Column(JSON, default=list) # specific excerpts backing the score
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    job = relationship("Job", back_populates="match_results")
    candidate = relationship("User", back_populates="match_results")
    resume = relationship("Resume", back_populates="match_results")

class InterviewQuestionSet(Base):
    __tablename__ = "interview_question_sets"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    candidate_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=True)
    resume_id = Column(String(36), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=True)
    
    technical = Column(JSON, default=list)
    project = Column(JSON, default=list)
    behavioral = Column(JSON, default=list)
    follow_up = Column(JSON, default=list)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class MockInterviewSession(Base):
    __tablename__ = "mock_interview_sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    candidate_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(String(36), ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True)
    resume_id = Column(String(36), ForeignKey("resumes.id", ondelete="SET NULL"), nullable=True)
    
    questions = Column(JSON, default=list)
    transcript = Column(JSON, default=list) # [{"question": "...", "answer": "...", "feedback": "...", "score": 85}]
    scores = Column(JSON, default=dict)     # {"technical": 80, "communication": 85, "projects": 75, "problem_solving": 90}
    readiness_score = Column(Integer, default=0) # 0 - 100
    feedback = Column(Text, nullable=True)
    status = Column(String(50), default="in_progress") # in_progress, completed
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)

    candidate = relationship("User", back_populates="mock_interviews")

class InterviewSlot(Base):
    __tablename__ = "interview_slots"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    recruiter_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    candidate_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(String(50), default="available") # available, booked, cancelled
    booked_at = Column(DateTime, nullable=True)

    job = relationship("Job", back_populates="interview_slots")
    candidate = relationship("User", back_populates="booked_slots", foreign_keys=[candidate_id])

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role_context = Column(String(50), default="candidate") # candidate | recruiter
    linked_resume_id = Column(String(36), nullable=True)
    linked_job_id = Column(String(36), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan", order_by="ChatMessage.created_at")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(50), nullable=False) # user, assistant, system
    content = Column(Text, nullable=False)
    context_sources = Column(JSON, default=list) # quotes/citations used from resume or candidates
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    session = relationship("ChatSession", back_populates="messages")
