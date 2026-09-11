@echo off
echo ========================================================
echo Launching AI Recruitment & Mock Interview Platform
echo Backend: http://127.0.0.1:8000
echo Frontend: http://127.0.0.1:5173
echo API Docs: http://127.0.0.1:8000/docs
echo ========================================================
start "TalentPulse AI Backend" cmd /k "start_backend.bat"
start "TalentPulse AI Frontend" cmd /k "start_frontend.bat"
echo Services started in separate terminal windows!
