"""
Schemas for password policy operations.
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, validator


class PasswordPolicyResponse(BaseModel):
    """Schema for password policy response."""
    id: UUID = Field(..., description="Policy ID")
    name: str = Field(..., description="Policy name")
    description: Optional[str] = Field(None, description="Policy description")
    min_length: int = Field(..., description="Minimum password length")
    max_length: int = Field(..., description="Maximum password length")
    require_uppercase: bool = Field(..., description="Require uppercase letters")
    require_lowercase: bool = Field(..., description="Require lowercase letters")
    require_numbers: bool = Field(..., description="Require numbers")
    require_special_chars: bool = Field(..., description="Require special characters")
    password_history_count: int = Field(..., description="Number of passwords to remember")
    password_expiry_days: int = Field(..., description="Password expiry in days")
    max_failed_attempts: int = Field(..., description="Maximum failed login attempts")
    lockout_duration_minutes: int = Field(..., description="Account lockout duration in minutes")
    is_active: bool = Field(..., description="Whether policy is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        orm_mode = True


class PasswordValidationRequest(BaseModel):
    """Schema for password validation request."""
    password: str = Field(..., description="Password to validate")


class PasswordValidationResponse(BaseModel):
    """Schema for password validation response."""
    valid: bool = Field(..., description="Whether password is valid")
    errors: List[str] = Field([], description="Validation errors")
    policy: dict = Field(..., description="Policy requirements")


class PasswordChangeRequest(BaseModel):
    """Schema for password change request."""
    old_password: str = Field(..., description="Current password")
    new_password: str = Field(..., description="New password")

    @validator('new_password')
    def validate_new_password(cls, v, values):
        """Basic validation for new password."""
        if 'old_password' in values and v == values['old_password']:
            raise ValueError("New password must be different from current password")
        return v


class PasswordChangeResponse(BaseModel):
    """Schema for password change response."""
    success: bool = Field(..., description="Whether password change was successful")
    message: str = Field(..., description="Response message")


class AccountLockStatus(BaseModel):
    """Schema for account lock status."""
    locked: bool = Field(..., description="Whether account is locked")
    failed_attempts: int = Field(..., description="Number of failed attempts")
    max_attempts: int = Field(..., description="Maximum allowed attempts")
    unlock_time: Optional[datetime] = Field(None, description="When account will be unlocked")
    remaining_attempts: int = Field(..., description="Remaining attempts before lockout")


class PasswordExpiryStatus(BaseModel):
    """Schema for password expiry status."""
    expired: bool = Field(..., description="Whether password has expired")
    expires_at: Optional[datetime] = Field(None, description="When password expires")
    days_until_expiry: Optional[int] = Field(None, description="Days until password expires")