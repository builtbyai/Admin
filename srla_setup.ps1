Write-Host "SRLA Project Setup Script" -ForegroundColor Green
Write-Host "=========================" -ForegroundColor Green
Write-Host ""

# Check if Node.js is installed
try {
    $nodeVersion = node --version
    Write-Host "Found Node.js $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Node.js is not installed!" -ForegroundColor Red
    Write-Host "Please download and install Node.js from https://nodejs.org/" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if Python is installed
try {
    $pythonVersion = python --version
    Write-Host "Found $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed!" -ForegroundColor Red
    Write-Host "Please download and install Python from https://www.python.org/" -ForegroundColor Yellow
    Write-Host "Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Backend setup
Write-Host "Setting up Backend..." -ForegroundColor Cyan
Set-Location srla_webstack

if (!(Test-Path venv)) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
& venv\Scripts\Activate.ps1
pip install -r requirements.txt

if (!(Test-Path .env)) {
    Write-Host "Creating .env file..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "Please edit srla_webstack\.env with your API keys" -ForegroundColor Magenta
}

Write-Host ""
Write-Host "Backend setup complete!" -ForegroundColor Green
Write-Host ""

# Mobile app setup
Write-Host "Setting up Mobile App..." -ForegroundColor Cyan
Set-Location ..\srla-mobile

Write-Host "Installing npm dependencies..." -ForegroundColor Yellow
npm install

if (!(Test-Path .env)) {
    Write-Host "Creating .env file..." -ForegroundColor Yellow
    Copy-Item .env.example .env
}

Write-Host ""
Write-Host "Mobile app setup complete!" -ForegroundColor Green
Write-Host ""

Write-Host "=========================" -ForegroundColor Green
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "=========================" -ForegroundColor Green
Write-Host ""
Write-Host "To start the project:" -ForegroundColor Cyan
Write-Host "1. Backend: cd srla_webstack && venv\Scripts\activate && python api/server.py" -ForegroundColor Yellow
Write-Host "2. Mobile: cd srla-mobile && npm start" -ForegroundColor Yellow
Write-Host ""
Read-Host "Press Enter to exit"
