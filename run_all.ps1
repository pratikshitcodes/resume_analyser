# PowerShell runner to launch Backend and Frontend in separate windows
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "Launching TalentPulse AI Recruitment Platform..." -ForegroundColor Green
Write-Host "Backend API:  http://127.0.0.1:8000" -ForegroundColor Yellow
Write-Host "Frontend UI:  http://127.0.0.1:5173" -ForegroundColor Yellow
Write-Host "API Docs:     http://127.0.0.1:8000/docs" -ForegroundColor Yellow
Write-Host "========================================================" -ForegroundColor Cyan

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Start Backend in a new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptDir'; python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

# Start Frontend in a new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptDir\frontend'; npm run dev -- --host 127.0.0.1 --port 5173"

Write-Host "Backend and Frontend launched in dedicated terminal windows!" -ForegroundColor Green
