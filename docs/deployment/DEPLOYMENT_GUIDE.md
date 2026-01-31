# Render.com Deployment Guide

## Quick Deployment Steps

### 1. Prepare Your Repository
```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### 2. Deploy Backend on Render.com

1. **Create New Web Service**
   - Connect your GitHub repository
   - Choose "Web Service"
   - Select your repository and branch

2. **Configure Build & Start Commands**
   - **Build Command**: `./build.sh`
   - **Start Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **Set Environment Variables** (copy from `.env.render`):
   ```
   PYTHON_VERSION=3.11.0
   DATABASE_URL=<your-postgres-connection-string>
   SECRET_KEY=<generate-random-secret>
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ENVIRONMENT=production
   CORS_ORIGINS=https://your-frontend.onrender.com
   ```

### 3. Deploy Frontend on Render.com

1. **Create Static Site**
   - Connect same repository
   - Choose "Static Site"

2. **Configure Build Settings**
   - **Build Command**: `cd frontend && npm ci && npm run build`
   - **Publish Directory**: `frontend/dist`

3. **Set Environment Variables**:
   ```
   NODE_VERSION=18.17.0
   VITE_API_BASE_URL=https://your-backend.onrender.com
   ```

### 4. Create Database

1. **PostgreSQL Database**
   - Create new PostgreSQL service
   - Copy connection string to backend environment variables

2. **Redis Cache** (Optional)
   - Create Redis service
   - Add REDIS_URL to backend environment variables

## Alternative: Using render.yaml

1. Place `render.yaml` in your repository root
2. Connect repository to Render.com
3. Render will automatically create all services

## Troubleshooting

### Common Issues

1. **Requirements Installation Fails**
   - Check `requirements-linux.txt` for Linux-specific packages
   - Ensure all dependencies have compatible versions

2. **Database Connection Issues**
   - Verify DATABASE_URL format: `postgresql://user:pass@host:port/dbname`
   - Check database service is running

3. **Build Timeout**
   - Optimize requirements.txt (remove dev dependencies)
   - Use Docker deployment for faster builds

4. **CORS Errors**
   - Update CORS_ORIGINS with correct frontend URL
   - Ensure both HTTP and HTTPS origins if needed

### Performance Optimization

1. **Use Docker Deployment**
   ```bash
   # Use Dockerfile.render for optimized builds
   ```

2. **Enable Caching**
   - Use Redis for session storage
   - Enable pip cache in build process

3. **Database Optimization**
   - Use connection pooling
   - Enable database indexes

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:port/db` |
| `SECRET_KEY` | JWT secret key | `your-secret-key-here` |
| `CORS_ORIGINS` | Allowed frontend origins | `https://app.onrender.com` |
| `REDIS_URL` | Redis connection string | `redis://host:port` |
| `ENVIRONMENT` | Deployment environment | `production` |

## Post-Deployment

1. **Create Admin User**
   - Access `/docs` endpoint
   - Use initial superuser credentials

2. **Test API Endpoints**
   - Verify `/health` endpoint
   - Test authentication flow

3. **Monitor Logs**
   - Check Render.com dashboard
   - Monitor error rates and performance