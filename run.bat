@echo off
echo ========================================================
echo   Launching Incident Investigation Agent
echo ========================================================
echo.
cd /d "%~dp0incident-investigation-agent\backend"
echo [1/2] Starting unified server on http://localhost:8000 ...
start http://localhost:8000
python main.py
