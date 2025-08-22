"""
Session management models.
"""
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Text, Integer
from sqlalchemy.orm import relationship

from .base import BaseModel, GUID


class SessionStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"


class UserSession(BaseModel):
    """
    User session tracking.
    """
    __tablename__ = "user_sessions"
    
    # Session identification
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    # Tenant context
    company_id = Column(GUID(), ForeignKey("companies.id"), nullable=False, index=True)
    
    # Session details
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    device_info = Column(Text, nullable=True)
    
    # Session timing
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_activity = Column(DateTime, nullable=False, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    
    # Session status
    status = Column(String(20), nullable=False, default=SessionStatus.ACTIVE)
    terminated_at = Column(DateTime, nullable=True)
    termination_reason = Column(String(100), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    def __repr__(self) -> str:
        return f"<UserSession(id={self.id}, user_id={self.user_id}, status='{self.status}')>"
    
    def is_expired(self) -> bool:
        """Check if session is expired."""
        return datetime.utcnow() > self.expires_at
    
    def is_active(self) -> bool:
        """Check if session is active."""
        return self.status == SessionStatus.ACTIVE and not self.is_expired()
    
    def extend_session(self, duration_minutes: int = 30):
        """Extend session expiration."""
        self.expires_at = datetime.utcnow() + timedelta(minutes=duration_minutes)
        self.last_activity = datetime.utcnow()


class SessionConfig(BaseModel):
    """
    Session configuration settings.
    """
    __tablename__ = "session_configs"
    
    # Configuration name
    name = Column(String(100), nullable=False, default="Default Session Config")
    description = Column(Text, nullable=True)
    
    # Session settings
    session_timeout_minutes = Column(Integer, nullable=False, default=30)
    max_concurrent_sessions = Column(Integer, nullable=False, default=3)
    remember_me_duration_days = Column(Integer, nullable=False, default=30)
    
    # Security settings
    require_fresh_login_minutes = Column(Integer, nullable=False, default=60)
    auto_logout_on_idle = Column(Boolean, nullable=False, default=True)
    
    # Configuration status
    is_active = Column(Boolean, nullable=False, default=True)
    
    def __repr__(self) -> str:
        return f"<SessionConfig(name='{self.name}', active={self.is_active})>"