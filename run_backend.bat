@echo off
echo Starting Paksa Financial System Backend...
echo.

:: Activate virtual environment if it exists
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    echo Virtual environment activated
)

:: Change to backend directory
cd backend

:: Run the backend server
echo Starting backend server on http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000