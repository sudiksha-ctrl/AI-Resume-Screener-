@echo off
echo ===================================================
echo  Starting AI Resume Screener (Backend + Frontend)
echo ===================================================
start "AI Resume Screener Backend" cmd /c "%~dp0run_backend.bat"
timeout /t 3 /nobreak >nul
start "AI Resume Screener Frontend" cmd /c "%~dp0run_frontend.bat"
echo Services launched!
echo Backend:  http://127.0.0.1:8000
echo Frontend: http://localhost:5173
pause
