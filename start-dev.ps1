# Paksa Financial System - Development Startup Script
Write-Host "Starting Paksa Financial System Development Environment..." -ForegroundColor Green

# Check if Node.js is installed
try {
    $nodeVersion = node --version
    Write-Host "Node.js version: $nodeVersion" -ForegroundColor Cyan
} catch {
    Write-Host "Error: Node.js is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

# Check if Python is installed
try {
    $pythonVersion = python --version
    Write-Host "Python version: $pythonVersion" -ForegroundColor Cyan
} catch {
    Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

# Start Backend
Write-Host "`nStarting Backend Server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\backend'; if (Test-Path '.venv') { .\.venv\Scripts\Activate.ps1 } else { python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt }; uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

# Wait a moment for backend to start
Start-Sleep -Seconds 3

# Start Frontend
Write-Host "Starting Frontend Server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\frontend'; npm install; npm run dev"

Write-Host "`nDevelopment servers are starting..." -ForegroundColor Green
Write-Host "Backend will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Frontend will be available at: http://localhost:3003" -ForegroundColor Cyan
Write-Host "API Documentation will be available at: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "`nPress any key to exit..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")