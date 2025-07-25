# Troubleshooting Guide

## Common Issues

### Database Issues

#### Connection Refused
**Symptoms**: `Connection refused` or `could not connect to server`

**Diagnosis**:
```bash
# Check if PostgreSQL is running
docker-compose ps postgres
kubectl get pods -l app=postgres -n paksa-financial

# Check connection string
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT 1;"
```

**Solutions**:
```bash
# Restart database
docker-compose restart postgres

# Check database logs
docker-compose logs postgres

# Verify network connectivity
docker-compose exec backend ping postgres
```

#### Slow Queries
**Symptoms**: High response times, database timeouts

**Diagnosis**:
```sql
-- Check slow queries
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC LIMIT 10;

-- Check active connections
SELECT * FROM pg_stat_activity WHERE state = 'active';
```

**Solutions**:
```sql
-- Add missing indexes
CREATE INDEX CONCURRENTLY idx_invoices_tenant_date 
ON invoices (tenant_id, created_at);

-- Update table statistics
ANALYZE invoices;

-- Kill long-running queries
SELECT pg_terminate_backend(pid) FROM pg_stat_activity 
WHERE state = 'active' AND query_start < now() - interval '5 minutes';
```

### Application Issues

#### High Memory Usage
**Symptoms**: Out of memory errors, slow performance

**Diagnosis**:
```bash
# Check memory usage
docker stats
kubectl top pods -n paksa-financial

# Check application metrics
curl http://localhost:8000/metrics | grep memory
```

**Solutions**:
```bash
# Restart application
docker-compose restart backend
kubectl rollout restart deployment/paksa-backend -n paksa-financial

# Scale down replicas temporarily
kubectl scale deployment paksa-backend --replicas=1 -n paksa-financial

# Increase memory limits
# Edit k8s/deployment.yaml and increase memory limits
```

#### Authentication Failures
**Symptoms**: 401 Unauthorized, JWT token errors

**Diagnosis**:
```bash
# Check JWT token
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/auth/verify

# Check logs for auth errors
docker-compose logs backend | grep -i auth
```

**Solutions**:
```bash
# Clear Redis cache
docker-compose exec redis redis-cli FLUSHALL

# Restart auth service
docker-compose restart backend

# Check JWT secret configuration
echo $JWT_SECRET_KEY
```

### Performance Issues

#### Slow API Responses
**Symptoms**: High response times, timeouts

**Diagnosis**:
```bash
# Check API response times
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/api/v1/invoices

# Check database query performance
# See Database Issues > Slow Queries above

# Check Redis cache hit rate
docker-compose exec redis redis-cli info stats | grep hit_rate
```

**Solutions**:
```bash
# Enable query caching
# Add @cache_result decorator to slow endpoints

# Optimize database queries
# Add appropriate indexes

# Scale horizontally
kubectl scale deployment paksa-backend --replicas=3 -n paksa-financial
```

#### High CPU Usage
**Symptoms**: Slow response, high load average

**Diagnosis**:
```bash
# Check CPU usage
docker stats
kubectl top pods -n paksa-financial

# Profile application
# Add profiling middleware to identify bottlenecks
```

**Solutions**:
```bash
# Scale up resources
kubectl patch deployment paksa-backend -p '{"spec":{"template":{"spec":{"containers":[{"name":"backend","resources":{"limits":{"cpu":"1000m"}}}]}}}}'

# Optimize code
# Review and optimize CPU-intensive operations

# Enable caching
# Cache expensive computations
```

### Network Issues

#### Load Balancer Errors
**Symptoms**: 502 Bad Gateway, 503 Service Unavailable

**Diagnosis**:
```bash
# Check backend health
curl http://backend:8000/health

# Check nginx configuration
docker-compose exec nginx nginx -t

# Check upstream servers
docker-compose logs nginx | grep upstream
```

**Solutions**:
```bash
# Restart load balancer
docker-compose restart nginx

# Check backend service status
kubectl get endpoints paksa-backend-service -n paksa-financial

# Update health check configuration
# Edit nginx configuration to adjust health check intervals
```

#### SSL Certificate Issues
**Symptoms**: SSL handshake failures, certificate warnings

**Diagnosis**:
```bash
# Check certificate validity
openssl x509 -in /path/to/cert.pem -text -noout

# Test SSL connection
openssl s_client -connect api.paksafinancial.com:443
```

**Solutions**:
```bash
# Renew certificate
certbot renew

# Update Kubernetes secret
kubectl create secret tls paksa-tls-secret --cert=cert.pem --key=key.pem -n paksa-financial --dry-run=client -o yaml | kubectl apply -f -

# Restart ingress controller
kubectl rollout restart deployment/nginx-ingress-controller
```

### Data Issues

#### Data Corruption
**Symptoms**: Inconsistent data, foreign key violations

**Diagnosis**:
```sql
-- Check data integrity
SELECT * FROM invoices WHERE total_amount < 0;

-- Check foreign key constraints
SELECT conname, conrelid::regclass, confrelid::regclass 
FROM pg_constraint WHERE contype = 'f';
```

**Solutions**:
```sql
-- Fix data inconsistencies
UPDATE invoices SET total_amount = subtotal + tax_amount 
WHERE total_amount != subtotal + tax_amount;

-- Restore from backup if needed
-- See deployment guide for backup restoration steps
```

#### Migration Failures
**Symptoms**: Alembic migration errors, schema mismatches

**Diagnosis**:
```bash
# Check migration status
docker-compose exec backend alembic current
docker-compose exec backend alembic history

# Check for conflicts
docker-compose exec backend alembic show head
```

**Solutions**:
```bash
# Resolve migration conflicts
docker-compose exec backend alembic merge heads

# Rollback problematic migration
docker-compose exec backend alembic downgrade -1

# Manual schema fixes if needed
docker-compose exec postgres psql -U postgres paksa_db
```

## Monitoring and Alerting

### Key Metrics to Monitor
- **Response Time**: API endpoint response times
- **Error Rate**: HTTP 4xx/5xx error rates
- **Database Performance**: Query execution time, connection count
- **Memory Usage**: Application and database memory consumption
- **CPU Usage**: System and application CPU utilization

### Setting Up Alerts
```yaml
# Prometheus alert rules
groups:
- name: paksa_alerts
  rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
    for: 2m
    annotations:
      summary: "High error rate detected"
      
  - alert: DatabaseConnectionHigh
    expr: pg_stat_database_numbackends > 80
    for: 5m
    annotations:
      summary: "High database connection count"
```

### Log Analysis
```bash
# Search for errors in logs
docker-compose logs backend | grep -i error

# Monitor real-time logs
docker-compose logs -f backend | grep -E "(ERROR|CRITICAL)"

# Analyze access patterns
kubectl logs -l app=paksa-backend -n paksa-financial | grep "POST /api"
```

## Emergency Procedures

### System Down
1. Check all services: `kubectl get pods -n paksa-financial`
2. Restart failed services: `kubectl rollout restart deployment/paksa-backend`
3. Check database connectivity: `kubectl exec -it postgres-primary-0 -- pg_isready`
4. Verify load balancer: `curl -I https://api.paksafinancial.com/health`
5. Notify stakeholders if issue persists

### Data Loss
1. Stop all write operations immediately
2. Assess extent of data loss
3. Restore from most recent backup
4. Verify data integrity after restoration
5. Resume operations and monitor closely

### Security Breach
1. Isolate affected systems
2. Change all passwords and API keys
3. Review access logs for unauthorized activity
4. Apply security patches
5. Conduct security audit before resuming operations

## Getting Help

### Internal Resources
- **Documentation**: `/docs` directory
- **API Reference**: `http://localhost:8000/docs`
- **Monitoring**: `http://localhost:3001` (Grafana)

### External Support
- **GitHub Issues**: Report bugs and feature requests
- **Community Forum**: Technical discussions
- **Professional Support**: Contact Paksa IT Solutions

### Escalation Process
1. **Level 1**: Development team
2. **Level 2**: DevOps/Infrastructure team  
3. **Level 3**: Senior architects
4. **Level 4**: External consultants