"""
Schemas for encryption operations.
"""
from typing import Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field


class EncryptedUserProfileResponse(BaseModel):
    """Schema for encrypted user profile response."""
    id: UUID = Field(..., description="Profile ID")
    user_id: str = Field(..., description="User ID")
    ssn: Optional[str] = Field(None, description="Social Security Number")
    phone_number: Optional[str] = Field(None, description="Phone number")
    address_line1: Optional[str] = Field(None, description="Address line 1")
    address_line2: Optional[str] = Field(None, description="Address line 2")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State")
    zip_code: Optional[str] = Field(None, description="ZIP code")
    bank_account_number: Optional[str] = Field(None, description="Bank account number")
    routing_number: Optional[str] = Field(None, description="Routing number")
    tax_id: Optional[str] = Field(None, description="Tax ID")
    emergency_contact_name: Optional[str] = Field(None, description="Emergency contact name")
    emergency_contact_phone: Optional[str] = Field(None, description="Emergency contact phone")

    class Config:
        orm_mode = True


class EncryptedUserProfileCreate(BaseModel):
    """Schema for creating encrypted user profile."""
    ssn: Optional[str] = Field(None, description="Social Security Number")
    phone_number: Optional[str] = Field(None, description="Phone number")
    address_line1: Optional[str] = Field(None, description="Address line 1")
    address_line2: Optional[str] = Field(None, description="Address line 2")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State")
    zip_code: Optional[str] = Field(None, description="ZIP code")
    bank_account_number: Optional[str] = Field(None, description="Bank account number")
    routing_number: Optional[str] = Field(None, description="Routing number")
    tax_id: Optional[str] = Field(None, description="Tax ID")
    emergency_contact_name: Optional[str] = Field(None, description="Emergency contact name")
    emergency_contact_phone: Optional[str] = Field(None, description="Emergency contact phone")


class EncryptionStatusResponse(BaseModel):
    """Schema for encryption status response."""
    encryption_enabled: bool = Field(..., description="Whether encryption is enabled")
    key_configured: bool = Field(..., description="Whether encryption key is configured")
    encrypted_user_profiles: int = Field(..., description="Number of encrypted user profiles")
    encryption_algorithm: str = Field(..., description="Encryption algorithm used")
    key_derivation: str = Field(..., description="Key derivation method")


class EncryptDataRequest(BaseModel):
    """Schema for data encryption request."""
    data: str = Field(..., description="Data to encrypt")


class EncryptDataResponse(BaseModel):
    """Schema for data encryption response."""
    encrypted_data: str = Field(..., description="Encrypted data")


class DecryptDataRequest(BaseModel):
    """Schema for data decryption request."""
    encrypted_data: str = Field(..., description="Encrypted data to decrypt")


class DecryptDataResponse(BaseModel):
    """Schema for data decryption response."""
    decrypted_data: str = Field(..., description="Decrypted data")