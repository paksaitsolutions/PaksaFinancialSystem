#!/bin/bash

echo "Building Paksa Financial System for Render.com"

# Install frontend dependencies and build
cd frontend
npm install
npm run build

# Copy frontend build to backend static folder
cd ..
mkdir -p backend/static
cp -r frontend/dist/* backend/static/

# Install backend dependencies
cd backend
pip install -r requirements.txt

echo "Build complete for Render.com deployment"