@echo off
echo ========================================================
echo   Launching Incident Investigation Agent
echo   Public Static URL: https://verbose-deck-blunt.ngrok-free.dev
echo ========================================================
echo.

echo [1/2] Starting Unified Server on http://localhost:8000 ...
start "Incident Agent - Backend" cmd /k "cd /d %~dp0incident-investigation-agent\backend && python main.py"

timeout /t 3 /nobreak >nul

echo [2/2] Starting Permanent ngrok Tunnel ...
start "Incident Agent - Public Tunnel" cmd /k "ngrok http --url=verbose-deck-blunt.ngrok-free.dev 8000"

echo.
echo ========================================================
echo   Both Local and Public URLs are Active!
echo   Local:  http://localhost:8000
echo   Public: https://verbose-deck-blunt.ngrok-free.dev
echo ========================================================
start http://localhost:8000
