@echo off
echo ========================================
echo   Paksa Financial System - Quick Setup
echo ========================================

:: Create virtual environment
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

:: Activate virtual environment
call .venv\Scripts\activate.bat

:: Install backend dependencies
echo Installing backend dependencies...
cd backend
pip install -r requirements.txt
cd ..

:: Install frontend dependencies
echo Installing frontend dependencies...
cd frontend
npm install
cd ..

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo To start the application:
echo 1. Backend: run_backend.bat
echo 2. Frontend: run_frontend.bat (in a new terminal)
echo.
echo Or use: start_project.bat (starts both)
echo.
pause