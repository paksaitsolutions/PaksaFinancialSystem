@echo off
echo ========================================
echo   Paksa Financial System - Dev Setup
echo ========================================
echo.

:: Create virtual environment if it doesn't exist
if not exist ".venv" (
    echo Creating Python virtual environment...
    python -m venv .venv
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)

:: Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

:: Install backend dependencies
echo.
echo Installing backend dependencies...
cd backend
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Failed to install backend dependencies
    pause
    exit /b 1
)
echo ✅ Backend dependencies installed
cd ..

:: Initialize database
echo.
echo Initializing database...
cd backend
python -c "from app.core.database import init_db; init_db(); print('✅ Database initialized')"
if %errorlevel% neq 0 (
    echo ❌ Database initialization failed
    pause
    exit /b 1
)
cd ..

:: Install frontend dependencies
echo.
echo Installing frontend dependencies...
cd frontend
call npm install
if %errorlevel% neq 0 (
    echo ❌ Failed to install frontend dependencies
    pause
    exit /b 1
)
echo ✅ Frontend dependencies installed
cd ..

echo.
echo ========================================
echo   Development Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Run 'start_project.bat' to start both services
echo 2. Open http://localhost:3003 in your browser
echo 3. Login with admin@paksa.com / admin123
echo.
echo Available scripts:
echo - start_project.bat: Start both backend and frontend
echo - backend\app\main.py: Backend server
echo - frontend\npm run dev: Frontend development server
echo.
pause