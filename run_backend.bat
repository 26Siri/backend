@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

set "PY=%~dp0.venv\Scripts\python.exe"

if not exist "%PY%" (
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo Failed to create venv. Ensure Python is on PATH.
        pause
        exit /b 1
    )
)

echo Upgrading pip...
"%PY%" -m pip install --upgrade pip

echo Installing requirements...
if "%SKIP_HEAVY%"=="1" (
    echo Using lightweight requirements only...
    "%PY%" -m pip install -r requirements-lite.txt
) else (
    "%PY%" -m pip install -r requirements.txt
)

if errorlevel 1 (
    echo Failed to install requirements.
    pause
    exit /b 1
)

echo.
echo Starting uvicorn server on http://127.0.0.1:8000
echo Press Ctrl+C to stop.
echo.

"%PY%" -m uvicorn backend.app:app --host 127.0.0.1 --port 8000 --reload

echo.
echo Server stopped.
pause
endlocal