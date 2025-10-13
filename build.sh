#!/bin/bash
# Build script for Render.com deployment

set -e  # Exit on any error

echo "Starting build process..."

# Detect platform and install requirements
echo "Installing Python dependencies..."
python install_requirements.py

# Navigate to backend directory
cd backend

# Run database migrations
echo "Running database migrations..."
python -m alembic upgrade head

# Initialize database if needed
echo "Initializing database..."
python init_db.py

echo "Build completed successfully!"