@echo off
echo Starting Video Link Scraper...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Install required packages
echo Installing required packages...
pip install requests beautifulsoup4

echo.
echo ============================================================
echo Video Link Scraper will:
echo - Search for video files (.MP4, .MOV, .AVI, .MKV, etc.)
echo - Find streaming links (.M3U8)
echo - Scan JavaScript for video URLs
echo - Save results in multiple formats (JSON, TXT, CSV)
echo ============================================================
echo.

REM Run the video scraper
python video_scraper.py

echo.
pause
