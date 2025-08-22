"""
Schemas for multi-tenant authentication.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr


class TenantAuthConfigRequest(BaseModel):
    """Schema for tenant auth configuration request."""
    custom_login_url: Optional[str] = Field(None, description="Custom login URL")
    company_code_required: bool = Field(False, description="Require company code in login")
    session_timeout_minutes: int = Field(30, description="Session timeout in minutes")
    remember_me_enabled: bool = Field(True, description="Enable remember me functionality")
    remember_me_duration_days: int = Field(30, description="Remember me duration in days")
    concurrent_sessions_limit: int = Field(5, description="Concurrent sessions limit")
    password_reset_enabled: bool = Field(True, description="Enable password reset")
    password_reset_expiry_hours: int = Field(24, description="Password reset expiry in hours")
    custom_reset_template: Optional[str] = Field(None, description="Custom reset email template")
    oauth_providers: Optional[Dict[str, Any]] = Field(None, description="OAuth providers config")
    saml_config: Optional[Dict[str, Any]] = Field(None, description="SAML configuration")
    login_logo_url: Optional[str] = Field(None, description="Login page logo URL")
    login_background_url: Optional[str] = Field(None, description="Login page background URL")
    brand_colors: Optional[Dict[str, str]] = Field(None, description="Brand colors")


class TenantAuthConfigResponse(BaseModel):
    """Schema for tenant auth configuration response."""
    id: UUID = Field(..., description="Config ID")
    company_id: UUID = Field(..., description="Company ID")
    custom_login_url: Optional[str] = Field(None, description="Custom login URL")
    company_code_required: bool = Field(..., description="Require company code in login")
    session_timeout_minutes: int = Field(..., description="Session timeout in minutes")
    remember_me_enabled: bool = Field(..., description="Enable remember me functionality")
    remember_me_duration_days: int = Field(..., description="Remember me duration in days")
    concurrent_sessions_limit: int = Field(..., description="Concurrent sessions limit")
    password_reset_enabled: bool = Field(..., description="Enable password reset")
    password_reset_expiry_hours: int = Field(..., description="Password reset expiry in hours")
    custom_reset_template: Optional[str] = Field(None, description="Custom reset email template")
    oauth_providers: Optional[Dict[str, Any]] = Field(None, description="OAuth providers config")
    saml_config: Optional[Dict[str, Any]] = Field(None, description="SAML configuration")
    login_logo_url: Optional[str] = Field(None, description="Login page logo URL")
    login_background_url: Optional[str] = Field(None, description="Login page background URL")
    brand_colors: Optional[Dict[str, str]] = Field(None, description="Brand colors")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        orm_mode = True


class TenantLoginRequest(BaseModel):
    """Schema for tenant login request."""
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., description="User password")
    company_code: Optional[str] = Field(None, description="Company code")
    remember_me: bool = Field(False, description="Remember me option")


class TenantLoginResponse(BaseModel):
    """Schema for tenant login response."""
    access_token: str = Field(..., description="Access token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiry in seconds")
    user_id: UUID = Field(..., description="User ID")
    company_id: UUID = Field(..., description="Company ID")
    company_name: str = Field(..., description="Company name")
    redirect_url: Optional[str] = Field(None, description="Post-login redirect URL")


class TenantSessionResponse(BaseModel):
    """Schema for tenant session response."""
    id: UUID = Field(..., description="Session ID")
    session_token: str = Field(..., description="Session token")
    user_id: UUID = Field(..., description="User ID")
    company_id: UUID = Field(..., description="Company ID")
    login_method: str = Field(..., description="Login method")
    ip_address: Optional[str] = Field(None, description="IP address")
    user_agent: Optional[str] = Field(None, description="User agent")
    expires_at: datetime = Field(..., description="Expiry timestamp")
    last_activity: datetime = Field(..., description="Last activity timestamp")
    remember_me: bool = Field(..., description="Remember me flag")
    status: str = Field(..., description="Session status")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        orm_mode = True


class PasswordResetRequest(BaseModel):
    """Schema for password reset request."""
    email: EmailStr = Field(..., description="User email")
    company_code: Optional[str] = Field(None, description="Company code")


class PasswordResetConfirmRequest(BaseModel):
    """Schema for password reset confirmation."""
    token: str = Field(..., description="Reset token")
    new_password: str = Field(..., description="New password")


class OAuthProviderRequest(BaseModel):
    """Schema for OAuth provider configuration."""
    provider_name: str = Field(..., description="Provider name")
    client_id: str = Field(..., description="OAuth client ID")
    client_secret: str = Field(..., description="OAuth client secret")
    redirect_uri: str = Field(..., description="OAuth redirect URI")
    scopes: Optional[List[str]] = Field(None, description="OAuth scopes")
    is_active: bool = Field(True, description="Is provider active")
    auto_create_users: bool = Field(False, description="Auto-create users")
    default_role: Optional[str] = Field(None, description="Default role for new users")


class OAuthProviderResponse(BaseModel):
    """Schema for OAuth provider response."""
    id: UUID = Field(..., description="Provider ID")
    company_id: UUID = Field(..., description="Company ID")
    provider_name: str = Field(..., description="Provider name")
    client_id: str = Field(..., description="OAuth client ID")
    redirect_uri: str = Field(..., description="OAuth redirect URI")
    scopes: Optional[List[str]] = Field(None, description="OAuth scopes")
    is_active: bool = Field(..., description="Is provider active")
    auto_create_users: bool = Field(..., description="Auto-create users")
    default_role: Optional[str] = Field(None, description="Default role for new users")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        orm_mode = True


class CompanySelectionResponse(BaseModel):
    """Schema for company selection response."""
    companies: List[Dict[str, Any]] = Field(..., description="Available companies")
    default_company_id: Optional[UUID] = Field(None, description="Default company ID")


class LoginAttemptResponse(BaseModel):
    """Schema for login attempt response."""
    id: UUID = Field(..., description="Attempt ID")
    company_id: Optional[UUID] = Field(None, description="Company ID")
    email: str = Field(..., description="Email address")
    success: bool = Field(..., description="Success flag")
    login_method: str = Field(..., description="Login method")
    failure_reason: Optional[str] = Field(None, description="Failure reason")
    ip_address: Optional[str] = Field(None, description="IP address")
    user_agent: Optional[str] = Field(None, description="User agent")
    created_at: datetime = Field(..., description="Attempt timestamp")

    class Config:
        orm_mode = True