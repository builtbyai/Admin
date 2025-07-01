@echo off
echo Starting SRLA Services...
echo ========================
echo.

REM Start Backend
echo Starting Backend API...
start cmd /k "cd srla_webstack && venv\Scripts\activate && python api/server.py"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start Web Frontend
echo Starting Web Frontend...
start cmd /k "cd srla_webstack && python -m http.server 3000"

REM Start Mobile App
echo Starting Mobile App...
start cmd /k "cd srla-mobile && npm start"

echo.
echo All services starting...
echo.
echo Backend API: http://localhost:8000
echo Web Portal: http://localhost:3000
echo Mobile App: Check Expo Dev Tools in browser
echo.
pause
