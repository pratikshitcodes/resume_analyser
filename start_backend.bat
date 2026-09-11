@echo off
echo ========================================================
echo Starting AI Recruitment Platform - Backend API (FastAPI)
echo ========================================================
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
