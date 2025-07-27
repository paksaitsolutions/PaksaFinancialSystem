from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import Boolean, Column, String, DateTime, ForeignKey, Text, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import BaseModel, GUID

class User(BaseModel):
    """User model for authentication and authorization."""
    __tablename__ = "users"
    
    # Basic information
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=True)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    
    # Authentication
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean(), default=True)
    is_verified = Column(Boolean(), default=False)
    is_superuser = Column(Boolean(), default=False)
    
    # Contact information
    phone_number = Column(String(20), nullable=True)
    profile_picture = Column(String(255), nullable=True)
    
    # Timestamps
    last_login = Column(DateTime(timezone=True), nullable=True)
    date_joined = Column(DateTime(timezone=True), server_default=func.now())
    
    # User-specific settings
    preferences = Column(Text, nullable=True)  # JSON string for user preferences
    
    # MFA support
    mfa_enabled = Column(Boolean(), default=False)
    mfa_secret = Column(String(32), nullable=True)  # TOTP secret
    
    # Multi-tenant support
    tenant_id = Column(GUID(), nullable=True, index=True)
    
    @property
    def full_name(self) -> str:
        """Return the full name of the user."""
        return f"{self.first_name or ''} {self.last_name or ''}".strip()
    
    @classmethod
    async def get_by_email(cls, db, email: str) -> Optional['User']:
        """Get a user by email."""
        from sqlalchemy import select
        result = await db.execute(select(cls).where(cls.email == email))
        return result.scalars().first()
    
    @classmethod
    async def get_by_username(cls, db, username: str) -> Optional['User']:
        """Get a user by username."""
        from sqlalchemy import select
        result = await db.execute(select(cls).where(cls.username == username))
        return result.scalars().first()
    
    @classmethod
    async def authenticate(
        cls, 
        db, 
        email: str, 
        password: str
    ) -> Optional['User']:
        """Authenticate a user by email and password."""
        from app.core.security import verify_password
        
        user = await cls.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"