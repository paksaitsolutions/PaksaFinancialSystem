"""
Security utilities for authentication and authorization.
"""
from datetime import datetime, timedelta
from typing import Any, Union, Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    """Create JWT access token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=getattr(settings, 'ACCESS_TOKEN_EXPIRE_MINUTES', 30)
        )
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, 
        getattr(settings, 'SECRET_KEY', 'dev-secret-key'), 
        algorithm=getattr(settings, 'ALGORITHM', 'HS256')
    )
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)

def verify_token(token: str) -> Optional[str]:
    """Verify JWT token and return subject."""
    try:
        payload = jwt.decode(
            token, 
            getattr(settings, 'SECRET_KEY', 'dev-secret-key'), 
            algorithms=[getattr(settings, 'ALGORITHM', 'HS256')]
        )
        return payload.get("sub")
    except JWTError:
        return None