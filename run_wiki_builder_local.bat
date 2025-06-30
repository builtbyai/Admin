@echo off
echo Starting Local Markdown to Wiki Builder...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Local Markdown to Wiki Builder (No API Required)
echo ============================================================
echo.
echo This tool will:
echo - Let you select multiple markdown files
echo - Analyze and structure the content locally
echo - Generate a comprehensive wiki with:
echo   * Table of contents with links
echo   * Organized categories
echo   * Cross-references
echo   * Keyword index
echo   * File index
echo   * Glossary
echo   * Extended examples
echo   * FAQ section
echo   * Target: ~20,000 words
echo.
echo ============================================================
echo.

REM Run the local wiki builder
python combine_md_to_wiki_local.py

echo.
pause
