#!/bin/bash

# Paksa Financial System - Production Deployment Script
set -e

echo "🚀 Starting Paksa Financial System Deployment"

# Check if .env exists
if [[ ! -f ".env" ]]; then
    echo "❌ .env file not found. Copy .env.example to .env and configure it."
    exit 1
fi

# Build and start services
echo "📦 Building Docker images..."
docker-compose build --no-cache

echo "🚀 Starting services..."
docker-compose up -d

# Wait for services
echo "⏳ Waiting for services to start..."
sleep 30

# Run database migrations
echo "🗄️ Running database migrations..."
docker-compose exec -T backend alembic upgrade head

# Health check
echo "🔍 Checking service health..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend health check failed"
    exit 1
fi

echo "🎉 Deployment completed successfully!"
echo "📊 Application: http://localhost:3000"
echo "🔧 API: http://localhost:8000"
echo "📖 Docs: http://localhost:8000/docs"