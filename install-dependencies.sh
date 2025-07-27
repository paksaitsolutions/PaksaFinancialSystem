#!/bin/bash

echo "🚀 Installing Paksa Financial System Dependencies..."

# Backend Dependencies
echo "📦 Installing Backend Dependencies..."
cd backend
pip install -r requirements.txt

# Frontend Dependencies
echo "📦 Installing Frontend Dependencies..."
cd ../frontend
npm install

echo "✅ All dependencies installed successfully!"
echo "🎯 Ready to start the application"