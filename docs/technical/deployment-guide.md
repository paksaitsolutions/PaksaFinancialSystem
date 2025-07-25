# Deployment Guide

## Prerequisites

### System Requirements
- **OS**: Linux (Ubuntu 20.04+ recommended)
- **Memory**: 8GB RAM minimum, 16GB recommended
- **Storage**: 100GB SSD minimum
- **CPU**: 4 cores minimum, 8 cores recommended

### Software Dependencies
- Docker 20.10+
- Docker Compose 2.0+
- Kubernetes 1.24+ (for production)
- PostgreSQL 15+
- Redis 6+

## Development Deployment

### 1. Clone Repository
```bash
git clone https://github.com/paksaitsolutions/PaksaFinancialSystem.git
cd PaksaFinancialSystem
```

### 2. Environment Configuration
```bash
# Copy environment templates
cp .env.example .env
cp frontend/.env.example frontend/.env

# Configure database settings
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/paksa_db
REDIS_URL=redis://localhost:6379/0
```

### 3. Start Services
```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f backend
```

### 4. Database Setup
```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Create initial data
docker-compose exec backend python scripts/create_initial_data.py
```

## Production Deployment

### 1. Kubernetes Deployment
```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Deploy secrets
kubectl create secret generic paksa-secrets \
  --from-literal=database-url="postgresql://user:pass@host:5432/db" \
  --from-literal=redis-url="redis://host:6379/0" \
  -n paksa-financial

# Deploy applications
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
kubectl apply -f k8s/hpa.yaml
```

### 2. Database Setup
```bash
# Primary database
kubectl exec -it postgres-primary-0 -- psql -U postgres
CREATE DATABASE paksa_db;
CREATE USER paksa_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE paksa_db TO paksa_user;

# Setup replication
kubectl exec -it postgres-replica-0 -- pg_basebackup -h postgres-primary -D /var/lib/postgresql/data -U replicator -v -P -W
```

### 3. SSL Configuration
```bash
# Generate SSL certificates
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout tls.key -out tls.crt \
  -subj "/CN=api.paksafinancial.com"

# Create TLS secret
kubectl create secret tls paksa-tls-secret \
  --cert=tls.crt --key=tls.key -n paksa-financial
```

## Docker Compose Production

### 1. Production Configuration
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  backend:
    build: ./backend
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - DEBUG=false
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
    restart: unless-stopped

  frontend:
    build: ./frontend
    environment:
      - NODE_ENV=production
    deploy:
      replicas: 2
    restart: unless-stopped
```

### 2. Start Production Stack
```bash
# Start with production config
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Scale services
docker-compose up -d --scale backend=3 --scale frontend=2
```

## Monitoring Setup

### 1. Prometheus & Grafana
```bash
# Start monitoring stack
docker-compose -f docker-compose.monitoring.yml up -d

# Access Grafana
open http://localhost:3001
# Login: admin/admin
```

### 2. Log Aggregation
```bash
# Start logging stack
docker-compose -f docker-compose.logging.yml up -d

# View logs in Grafana
# Add Loki datasource: http://loki:3100
```

## Health Checks

### Application Health
```bash
# Backend health
curl http://localhost:8000/health

# Frontend health
curl http://localhost:3000/

# Database health
docker-compose exec postgres pg_isready
```

### Kubernetes Health
```bash
# Check pod status
kubectl get pods -n paksa-financial

# Check service endpoints
kubectl get endpoints -n paksa-financial

# View pod logs
kubectl logs -f deployment/paksa-backend -n paksa-financial
```

## Backup & Recovery

### Database Backup
```bash
# Create backup
docker-compose exec postgres pg_dump -U postgres paksa_db > backup.sql

# Restore backup
docker-compose exec -T postgres psql -U postgres paksa_db < backup.sql
```

### Application Data Backup
```bash
# Backup volumes
docker run --rm -v paksa_postgres_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/postgres_backup.tar.gz /data

# Restore volumes
docker run --rm -v paksa_postgres_data:/data -v $(pwd):/backup \
  alpine tar xzf /backup/postgres_backup.tar.gz -C /
```

## Troubleshooting

### Common Issues

#### Database Connection Failed
```bash
# Check database status
docker-compose exec postgres pg_isready

# Check connection string
echo $DATABASE_URL

# Reset database
docker-compose down postgres
docker volume rm paksa_postgres_data
docker-compose up -d postgres
```

#### High Memory Usage
```bash
# Check memory usage
docker stats

# Restart services
docker-compose restart backend

# Scale down if needed
docker-compose up -d --scale backend=1
```

#### SSL Certificate Issues
```bash
# Check certificate validity
openssl x509 -in tls.crt -text -noout

# Regenerate certificate
kubectl delete secret paksa-tls-secret -n paksa-financial
# Follow SSL configuration steps above
```

## Performance Tuning

### Database Optimization
```sql
-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM invoices WHERE tenant_id = 'uuid';

-- Update statistics
ANALYZE;

-- Reindex if needed
REINDEX DATABASE paksa_db;
```

### Application Tuning
```bash
# Increase worker processes
export WORKERS=4
docker-compose up -d backend

# Tune memory limits
docker-compose up -d --scale backend=2
```

## Security Checklist

- [ ] SSL/TLS certificates configured
- [ ] Database passwords changed from defaults
- [ ] Firewall rules configured
- [ ] Regular security updates applied
- [ ] Backup encryption enabled
- [ ] Access logs monitored
- [ ] Rate limiting configured