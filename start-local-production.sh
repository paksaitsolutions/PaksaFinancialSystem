#!/bin/bash

# Paksa Financial System - Local Production Startup Script

echo "🚀 Starting Paksa Financial System - Local Production Environment"
echo "=================================================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p backups
mkdir -p database

# Set permissions
chmod +x start-local-production.sh

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.local-production.yml down

# Remove old volumes (optional - uncomment if you want fresh data)
# echo "🗑️  Removing old volumes..."
# docker-compose -f docker-compose.local-production.yml down -v

# Build and start services
echo "🔨 Building and starting services..."
docker-compose -f docker-compose.local-production.yml up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Check service health
echo "🏥 Checking service health..."

# Check PostgreSQL
echo "  - PostgreSQL..."
docker-compose -f docker-compose.local-production.yml exec -T postgres pg_isready -U paksa_user -d paksa_financial_local

# Check Redis
echo "  - Redis..."
docker-compose -f docker-compose.local-production.yml exec -T redis redis-cli ping

# Check Backend API
echo "  - Backend API..."
curl -f http://localhost:8000/health || echo "Backend not ready yet"

# Check Frontend
echo "  - Frontend..."
curl -f http://localhost:3000 || echo "Frontend not ready yet"

echo ""
echo "✅ Paksa Financial System is starting up!"
echo ""
echo "🌐 Access URLs:"
echo "   Frontend:  http://localhost:3000"
echo "   Backend:   http://localhost:8000"
echo "   API Docs:  http://localhost:8000/docs"
echo "   Health:    http://localhost:8000/health"
echo ""
echo "👤 Demo Login Credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "📊 Sample Data Included:"
echo "   - GL Accounts (Cash, AR, AP, Revenue, Expenses)"
echo "   - Vendors (Office Supplies Inc, Tech Solutions Ltd)"
echo "   - Customers (ABC Corporation, XYZ Industries)"
echo "   - Employees (John Smith, Sarah Johnson)"
echo ""
echo "🔧 Management Commands:"
echo "   View logs:    docker-compose -f docker-compose.local-production.yml logs -f"
echo "   Stop system:  docker-compose -f docker-compose.local-production.yml down"
echo "   Restart:      docker-compose -f docker-compose.local-production.yml restart"
echo ""
echo "📝 Note: It may take a few minutes for all services to be fully ready."
echo "         Check http://localhost:8000/health for system status."