@echo off
REM Start script for Claw Personal Assistant on Windows

echo Starting Claw Personal Assistant...

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is required but not installed.
    pause
    exit /b 1
)

REM Install dependencies if requirements.txt exists
if exist "requirements.txt" (
    echo Installing dependencies...
    python -m pip install -r requirements.txt
)

REM Start the assistant
echo Starting assistant...
python claw_main.py

pause