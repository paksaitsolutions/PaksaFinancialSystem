"""
MFA schemas.
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

class MFADeviceBase(BaseModel):
    """Base MFA device schema."""
    device_name: str
    device_type: str  # totp, sms, email
    phone_number: Optional[str] = None
    email: Optional[str] = None

class MFADeviceCreate(MFADeviceBase):
    """Create MFA device schema."""
    pass

class MFADeviceResponse(MFADeviceBase):
    """MFA device response schema."""
    id: UUID
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_used: Optional[datetime] = None

    class Config:
        orm_mode = True

class MFASetupRequest(BaseModel):
    """MFA setup request."""
    device_type: str
    device_name: str
    phone_number: Optional[str] = None
    email: Optional[str] = None

class MFASetupResponse(BaseModel):
    """MFA setup response."""
    device_id: UUID
    secret_key: Optional[str] = None  # For TOTP
    qr_code: Optional[str] = None  # Base64 QR code
    backup_codes: List[str]

class MFAVerifyRequest(BaseModel):
    """MFA verification request."""
    device_id: UUID
    code: str

class MFALoginRequest(BaseModel):
    """MFA login request."""
    user_id: UUID
    code: str
    device_type: Optional[str] = None

class MFAStatusResponse(BaseModel):
    """MFA status response."""
    is_enabled: bool
    devices: List[MFADeviceResponse]
    backup_codes_remaining: int