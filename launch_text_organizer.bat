@echo off
echo Text File Organizer - First Time Setup and Launch
echo ================================================

REM Check Python installation
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

python --version
echo.

REM Check if this is first run by looking for requirements file
if not exist "requirements_installed.flag" (
    echo First time setup - Installing requirements...
    echo.
    
    REM Try to fix potential pip issues first
    echo Upgrading pip...
    python -m pip install --upgrade pip
    
    REM Install required packages with more specific error handling
    echo Installing required packages...
    python -m pip install -r requirements_text_organizer.txt
    
    if %errorlevel% neq 0 (
        echo.
        echo Error installing requirements. This might be due to:
        echo 1. Python environment conflicts
        echo 2. Missing Visual C++ build tools
        echo 3. Network connectivity issues
        echo.
        echo Try running these commands manually:
        echo   python -m pip install --upgrade pip
        echo   python -m pip install -r requirements_text_organizer.txt
        echo.
        pause
        exit /b 1
    )
    
    REM Create flag file to indicate requirements are installed
    echo Requirements installed on %date% %time% > requirements_installed.flag
    echo.
    echo Setup complete!
    echo.
)

echo Launching Text File Organizer...
echo.

REM Test basic Python functionality first
echo Testing Python environment...
python -c "import sys; print('Python executable:', sys.executable)"
if %errorlevel% neq 0 (
    echo Error: Python environment appears to be corrupted.
    echo Please reinstall Python or try using a virtual environment.
    pause
    exit /b 1
)

REM Skip dependency installation and try minimal version due to Python environment issues
echo Python environment appears corrupted, using minimal version...
python text_organizer_minimal.py

if %errorlevel% neq 0 (
    echo.
    echo Error running the minimal text organizer.
    echo Your Python installation may be corrupted.
    echo Consider reinstalling Python from https://python.org
    echo.
    pause
    exit /b 1
)

echo.
echo Text File Organizer finished.
pause
