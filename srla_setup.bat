@echo off
echo SRLA Project Setup Script
echo =========================
echo.

REM Check if Node.js is installed
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed!
    echo Please download and install Node.js from https://nodejs.org/
    echo.
    pause
    exit /b 1
)

REM Check if Python is installed
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed!
    echo Please download and install Python from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo Found Node.js and Python installations
echo.

REM Backend setup
echo Setting up Backend...
cd srla_webstack
if not exist venv (
    echo Creating Python virtual environment...
    python -m venv venv
)

echo Installing Python dependencies...
call venv\Scripts\activate
pip install -r requirements.txt

if not exist .env (
    echo Creating .env file...
    copy .env.example .env
    echo Please edit srla_webstack\.env with your API keys
)

echo.
echo Backend setup complete!
echo.

REM Mobile app setup
echo Setting up Mobile App...
cd ..\srla-mobile

echo Installing npm dependencies...
call npm install

if not exist .env (
    echo Creating .env file...
    copy .env.example .env
)

echo.
echo Mobile app setup complete!
echo.

echo =========================
echo Setup Complete!
echo =========================
echo.
echo To start the project:
echo 1. Backend: cd srla_webstack && venv\Scripts\activate && python api/server.py
echo 2. Mobile: cd srla-mobile && npm start
echo.
pause
