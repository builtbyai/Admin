@echo off
echo Building webstack from HTML file...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

REM Install required packages
echo Installing required packages...
pip install beautifulsoup4 lxml

echo.
echo Running HTML to Webstack converter...
python html_to_webstack.py

echo.
echo Process complete!
pause
