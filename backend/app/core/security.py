from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import redis
import json
from ..core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Security
security = HTTPBearer()

# Redis for session management
redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

class SecurityManager:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    @staticmethod
    def create_refresh_token(data: Dict[str, Any]) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> Dict[str, Any]:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            if payload.get("type") != token_type:
                raise HTTPException(status_code=401, detail="Invalid token type")
            return payload
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    @staticmethod
    def blacklist_token(token: str):
        """Add token to blacklist"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            exp = payload.get("exp")
            if exp:
                ttl = exp - int(datetime.utcnow().timestamp())
                if ttl > 0:
                    redis_client.setex(f"blacklist:{token}", ttl, "1")
        except JWTError:
            pass
    
    @staticmethod
    def is_token_blacklisted(token: str) -> bool:
        return redis_client.exists(f"blacklist:{token}") > 0

class RateLimiter:
    @staticmethod
    def check_rate_limit(request: Request, identifier: str, limit: int = 60, window: int = 60):
        """Rate limiting implementation"""
        key = f"rate_limit:{identifier}:{int(datetime.utcnow().timestamp() // window)}"
        current = redis_client.get(key)
        
        if current is None:
            redis_client.setex(key, window, 1)
            return True
        
        if int(current) >= limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )
        
        redis_client.incr(key)
        return True

class LoginAttemptTracker:
    @staticmethod
    def record_failed_attempt(identifier: str):
        """Record failed login attempt"""
        key = f"login_attempts:{identifier}"
        attempts = redis_client.get(key)
        
        if attempts is None:
            redis_client.setex(key, settings.LOCKOUT_DURATION_MINUTES * 60, 1)
        else:
            attempts = int(attempts) + 1
            if attempts >= settings.MAX_LOGIN_ATTEMPTS:
                redis_client.setex(f"lockout:{identifier}", settings.LOCKOUT_DURATION_MINUTES * 60, "1")
            redis_client.setex(key, settings.LOCKOUT_DURATION_MINUTES * 60, attempts)
    
    @staticmethod
    def clear_failed_attempts(identifier: str):
        """Clear failed login attempts on successful login"""
        redis_client.delete(f"login_attempts:{identifier}")
    
    @staticmethod
    def is_locked_out(identifier: str) -> bool:
        """Check if account is locked out"""
        return redis_client.exists(f"lockout:{identifier}") > 0

# Dependency for getting current user
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    
    # Check if token is blacklisted
    if SecurityManager.is_token_blacklisted(token):
        raise HTTPException(status_code=401, detail="Token has been revoked")
    
    # Verify token
    payload = SecurityManager.verify_token(token)
    user_id = payload.get("sub")
    
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Get user from database (implement based on your user model)
    # user = get_user_by_id(user_id)
    # if user is None:
    #     raise HTTPException(status_code=401, detail="User not found")
    
    return {"user_id": user_id, "email": payload.get("email")}

# Rate limiting dependency
async def rate_limit_dependency(request: Request):
    client_ip = request.client.host
    RateLimiter.check_rate_limit(request, client_ip, settings.RATE_LIMIT_PER_MINUTE)
    return True