#!/bin/bash

echo "Building Paksa Financial System - Unified Deployment"

# Build frontend
echo "Building frontend..."
cd frontend
npm install
npm run build

# Copy frontend build to backend
echo "Copying frontend to backend..."
cd ..
rm -rf backend/static
cp -r frontend/dist backend/static

# Install backend dependencies
echo "Installing backend dependencies..."
cd backend
pip install -r requirements.txt

echo "Build complete! Deploy the backend folder."