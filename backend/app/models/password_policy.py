"""
Password policy models.
"""
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Integer, Text
from sqlalchemy.orm import relationship

from .base import BaseModel, GUID


class PasswordPolicy(BaseModel):
    """
    Password policy configuration.
    """
    __tablename__ = "password_policies"
    
    # Policy name and description
    name = Column(String(100), nullable=False, default="Default Policy")
    description = Column(Text, nullable=True)
    
    # Password requirements
    min_length = Column(Integer, nullable=False, default=8)
    max_length = Column(Integer, nullable=False, default=128)
    require_uppercase = Column(Boolean, nullable=False, default=True)
    require_lowercase = Column(Boolean, nullable=False, default=True)
    require_numbers = Column(Boolean, nullable=False, default=True)
    require_special_chars = Column(Boolean, nullable=False, default=True)
    
    # Password history and expiration
    password_history_count = Column(Integer, nullable=False, default=5)
    password_expiry_days = Column(Integer, nullable=False, default=90)
    
    # Account lockout
    max_failed_attempts = Column(Integer, nullable=False, default=5)
    lockout_duration_minutes = Column(Integer, nullable=False, default=30)
    
    # Policy status
    is_active = Column(Boolean, nullable=False, default=True)
    
    def __repr__(self) -> str:
        return f"<PasswordPolicy(name='{self.name}', active={self.is_active})>"


class PasswordHistory(BaseModel):
    """
    Password history for users.
    """
    __tablename__ = "password_history"
    
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="password_history")
    
    def __repr__(self) -> str:
        return f"<PasswordHistory(user_id={self.user_id}, created_at={self.created_at})>"


class LoginAttempt(BaseModel):
    """
    Login attempt tracking for account lockout.
    """
    __tablename__ = "login_attempts"
    
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    success = Column(Boolean, nullable=False)
    attempted_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="login_attempts")
    
    def __repr__(self) -> str:
        return f"<LoginAttempt(user_id={self.user_id}, success={self.success}, attempted_at={self.attempted_at})>"