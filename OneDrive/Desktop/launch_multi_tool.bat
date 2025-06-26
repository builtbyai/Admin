@echo off
echo Starting Multi-Use File Organizer Tool...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking required packages...
python -c "import tkinter, PIL, pytesseract, watchdog, pandas, eyed3, mutagen, cv2, numpy" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install pillow pytesseract watchdog pandas eyed3 mutagen-python opencv-python numpy
    if errorlevel 1 (
        echo Failed to install required packages
        pause
        exit /b 1
    )
)

REM Launch the application
echo Launching Multi-Tool Application...
python "%~dp0multi_tool.py"

if errorlevel 1 (
    echo Application encountered an error
    pause
)
