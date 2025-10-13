"""
User model for authentication and authorization.
"""
from typing import TYPE_CHECKING
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey
from app.models.base import GUID
from sqlalchemy.orm import Session, relationship
from sqlalchemy import select
from datetime import datetime
import uuid
from app.core.database import Base
from app.core.security import verify_password

if TYPE_CHECKING:
    from .role import Role
    from .core_models import Company
    from .notification import Notification

class User(Base):
    """User model."""
    
    __tablename__ = "users"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Note: Company and Role relationships accessed via foreign keys to avoid circular imports
    
    # Note: Role relationship is defined in Role model to avoid circular imports
    
    # Relationships
    notifications = relationship("Notification", back_populates="user")
    
    @classmethod
    def authenticate(cls, db: Session, email: str, password: str):
        """Authenticate user by email and password."""
        user = db.query(cls).filter(
            cls.email == email,
            cls.is_active == True
        ).first()

        if user and verify_password(password, user.hashed_password):
            # Update last login
            user.last_login = datetime.utcnow()
            db.commit()
            return user

        return None
    
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        return f"{self.first_name or ''} {self.last_name or ''}".strip()
    
    def get_context(self):
        """Get user's basic context."""
        return {
            'user_id': str(self.id),
            'email': self.email,
            'full_name': self.full_name,
            'is_superuser': self.is_superuser,
            'is_active': self.is_active
        }
    
    def __repr__(self):
        return f"<User {self.email}>"

class MFADevice(Base):
    """Multi-factor authentication device model."""
    
    __tablename__ = "mfa_devices"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    device_name = Column(String(100), nullable=False)
    device_type = Column(String(20), nullable=False)  # totp, sms, email
    secret_key = Column(String(255))  # For TOTP
    phone_number = Column(String(20))  # For SMS
    email = Column(String(255))  # For email
    backup_codes = Column(Text)  # JSON array of backup codes
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime)
    
    # Relationships
    user = relationship("User", viewonly=True)
    
    def __repr__(self):
        return f"<MFADevice {self.device_name} ({self.device_type})>"

class MFAAttempt(Base):
    """MFA attempt log model."""
    
    __tablename__ = "mfa_attempts"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    device_id = Column(GUID(), ForeignKey("mfa_devices.id"), nullable=False)
    attempt_type = Column(String(20), nullable=False)  # totp, sms, email, backup
    code_used = Column(String(10))  # Partial code for logging
    is_successful = Column(Boolean, nullable=False)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", viewonly=True)
    device = relationship("MFADevice", viewonly=True)
    
    def __repr__(self):
        return f"<MFAAttempt {self.attempt_type} {'SUCCESS' if self.is_successful else 'FAILED'}>"