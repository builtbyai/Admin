@echo off
echo Text File Organizer - First Time Setup and Launch
echo ================================================

REM Check if this is first run by looking for requirements file
if not exist "requirements_installed.flag" (
    echo First time setup - Installing requirements...
    echo.
    
    REM Install required packages
    pip install -r requirements_text_organizer.txt
    
    if %errorlevel% neq 0 (
        echo Error installing requirements. Please check your Python installation.
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

REM Run the Python script
python text_organizer.py

if %errorlevel% neq 0 (
    echo Error running the text organizer. Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo Text File Organizer finished.
pause
