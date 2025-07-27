#!/bin/bash

echo "🚀 Starting Paksa Financial System - Production Mode"

# Set environment variables
export ENVIRONMENT=production
export DATABASE_URL=sqlite+aiosqlite:///./paksa_finance.db
export DEBUG=false

# Start backend
echo "🔧 Starting Backend Server..."
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait for backend to start
sleep 5

# Start frontend
echo "🎨 Starting Frontend Server..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo "✅ Paksa Financial System Started Successfully!"
echo "🌐 Backend: http://localhost:8000"
echo "🎨 Frontend: http://localhost:3000"
echo "📚 API Docs: http://localhost:8000/docs"

# Wait for user input to stop
echo "Press Ctrl+C to stop the servers..."
wait