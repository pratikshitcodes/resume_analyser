# TalentPulse AI — Full-Stack Recruitment & Interview Platform

A production-grade, full-stack AI recruitment platform featuring **Candidate Mode** and **Recruiter Mode** powered by pluggable LLMs (Groq, OpenAI, Gemini) and FastAPI + React + TypeScript + Tailwind CSS.

---

## 🌟 Key Features

### 👤 Candidate Mode
1. **Resume Ingestion & Extraction**: Multi-format parsing (PDF via PyMuPDF/pypdf, DOCX, TXT) into strict Pydantic JSON schema (skills, experience, education, projects, certifications, hyperlinks).
2. **ATS Compatibility Analyzer**: Computes 0–100 ATS score based on keyword density, formatting, section balance, and quantifiable achievements. Highlights strengths, gaps, actionable tips, and a **"Best Project" deep-dive analysis**.
3. **Grounded AI Career Copilot (RAG)**: Interactive chat grounded strictly in candidate parsed profile data and ATS findings with cited source tags.
4. **Target Job Fit Evaluator**: Match candidate resume against target job descriptions with instant fit score and skill gap breakdown (matched vs missing skills).
5. **AI Technical Mock Interview Studio**: Generates customized Technical, Project-Specific, Behavioral, and Follow-Up questions with real-time answer scoring and final **Hiring Readiness Scorecard**.
6. **Interview Scheduling**: View open recruiter interview slots and book with 1-click.

### 🏢 Recruiter Mode
1. **Job Requisition & JD Auto-Extractor**: Publish jobs with automatic LLM extraction of required & nice-to-have skills, qualifications, and responsibilities.
2. **Asynchronous Batch Resume Screener**: Bulk upload 100+ resumes (multi-file or ZIP archive) processed asynchronously with real-time progress tracking.
3. **Candidate Prioritization Matrix**: Weighted match ranking with **Shortlist**, **Maybe**, and **Reject** classification filters.
4. **Evidence-Backed Justifications**: Deep-dive modal citing exact quotes and deliverables from candidate resumes backing up every score.
5. **Recruiter Natural Language Query (NLQ)**: Ask questions in plain English (e.g., *"Find candidates with 3+ years experience in FastAPI and Docker"*) with AI answers grounded in the applicant database.
6. **Interview Slot Management**: Create interview time slots and monitor booked candidates.
7. **1-Click Multi-Format Export Center**: Download Executive **PDF Reports** (ReportLab), structured **CSVs**, and **JSON** datasets.

---

## 🛠️ Tech Stack & Architecture

- **Backend**: FastAPI, SQLAlchemy 2.0 ORM, Pydantic v2, Python-Jose (JWT), Passlib/Bcrypt, ReportLab, PyMuPDF, python-docx
- **AI/LLM Layer**: Pluggable AI Provider architecture (`GroqProvider`, `OpenAIProvider`, `GeminiProvider`, `MockProvider`) with schema enforcement and resilient fallbacks
- **Database**: SQLite (default local zero-setup) with seamless PostgreSQL support
- **Async Workers**: In-process asynchronous task manager with live progress polling (`/tasks/{task_id}`)
- **Frontend**: React 18, TypeScript, Tailwind CSS, Lucide React, Vite

---

## 🚀 Quick Start (Local Direct Execution - No Docker Needed)

### 1. Launch Services
Run both backend and frontend with a single command:
```bash
run_all.bat
```
Or start them individually in separate terminals:

**Terminal 1 (Backend API):**
```bash
start_backend.bat
# Runs on http://127.0.0.1:8000
# OpenAPI Docs: http://127.0.0.1:8000/docs
```

**Terminal 2 (Frontend UI):**
```bash
start_frontend.bat
# Runs on http://127.0.0.1:5173
```

---

## 🧪 Running Automated Tests

Run the backend test suite:
```bash
python -m pytest tests/test_platform.py -v
```

All 4 test suites verify:
- Authentication & JWT issuance (Candidate and Recruiter roles)
- Resume parsing, structured profile extraction, and ATS scoring
- Job creation, match engine, and PDF/CSV/JSON export generation
- Candidate Grounded Chat and Mock Interview state progression
