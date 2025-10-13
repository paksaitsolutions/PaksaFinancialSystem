"""
Multi-tenant authentication models.
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, String, DateTime, Boolean, Text, JSON, Integer
from sqlalchemy.orm import relationship

from .base import BaseModel, GUID


class LoginMethod(str, Enum):
    EMAIL_PASSWORD = "email_password"
    OAUTH_GOOGLE = "oauth_google"
    OAUTH_MICROSOFT = "oauth_microsoft"
    SAML_SSO = "saml_sso"


class SessionStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"


class TenantAuthConfig(BaseModel):
    """
    Company-specific authentication configuration.
    """
    __tablename__ = "tenant_auth_configs"
    
    company_id = Column(GUID(), nullable=False, unique=True, index=True)
    
    # Login URL configuration
    custom_login_url = Column(String(255), nullable=True)
    company_code_required = Column(Boolean, nullable=False, default=False)
    
    # Session configuration
    session_timeout_minutes = Column(Integer, nullable=False, default=30)
    remember_me_enabled = Column(Boolean, nullable=False, default=True)
    remember_me_duration_days = Column(Integer, nullable=False, default=30)
    concurrent_sessions_limit = Column(Integer, nullable=False, default=5)
    
    # Password reset configuration
    password_reset_enabled = Column(Boolean, nullable=False, default=True)
    password_reset_expiry_hours = Column(Integer, nullable=False, default=24)
    custom_reset_template = Column(Text, nullable=True)
    
    # OAuth/SSO configuration
    oauth_providers = Column(JSON, nullable=True)
    saml_config = Column(JSON, nullable=True)
    
    # Branding
    login_logo_url = Column(String(500), nullable=True)
    login_background_url = Column(String(500), nullable=True)
    brand_colors = Column(JSON, nullable=True)
    
    def __repr__(self) -> str:
        return f"<TenantAuthConfig(company_id={self.company_id})>"


class TenantSession(BaseModel):
    """
    Multi-tenant user sessions.
    """
    __tablename__ = "tenant_sessions"
    
    # Session identification
    session_token = Column(String(255), nullable=False, unique=True, index=True)
    user_id = Column(GUID(), nullable=False, index=True)
    company_id = Column(GUID(), nullable=False, index=True)
    
    # Session details
    login_method = Column(String(50), nullable=False, default=LoginMethod.EMAIL_PASSWORD)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Session timing
    expires_at = Column(DateTime, nullable=False)
    last_activity = Column(DateTime, nullable=False, default=datetime.utcnow)
    remember_me = Column(Boolean, nullable=False, default=False)
    
    # Session status
    status = Column(String(20), nullable=False, default=SessionStatus.ACTIVE)
    terminated_reason = Column(String(100), nullable=True)
    
    def __repr__(self) -> str:
        return f"<TenantSession(user_id={self.user_id}, company_id={self.company_id})>"


class CompanyLoginAttempt(BaseModel):
    """
    Company-specific login attempts for security monitoring.
    """
    __tablename__ = "company_login_attempts"
    
    # Attempt identification
    company_id = Column(GUID(), nullable=True, index=True)
    email = Column(String(255), nullable=False, index=True)
    
    # Attempt details
    success = Column(Boolean, nullable=False)
    login_method = Column(String(50), nullable=False, default=LoginMethod.EMAIL_PASSWORD)
    failure_reason = Column(String(100), nullable=True)
    
    # Request details
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    def __repr__(self) -> str:
        return f"<CompanyLoginAttempt(email='{self.email}', success={self.success})>"


class PasswordResetToken(BaseModel):
    """
    Company-branded password reset tokens.
    """
    __tablename__ = "password_reset_tokens"
    
    # Token identification
    token = Column(String(255), nullable=False, unique=True, index=True)
    user_id = Column(GUID(), nullable=False, index=True)
    company_id = Column(GUID(), nullable=False, index=True)
    
    # Token details
    email = Column(String(255), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, nullable=False, default=False)
    used_at = Column(DateTime, nullable=True)
    
    def __repr__(self) -> str:
        return f"<PasswordResetToken(email='{self.email}', used={self.used})>"


class OAuthProvider(BaseModel):
    """
    Company-specific OAuth provider configurations.
    """
    __tablename__ = "oauth_providers"
    
    # Provider identification
    company_id = Column(GUID(), nullable=False, index=True)
    provider_name = Column(String(50), nullable=False)
    
    # Provider configuration
    client_id = Column(String(255), nullable=False)
    client_secret = Column(String(500), nullable=False)  # Encrypted
    redirect_uri = Column(String(500), nullable=False)
    scopes = Column(JSON, nullable=True)
    
    # Provider settings
    is_active = Column(Boolean, nullable=False, default=True)
    auto_create_users = Column(Boolean, nullable=False, default=False)
    default_role = Column(String(50), nullable=True)
    
    def __repr__(self) -> str:
        return f"<OAuthProvider(company_id={self.company_id}, provider='{self.provider_name}')>"