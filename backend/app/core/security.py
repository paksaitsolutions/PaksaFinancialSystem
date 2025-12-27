from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import json
from app.core.config.settings import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Security
security = HTTPBearer()

# Redis for session management (optional)
try:
    import redis
    if hasattr(settings, 'USE_REDIS') and settings.USE_REDIS and settings.REDIS_URL:
        redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
        REDIS_AVAILABLE = True
    else:
        redis_client = None
        REDIS_AVAILABLE = False
except (ImportError, ValueError):
    redis_client = None
    REDIS_AVAILABLE = False

class SecurityManager:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        # Truncate password to 72 bytes for bcrypt compatibility
        truncated_password = plain_password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
        return pwd_context.verify(truncated_password, hashed_password)
    
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
        if not REDIS_AVAILABLE:
            return
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
        if not REDIS_AVAILABLE:
            return False
        return redis_client.exists(f"blacklist:{token}") > 0

class RateLimiter:
    @staticmethod
    def check_rate_limit(request: Request, identifier: str, limit: int = 60, window: int = 60):
        """Rate limiting implementation"""
        if not REDIS_AVAILABLE:
            return True
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
        if not REDIS_AVAILABLE:
            return
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
        if not REDIS_AVAILABLE:
            return
        redis_client.delete(f"login_attempts:{identifier}")
    
    @staticmethod
    def is_locked_out(identifier: str) -> bool:
        """Check if account is locked out"""
        if not REDIS_AVAILABLE:
            return False
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
    
    return {
        "user_id": user_id, 
        "email": payload.get("email"),
        "tenant_id": payload.get("tenant_id", "demo-tenant-123")
    }

# Dependency for getting current active user
async def get_current_active_user(current_user: dict = Depends(get_current_user)):
    return current_user

# Dependency for getting current superuser
async def get_current_superuser(current_user: dict = Depends(get_current_user)):
    return current_user

# Helper functions for backward compatibility
def create_access_token(subject: str, additional_claims: dict = None):
    data = {"sub": subject}
    if additional_claims:
        data.update(additional_claims)
    return SecurityManager.create_access_token(data)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Truncate password to 72 bytes for bcrypt compatibility
    truncated_password = plain_password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    return SecurityManager.verify_password(truncated_password, hashed_password)

def get_password_hash(password: str) -> str:
    return SecurityManager.get_password_hash(password)

# Rate limiting dependency
async def rate_limit_dependency(request: Request):
    client_ip = request.client.host
    RateLimiter.check_rate_limit(request, client_ip, settings.RATE_LIMIT_PER_MINUTE)
    return True

# Advanced security features
class SecurityAudit:
    @staticmethod
    def log_security_event(event_type: str, user_id: str = None, ip_address: str = None, details: dict = None):
        """Log security events for audit trail"""
        if not REDIS_AVAILABLE:
            return
        
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "ip_address": ip_address,
            "details": details or {}
        }
        
        # Store in Redis with TTL of 30 days
        key = f"security_event:{datetime.utcnow().timestamp()}"
        redis_client.setex(key, 30 * 24 * 60 * 60, json.dumps(event))

class SessionManager:
    @staticmethod
    def create_session(user_id: str, ip_address: str = None, user_agent: str = None) -> str:
        """Create user session"""
        import uuid
        session_id = str(uuid.uuid4())
        
        if REDIS_AVAILABLE:
            session_data = {
                "user_id": user_id,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "created_at": datetime.utcnow().isoformat(),
                "last_activity": datetime.utcnow().isoformat()
            }
            redis_client.setex(f"session:{session_id}", settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60, json.dumps(session_data))
        
        return session_id
    
    @staticmethod
    def validate_session(session_id: str) -> dict:
        """Validate and refresh session"""
        if not REDIS_AVAILABLE:
            return {}
        
        session_data = redis_client.get(f"session:{session_id}")
        if not session_data:
            raise HTTPException(status_code=401, detail="Invalid session")
        
        session = json.loads(session_data)
        session["last_activity"] = datetime.utcnow().isoformat()
        redis_client.setex(f"session:{session_id}", settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60, json.dumps(session))
        
        return session
    
    @staticmethod
    def invalidate_session(session_id: str):
        """Invalidate user session"""
        if REDIS_AVAILABLE:
            redis_client.delete(f"session:{session_id}")

# Enhanced user dependency with session validation
async def get_current_user_with_session(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    
    # Check if token is blacklisted
    if SecurityManager.is_token_blacklisted(token):
        SecurityAudit.log_security_event("TOKEN_BLACKLISTED", details={"token": token[:20] + "..."})
        raise HTTPException(status_code=401, detail="Token has been revoked")
    
    # Verify token
    payload = SecurityManager.verify_token(token)
    user_id = payload.get("sub")
    session_id = payload.get("session_id")
    
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Validate session if session_id is present
    if session_id:
        try:
            SessionManager.validate_session(session_id)
        except HTTPException:
            SecurityAudit.log_security_event("INVALID_SESSION", user_id=user_id, details={"session_id": session_id})
            raise
    
    return {
        "user_id": user_id, 
        "email": payload.get("email"),
        "session_id": session_id,
        "tenant_id": payload.get("tenant_id", "demo-tenant-123")
    }