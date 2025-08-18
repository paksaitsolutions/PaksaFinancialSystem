"""
Core security and authentication utilities for Paksa Financial System.
"""
from datetime import datetime, timedelta
from typing import Optional, Any, Dict
from uuid import UUID, uuid4

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field

from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Token(BaseModel):
    """JWT token model."""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Token payload data model."""
    username: Optional[str] = None
    user_id: Optional[UUID] = None
    scopes: list[str] = []

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate a password hash."""
    return pwd_context.hash(password)

def create_access_token(
    subject: str, 
    user_id: UUID, 
    expires_delta: Optional[timedelta] = None,
    scopes: Optional[list[str]] = None
) -> str:
    """Create a new JWT access token."""
    scopes = scopes or []
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {
        "sub": subject,
        "user_id": str(user_id),
        "scopes": scopes,
        "exp": expire
    }
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def decode_token(token: str) -> Dict[str, Any]:
    """Decode and verify a JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_aud": False}
        )
        return payload
    except JWTError as e:
        raise ValueError("Invalid authentication credentials") from e

def create_refresh_token(
    subject: str,
    user_id: UUID,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create a refresh token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
    
    to_encode = {
        "sub": subject,
        "user_id": str(user_id),
        "token_type": "refresh",
        "exp": expire
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.REFRESH_SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def verify_refresh_token(token: str) -> Dict[str, Any]:
    """Verify a refresh token and return the payload."""
    try:
        payload = jwt.decode(
            token,
            settings.REFRESH_SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        if payload.get("token_type") != "refresh":
            raise ValueError("Invalid token type")
        return payload
    except JWTError as e:
        raise ValueError("Invalid refresh token") from e

class AuditMixin:
    """Mixin class for audit fields."""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: UUID = Field(..., description="User ID of the creator")
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    updated_by: UUID = Field(..., description="User ID of the last updater")
    is_active: bool = Field(default=True, description="Soft delete flag")

class PermissionMixin:
    """Mixin class for permission checks."""
    @classmethod
    def has_permission(cls, user_roles: list[str], required_permission: str) -> bool:
        """Check if user has the required permission."""
        # This should be implemented based on your permission model
        return required_permission in user_roles

class DataEncryptionMixin:
    """Mixin for field-level encryption."""
    @staticmethod
    def encrypt_field(value: str) -> str:
        """Encrypt a field value."""
        # Implementation depends on your encryption strategy
        # This is a placeholder - use a proper encryption library
        return f"encrypted_{value}"
    
    @staticmethod
    def decrypt_field(encrypted_value: str) -> str:
        """Decrypt a field value."""
        # Implementation depends on your encryption strategy
        # This is a placeholder - use a proper decryption library
        if encrypted_value.startswith("encrypted_"):
            return encrypted_value[10:]
        return encrypted_value
