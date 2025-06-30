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
echo - Let you select multiple text/markdown files
echo - Chunk files into 50,000 character segments
echo - Analyze each chunk for themes and content
echo - Create relational database tables with:
echo   * File information and summaries
echo   * Themes and their relationships
echo   * Keywords and tags (5 per file)
echo   * Key points and insights
echo   * Cross-file relationships
echo - Export results to:
echo   * Excel workbook with multiple sheets
echo   * CSV files for all database tables
echo   * Text summary report
echo.
echo Using Google Gemini 2.5 Pro (Enhanced capabilities)
echo.
echo You'll need an OpenRouter API key.
echo Get one at: https://openrouter.ai/
echo.
echo ============================================================
echo.
pause

REM Run the analyzer
python process_text_to_tables.py

echo.
pause
