@echo off
echo Starting Markdown to Wiki Builder...
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
pip install requests

echo.
echo ============================================================
echo Markdown to Wiki Builder
echo ============================================================
echo.
echo This tool will:
echo - Let you select multiple markdown files
echo - Analyze and structure the content
echo - Generate a comprehensive wiki with:
echo   * Table of contents
echo   * Organized sections
echo   * Cross-references
echo   * Keyword index
echo   * ~20,000 words of content
echo.
echo You'll need an OpenRouter API key.
echo Get one free at: https://openrouter.ai/
echo.
echo ============================================================
echo.
pause

REM Run the wiki builder
python combine_md_to_wiki.py

echo.
pause
