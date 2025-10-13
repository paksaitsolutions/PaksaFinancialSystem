#!/bin/bash
set -e

echo "=== Building Paksa Financial System for Render.com ==="
echo "Current directory: $(pwd)"
echo "Files: $(ls -la)"

# Make script executable
chmod +x render-build.sh

# Install Node.js if not available
if ! command -v node &> /dev/null; then
    echo "Installing Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

# Install frontend dependencies and build
if [ -d "frontend" ]; then
    echo "=== Building Frontend ==="
    cd frontend
    
    # Install dependencies
    echo "Installing npm dependencies..."
    npm ci --production=false
    
    # Build frontend
    echo "Building Vue.js application..."
    npm run build
    
    echo "Frontend build complete. Contents of dist:"
    ls -la dist/
    
    cd ..
    
    # Copy frontend build to backend static folder
    echo "=== Copying Frontend Files ==="
    mkdir -p backend/static
    cp -r frontend/dist/* backend/static/
    
    echo "Frontend files copied. Backend static contents:"
    ls -la backend/static/
else
    echo "ERROR: Frontend directory not found"
    exit 1
fi

# Install backend dependencies
echo "=== Installing Backend Dependencies ==="
cd backend
pip install --upgrade pip
pip install -r requirements.txt

echo "=== Build Complete ==="
echo "Starting application..."

# Start the application
exec python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}