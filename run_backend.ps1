# Run backend server (PowerShell helper) without sourcing Activate.ps1 to avoid ExecutionPolicy prompts.
# Usage: Open PowerShell, then:
# cd e:\MINIPTOJECT\backend
# .\run_backend.ps1

param()

$venvDir = Join-Path $PSScriptRoot '.venv'
$pythonExe = Join-Path $venvDir 'Scripts\python.exe'

if (-not (Test-Path $venvDir)) {
    Write-Host 'Creating virtual environment (.venv)...'
    python -m venv .venv
}

if (-not (Test-Path $pythonExe)) {
    Write-Error "Python executable not found at $pythonExe. Ensure Python is installed and venv creation succeeded."
    exit 1
}

Write-Host "Using venv python: $pythonExe"

if (Test-Path 'requirements.txt') {
    Write-Host 'Installing requirements using venv python...'
    & $pythonExe -m pip install --upgrade pip
    & $pythonExe -m pip install -r requirements.txt
}

Write-Host 'Starting uvicorn on 127.0.0.1:8000 (logs -> backend.log). Use Ctrl+C to stop.'
# Run uvicorn with the venv python and tee output to backend.log
& $pythonExe -m uvicorn backend.app:app --host 127.0.0.1 --port 8000 --reload 2>&1 | Tee-Object -FilePath backend.log
