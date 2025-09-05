@echo off
echo Installing Paksa Financial System Dependencies...

echo.
echo Installing Backend Dependencies...
cd backend
pip install -r requirements.txt
pip install -r requirements-dev.txt

echo.
echo Installing Frontend Dependencies...
cd ../frontend
npm install

echo.
echo Dependencies installed successfully!
echo.
echo To run the application:
echo Backend: cd backend && python -m uvicorn app.main:app --reload
echo Frontend: cd frontend && npm run dev

pause