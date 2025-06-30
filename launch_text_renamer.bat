@echo off
echo Starting Media File Renamer...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

REM Check if the script exists
if not exist "text_file_renamer.py" (
    echo Error: text_file_renamer.py not found
    echo Please ensure the script is in the same directory as this batch file
    pause
    exit /b 1
)

REM Run the Python script
python text_file_renamer.py

if errorlevel 1 (
    echo.
    echo Error occurred while running the script
    pause
)
