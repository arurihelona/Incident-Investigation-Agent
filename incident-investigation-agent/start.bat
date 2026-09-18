@echo off
echo ===================================================
echo Starting Incident Investigation Agent Prototype
echo ===================================================

start "Incident Agent - Backend (FastAPI)" cmd /k "cd /d %~dp0backend && python main.py"
start "Incident Agent - Frontend (Vite)" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo Both Backend (http://localhost:8000) and Frontend (http://localhost:5173) are launching!
echo Open http://localhost:5173 in your browser.
