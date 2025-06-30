@echo off
echo Starting Web Scraper with Media Collection...
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
pip install requests beautifulsoup4 urllib3

echo.
echo ============================================================
echo Web Scraper will:
echo - Ask for URLs to scrape (or load from Sources.txt)
echo - Download web pages and convert to Markdown
echo - Download images and media files
echo - Follow links recursively
echo - Save everything in a timestamped folder
echo ============================================================
echo.

REM Run the scraper
python web_scraper.py

echo.
pause
