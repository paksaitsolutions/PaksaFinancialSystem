from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import os
from functools import wraps
import logging
from starlette.middleware.base import BaseHTTPMiddleware

# Configure logging
logger = logging.getLogger(__name__)

class SecurityConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    RATE_LIMIT = 100  # requests per minute
    TOKEN_AUDIENCE = "paksa-financial-system"

class RateLimiter:
    def __init__(self):
        self.requests = {}
    
    async def check_rate_limit(self, client_ip: str) -> bool:
        current_time = datetime.utcnow()
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        # Remove old requests
        self.requests[client_ip] = [t for t in self.requests[client_ip] 
                                  if t > current_time - timedelta(minutes=1)]
        
        if len(self.requests[client_ip]) >= SecurityConfig.RATE_LIMIT:
            return False
        
        self.requests[client_ip].append(current_time)
        return True

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)
        self.rate_limiter = RateLimiter()
    
    async def __call__(self, request: Request):
        # Rate limiting check
        client_ip = request.client.host if request.client else "unknown"
        if not await self.rate_limiter.check_rate_limit(client_ip):
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
                headers={"Retry-After": "60"}
            )
        
        # JWT verification
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        try:
            payload = self.verify_jwt(credentials.credentials)
            request.state.user = payload
            return payload
        except JWTError as e:
            logger.error(f"JWT verification failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    def verify_jwt(self, token: str) -> Dict[str, Any]:
        try:
            payload = jwt.decode(
                token,
                SecurityConfig.SECRET_KEY,
                algorithms=[SecurityConfig.ALGORITHM],
                audience=SecurityConfig.TOKEN_AUDIENCE
            )
            return payload
        except JWTError as e:
            logger.error(f"JWT verification error: {str(e)}")
            raise

def role_required(required_roles: list):
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            user_roles = request.state.user.get("roles", [])
            if not any(role in user_roles for role in required_roles):
                logger.warning(f"Unauthorized access attempt by user {request.state.user.get('sub')} for role(s) {required_roles}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Log security headers
        logger.debug(f"Security headers set for {request.url}")
        
        return response

def validate_input(data: Any, schema: Any) -> bool:
    """Generic input validation using Pydantic schemas"""
    try:
        schema.model_validate(data)
        return True
    except Exception as e:
        logger.warning(f"Input validation failed: {str(e)}")
        return False

def sanitize_input(input_data: str) -> str:
    """Basic input sanitization to prevent XSS and injection attacks"""
    if not input_data:
        return ""
    
    # Basic XSS prevention
    sanitized = (
        input_data.replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#x27;")
    )
    
    # Prevent SQL injection (additional parameterized queries should be used)
    sql_keywords = [
        "SELECT", "INSERT", "UPDATE", "DELETE", "DROP", "--",
        "UNION", "OR 1=1", ";", "' OR '1'='1"
    ]
    
    for keyword in sql_keywords:
        if keyword in input_data.upper():
            logger.warning(f"Potential SQL injection attempt detected: {input_data}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid input detected"
            )
    
    return sanitized
