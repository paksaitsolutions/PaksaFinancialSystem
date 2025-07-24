#!/bin/bash

set -e

ENVIRONMENT=${1:-staging}
VERSION=${2:-latest}

echo "Deploying Paksa Financial System to $ENVIRONMENT environment..."

# Build and push Docker images
echo "Building Docker images..."
docker build -t paksafinancial/backend:$VERSION ./backend
docker build -t paksafinancial/frontend:$VERSION ./frontend

if [ "$ENVIRONMENT" = "production" ]; then
    echo "Pushing to production registry..."
    docker push paksafinancial/backend:$VERSION
    docker push paksafinancial/frontend:$VERSION
fi

# Deploy to Kubernetes
echo "Deploying to Kubernetes..."
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Wait for deployment
echo "Waiting for deployment to complete..."
kubectl rollout status deployment/paksa-backend -n paksa-financial
kubectl rollout status deployment/paksa-frontend -n paksa-financial

# Run health checks
echo "Running health checks..."
kubectl get pods -n paksa-financial
kubectl get services -n paksa-financial

echo "Deployment completed successfully!"