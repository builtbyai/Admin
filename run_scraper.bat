@echo off
echo Starting Web Scraper...
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
echo Running web scraper...
python web_scraper.py

echo.
echo Scraping complete! Check the 'scraped_content' folder for results.
pause
