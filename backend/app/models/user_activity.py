"""
User activity and login history models.
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, String, DateTime, Boolean, Text, JSON, Integer
from sqlalchemy.orm import relationship

from .base import BaseModel


class ActivityType(str, Enum):
    LOGIN = "login"
    LOGOUT = "logout"
    PASSWORD_CHANGE = "password_change"
    PROFILE_UPDATE = "profile_update"
    PERMISSION_CHANGE = "permission_change"
    DATA_ACCESS = "data_access"
    DATA_MODIFY = "data_modify"
    SYSTEM_ACTION = "system_action"


class LoginHistory(BaseModel):
    """
    User login history with company context.
    """
    __tablename__ = "login_history"
    
    user_id = Column(String, nullable=False, index=True)
    company_id = Column(String, nullable=False, index=True)
    
    # Login details
    login_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    logout_time = Column(DateTime, nullable=True)
    session_duration = Column(Integer, nullable=True)  # in seconds
    
    # Authentication method
    login_method = Column(String(50), nullable=False, default="email_password")
    success = Column(Boolean, nullable=False, default=True)
    failure_reason = Column(String(200), nullable=True)
    
    # Session details
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    location = Column(String(200), nullable=True)
    device_type = Column(String(50), nullable=True)
    
    def __repr__(self) -> str:
        return f"<LoginHistory(user_id={self.user_id}, company_id={self.company_id}, success={self.success})>"


class UserActivity(BaseModel):
    """
    User activity logs with company context.
    """
    __tablename__ = "user_activities"
    
    user_id = Column(String, nullable=False, index=True)
    company_id = Column(String, nullable=False, index=True)
    
    # Activity details
    activity_type = Column(String(50), nullable=False)
    action = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Resource details
    resource_type = Column(String(100), nullable=True)
    resource_id = Column(String, nullable=True)
    
    # Request details
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    request_method = Column(String(10), nullable=True)
    request_path = Column(String(500), nullable=True)
    
    # Additional data
    meta_data = Column(JSON, nullable=True)
    
    def __repr__(self) -> str:
        return f"<UserActivity(user_id={self.user_id}, action='{self.action}')>"


class CompanyPasswordPolicy(BaseModel):
    """
    Company-specific password policies.
    """
    __tablename__ = "company_password_policies"
    
    company_id = Column(String, nullable=False, unique=True, index=True)
    
    # Password requirements
    min_length = Column(Integer, nullable=False, default=8)
    max_length = Column(Integer, nullable=False, default=128)
    require_uppercase = Column(Boolean, nullable=False, default=True)
    require_lowercase = Column(Boolean, nullable=False, default=True)
    require_numbers = Column(Boolean, nullable=False, default=True)
    require_special_chars = Column(Boolean, nullable=False, default=True)
    
    # Password history
    password_history_count = Column(Integer, nullable=False, default=5)
    password_expiry_days = Column(Integer, nullable=False, default=90)
    
    # Account lockout
    max_failed_attempts = Column(Integer, nullable=False, default=5)
    lockout_duration_minutes = Column(Integer, nullable=False, default=30)
    
    # Reset policies
    reset_token_expiry_hours = Column(Integer, nullable=False, default=24)
    require_security_questions = Column(Boolean, nullable=False, default=False)
    
    def __repr__(self) -> str:
        return f"<CompanyPasswordPolicy(company_id={self.company_id})>"


class CrossCompanyAccess(BaseModel):
    """
    Cross-company user access for service providers.
    """
    __tablename__ = "cross_company_access"
    
    user_id = Column(String, nullable=False, index=True)
    source_company_id = Column(String, nullable=False, index=True)
    target_company_id = Column(String, nullable=False, index=True)
    
    # Access details
    access_type = Column(String(50), nullable=False, default="read_only")
    permissions = Column(JSON, nullable=True)
    
    # Access control
    is_active = Column(Boolean, nullable=False, default=True)
    expires_at = Column(DateTime, nullable=True)
    
    # Approval
    approved_by = Column(String, nullable=False)
    approval_reason = Column(Text, nullable=True)
    
    def __repr__(self) -> str:
        return f"<CrossCompanyAccess(user_id={self.user_id}, target_company={self.target_company_id})>"


class UserSessionActivity(BaseModel):
    """
    Detailed user session activity tracking.
    """
    __tablename__ = "user_session_activities"
    
    session_id = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    company_id = Column(String, nullable=False, index=True)
    
    # Activity details
    activity_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    page_url = Column(String(500), nullable=True)
    action_taken = Column(String(200), nullable=True)
    
    # Performance metrics
    response_time_ms = Column(Integer, nullable=True)
    
    def __repr__(self) -> str:
        return f"<UserSessionActivity(session_id={self.session_id}, action='{self.action_taken}')>"