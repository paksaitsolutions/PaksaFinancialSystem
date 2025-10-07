@echo off
echo ========================================
echo   Paksa Financial System - Quick Start
echo ========================================
echo.

:: Check if virtual environment exists
if not exist ".venv" (
    echo Creating Python virtual environment...
    python -m venv .venv
    echo Virtual environment created.
    echo.
)

:: Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

:: Install backend dependencies
echo Installing backend dependencies...
cd backend
pip install -r requirements.txt
cd ..

:: Install frontend dependencies
echo Installing frontend dependencies...
cd frontend
call npm install
cd ..

:: Start both services
echo.
echo ========================================
echo   Starting Paksa Financial System
echo ========================================
echo Backend will run on: http://localhost:8000
echo Frontend will run on: http://localhost:3003
echo API Documentation: http://localhost:8000/docs
echo.

:: Start backend in background
start "Paksa Backend" cmd /k "cd /d %cd% && call .venv\Scripts\activate.bat && cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

:: Wait a moment for backend to start
timeout /t 3 /nobreak >nul

:: Start frontend
start "Paksa Frontend" cmd /k "cd /d %cd%\frontend && npm run dev"

echo.
echo ========================================
echo   Services Started Successfully!
echo ========================================
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3003
echo API Docs: http://localhost:8000/docs
echo.
echo Default Login Credentials:
echo Email: admin@paksa.com
echo Password: admin123
echo.
echo Press any key to exit this window...
pause >nul