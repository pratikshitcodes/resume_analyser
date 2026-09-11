import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import Base, engine, SessionLocal
from app.core.security import create_access_token
from app.models import User, Job, Resume, MatchResult

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_auth_registration_and_login():
    # Register Candidate
    reg_cand = client.post("/api/v1/auth/register", json={
        "email": "testcandidate@example.com",
        "password": "securepassword123",
        "full_name": "Alice Smith",
        "role": "candidate"
    })
    assert reg_cand.status_code in [200, 400] # 400 if already exists

    # Login Candidate
    login_cand = client.post("/api/v1/auth/login", json={
        "email": "testcandidate@example.com",
        "password": "securepassword123"
    })
    assert login_cand.status_code == 200
    cand_data = login_cand.json()
    assert "access_token" in cand_data
    assert cand_data["role"] == "candidate"

    # Register Recruiter
    reg_rec = client.post("/api/v1/auth/register", json={
        "email": "testrecruiter@example.com",
        "password": "securepassword123",
        "full_name": "Bob Recruiter",
        "role": "recruiter"
    })
    assert reg_rec.status_code in [200, 400]

    # Login Recruiter
    login_rec = client.post("/api/v1/auth/login", json={
        "email": "testrecruiter@example.com",
        "password": "securepassword123"
    })
    assert login_rec.status_code == 200
    rec_data = login_rec.json()
    assert rec_data["role"] == "recruiter"

def test_recruiter_create_job_and_export():
    # Recruiter login
    login_rec = client.post("/api/v1/auth/login", json={
        "email": "testrecruiter@example.com",
        "password": "securepassword123"
    })
    rec_token = login_rec.json()["access_token"]
    headers = {"Authorization": f"Bearer {rec_token}"}

    # Create Job
    job_res = client.post("/api/v1/recruiter/jobs", json={
        "title": "Senior Python Engineer",
        "company": "NextGen AI",
        "description": "Looking for a Senior Python Engineer with FastAPI, PostgreSQL, and Docker experience.",
        "experience_required": "3+ years"
    }, headers=headers)
    assert job_res.status_code == 200
    job = job_res.json()
    assert job["title"] == "Senior Python Engineer"
    job_id = job["id"]

    # Export CSV & JSON & PDF (empty or with items)
    csv_res = client.get(f"/api/v1/recruiter/jobs/{job_id}/export/csv", headers=headers)
    assert csv_res.status_code == 200
    assert "text/csv" in csv_res.headers["content-type"]

    json_res = client.get(f"/api/v1/recruiter/jobs/{job_id}/export/json", headers=headers)
    assert json_res.status_code == 200

    pdf_res = client.get(f"/api/v1/recruiter/jobs/{job_id}/export/pdf", headers=headers)
    assert pdf_res.status_code == 200
    assert "application/pdf" in pdf_res.headers["content-type"]

def test_candidate_resume_and_mock_interview():
    # Candidate login
    login_cand = client.post("/api/v1/auth/login", json={
        "email": "testcandidate@example.com",
        "password": "securepassword123"
    })
    cand_token = login_cand.json()["access_token"]
    headers = {"Authorization": f"Bearer {cand_token}"}

    # Upload sample text resume
    sample_resume = b"""Alice Smith
alice@example.com | +1 (555) 019-2834 | linkedin.com/in/alicesmith | github.com/alicesmith

SUMMARY:
Results-driven Backend Engineer with 3 years experience building scalable web services with Python, FastAPI, and PostgreSQL.

SKILLS:
Python, FastAPI, PostgreSQL, Docker, Redis, Git, React, REST APIs

EXPERIENCE:
Software Engineer | Acme Tech (2023 - Present)
- Architected and built high-performance microservices in FastAPI reducing response times by 40%.
- Designed database schemas and managed migrations with SQLAlchemy and PostgreSQL.

PROJECTS:
AI Resume Evaluator
- Built an automated candidate screening platform utilizing LLMs and full-stack React UI.
"""

    upload_res = client.post(
        "/api/v1/candidate/upload-resume",
        files={"file": ("alice_resume.txt", sample_resume, "text/plain")},
        headers=headers
    )
    assert upload_res.status_code == 200
    res_data = upload_res.json()
    assert res_data["profile"]["name"] is not None
    assert "Python" in res_data["profile"]["skills"]
    assert res_data["ats_analysis"]["ats_score"] > 0

    # Test Candidate Grounded Chat
    chat_res = client.post(
        "/api/v1/candidate/chat",
        json={"message": "What is my top project and what are my strengths?"},
        headers=headers
    )
    assert chat_res.status_code == 200
    chat_data = chat_res.json()
    assert "reply" in chat_data
    assert len(chat_data["context_sources"]) > 0

    # Test Mock Interview Start & Step
    start_res = client.post(
        "/api/v1/candidate/mock-interview/start",
        json={"num_questions": 3},
        headers=headers
    )
    assert start_res.status_code == 200
    session_id = start_res.json()["id"]

    step_res = client.post(
        "/api/v1/candidate/mock-interview/step",
        json={
            "session_id": session_id,
            "question_index": 0,
            "user_answer": "I use connection pooling with SQLAlchemy, add appropriate indexes to filtered columns, and use async query execution to avoid blocking."
        },
        headers=headers
    )
    assert step_res.status_code == 200
    assert "step_feedback" in step_res.json()
