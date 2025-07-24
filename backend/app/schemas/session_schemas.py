"""
Schemas for session management operations.
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field


class SessionResponse(BaseModel):
    """Schema for session response."""
    id: UUID = Field(..., description="Session ID")
    session_token: str = Field(..., description="Session token")
    user_id: UUID = Field(..., description="User ID")
    ip_address: Optional[str] = Field(None, description="IP address")
    user_agent: Optional[str] = Field(None, description="User agent")
    device_info: Optional[str] = Field(None, description="Device information")
    created_at: datetime = Field(..., description="Session creation time")
    last_activity: datetime = Field(..., description="Last activity time")
    expires_at: datetime = Field(..., description="Session expiration time")
    status: str = Field(..., description="Session status")
    terminated_at: Optional[datetime] = Field(None, description="Termination time")
    termination_reason: Optional[str] = Field(None, description="Termination reason")

    class Config:
        orm_mode = True


class SessionValidationResponse(BaseModel):
    """Schema for session validation response."""
    valid: bool = Field(..., description="Whether session is valid")
    reason: Optional[str] = Field(None, description="Validation failure reason")
    user_id: Optional[UUID] = Field(None, description="User ID if valid")
    expires_at: Optional[datetime] = Field(None, description="Session expiration if valid")


class SessionCreateRequest(BaseModel):
    """Schema for session creation request."""
    user_id: UUID = Field(..., description="User ID")
    ip_address: Optional[str] = Field(None, description="IP address")
    user_agent: Optional[str] = Field(None, description="User agent")
    remember_me: bool = Field(False, description="Remember me option")


class SessionExtendRequest(BaseModel):
    """Schema for session extension request."""
    duration_minutes: Optional[int] = Field(None, description="Extension duration in minutes")


class SessionTerminateRequest(BaseModel):
    """Schema for session termination request."""
    reason: str = Field("User logout", description="Termination reason")


class SessionConfigResponse(BaseModel):
    """Schema for session configuration response."""
    id: UUID = Field(..., description="Config ID")
    name: str = Field(..., description="Configuration name")
    description: Optional[str] = Field(None, description="Configuration description")
    session_timeout_minutes: int = Field(..., description="Session timeout in minutes")
    max_concurrent_sessions: int = Field(..., description="Maximum concurrent sessions")
    remember_me_duration_days: int = Field(..., description="Remember me duration in days")
    require_fresh_login_minutes: int = Field(..., description="Fresh login requirement in minutes")
    auto_logout_on_idle: bool = Field(..., description="Auto logout on idle")
    is_active: bool = Field(..., description="Whether configuration is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        orm_mode = True


class UserSessionsResponse(BaseModel):
    """Schema for user sessions response."""
    sessions: List[SessionResponse] = Field(..., description="List of user sessions")
    total_count: int = Field(..., description="Total session count")
    active_count: int = Field(..., description="Active session count")


class SessionStatsResponse(BaseModel):
    """Schema for session statistics response."""
    total_sessions: int = Field(..., description="Total sessions")
    active_sessions: int = Field(..., description="Active sessions")
    expired_sessions: int = Field(..., description="Expired sessions")
    terminated_sessions: int = Field(..., description="Terminated sessions")
    unique_users: int = Field(..., description="Unique users with sessions")