#!/bin/bash
set -e

echo "=== Building Paksa Financial System for Render.com ==="
echo "Current directory: $(pwd)"
echo "Files: $(ls -la)"

# Make script executable
chmod +x render-build.sh

# Ensure backend static directory exists with fallback
echo "=== Preparing Static Files ==="
mkdir -p backend/static

# Create fallback index.html if it doesn't exist
if [ ! -f "backend/static/index.html" ]; then
    echo "Creating fallback index.html..."
    cat > backend/static/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Paksa Financial System</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; text-align: center; }
        .status { background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .api-links { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }
        .api-link { background: #3498db; color: white; padding: 15px; text-decoration: none; border-radius: 5px; text-align: center; }
        .api-link:hover { background: #2980b9; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏦 Paksa Financial System</h1>
        <div class="status">
            <strong>✅ System Status:</strong> Operational<br>
            <strong>📊 Version:</strong> 1.0.0<br>
            <strong>🔧 Environment:</strong> Production
        </div>
        <h2>API Access</h2>
        <div class="api-links">
            <a href="/docs" class="api-link">📚 API Documentation</a>
            <a href="/health" class="api-link">❤️ Health Check</a>
            <a href="/api/info" class="api-link">ℹ️ System Info</a>
        </div>
        <p><strong>Demo Login:</strong> admin@paksa.com / admin123</p>
    </div>
</body>
</html>
EOF
fi

# Try to build frontend if available
if [ -d "frontend" ] && command -v node &> /dev/null; then
    echo "=== Attempting Frontend Build ==="
    cd frontend
    
    # Try to install dependencies and build
    if npm ci --production=false && npm run build; then
        echo "Frontend build successful!"
        cd ..
        cp -r frontend/dist/* backend/static/ 2>/dev/null || echo "Warning: Could not copy some frontend files"
        echo "Frontend files copied to backend/static/"
    else
        echo "Frontend build failed, using fallback HTML"
        cd ..
    fi
else
    echo "Node.js not available or frontend directory missing, using fallback HTML"
fi

echo "Static files ready. Contents:"
ls -la backend/static/

# Install backend dependencies
echo "=== Installing Backend Dependencies ==="
cd backend
pip install --upgrade pip
pip install -r requirements.txt

echo "=== Build Complete ==="
echo "Starting application..."

# Start the application
exec python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}