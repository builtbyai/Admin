@echo off
echo Starting Text File Analyzer...
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
pip install requests pandas openpyxl

echo.
echo ============================================================
echo Text File Analyzer with OpenRouter API
echo ============================================================
echo.
echo This tool will:
echo - Prompt for OpenRouter API key at startup
echo - Let you select multiple text/markdown files
echo - Use AI to intelligently categorize content
echo - Create smart CSV tables organized by:
echo   * Categories and subcategories
echo   * Themes and topics
echo   * Content types and domains
echo   * Tags (5 per file)
echo - Generate summaries for each file
echo - Export only CSV files (no database)
echo.
echo Using Google Gemini 2.5 Pro for intelligent analysis
echo.
echo Get your API key at: https://openrouter.ai/
echo.
echo ============================================================
echo.
pause

REM Run the analyzer
python process_text_to_tables.py

echo.
pause
