# Paksa Financial System Deployment Script for Windows
param(
    [switch]$Build,
    [switch]$Stop,
    [switch]$Restart,
    [switch]$Logs
)

Write-Host "🚀 Paksa Financial System Deployment" -ForegroundColor Green

# Check if Docker is installed
try {
    docker --version | Out-Null
    docker-compose --version | Out-Null
} catch {
    Write-Host "❌ Docker or Docker Compose is not installed. Please install Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Create necessary directories
Write-Host "📁 Creating necessary directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "backend\logs" | Out-Null
New-Item -ItemType Directory -Force -Path "backend\uploads" | Out-Null
New-Item -ItemType Directory -Force -Path "postgres_data" | Out-Null
New-Item -ItemType Directory -Force -Path "redis_data" | Out-Null

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  .env file not found. Creating from template..." -ForegroundColor Yellow
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
    }
    Write-Host "📝 Please edit .env file with your configuration before continuing." -ForegroundColor Yellow
    Write-Host "Press Enter to continue after editing .env file..."
    Read-Host
}

if ($Stop) {
    Write-Host "🛑 Stopping services..." -ForegroundColor Yellow
    docker-compose down
    exit 0
}

if ($Logs) {
    Write-Host "📋 Showing logs..." -ForegroundColor Yellow
    docker-compose logs -f
    exit 0
}

if ($Restart) {
    Write-Host "🔄 Restarting services..." -ForegroundColor Yellow
    docker-compose restart
    exit 0
}

# Build and start services
if ($Build) {
    Write-Host "🔨 Building Docker images..." -ForegroundColor Yellow
    docker-compose build --no-cache
}

Write-Host "🚀 Starting services..." -ForegroundColor Yellow
docker-compose up -d

# Wait for services to be ready
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Check service health
Write-Host "🔍 Checking service health..." -ForegroundColor Yellow

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Backend is healthy" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Backend health check failed" -ForegroundColor Red
    docker-compose logs backend
}

try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Frontend is accessible" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Frontend is not accessible" -ForegroundColor Red
    docker-compose logs frontend
}

try {
    $response = Invoke-WebRequest -Uri "http://localhost" -UseBasicParsing -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Nginx is running" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Nginx is not accessible" -ForegroundColor Red
    docker-compose logs nginx
}

Write-Host ""
Write-Host "🎉 Deployment completed!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Service URLs:" -ForegroundColor Cyan
Write-Host "   Frontend: http://localhost" -ForegroundColor White
Write-Host "   Backend API: http://localhost/api" -ForegroundColor White
Write-Host "   API Docs: http://localhost/docs" -ForegroundColor White
Write-Host ""
Write-Host "🔐 Default Login:" -ForegroundColor Cyan
Write-Host "   Email: admin@paksa.com" -ForegroundColor White
Write-Host "   Password: admin123" -ForegroundColor White
Write-Host ""
Write-Host "📋 Useful Commands:" -ForegroundColor Cyan
Write-Host "   View logs: .\deploy.ps1 -Logs" -ForegroundColor White
Write-Host "   Stop services: .\deploy.ps1 -Stop" -ForegroundColor White
Write-Host "   Restart services: .\deploy.ps1 -Restart" -ForegroundColor White
Write-Host "   Rebuild: .\deploy.ps1 -Build" -ForegroundColor White
Write-Host ""