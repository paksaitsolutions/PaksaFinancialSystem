"""
Enhanced user model with encrypted sensitive fields.
"""
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.orm import relationship

from .base import BaseModel
from .encrypted_fields import EncryptedString


class EncryptedUserProfile(BaseModel):
    """User profile with encrypted sensitive information."""
    __tablename__ = "encrypted_user_profiles"
    
    # Basic information (not encrypted)
    user_id = Column(String(36), unique=True, nullable=False, index=True)
    
    # Encrypted sensitive fields
    ssn = Column(EncryptedString(20), nullable=True)
    phone_number = Column(EncryptedString(20), nullable=True)
    address_line1 = Column(EncryptedString(200), nullable=True)
    address_line2 = Column(EncryptedString(200), nullable=True)
    city = Column(EncryptedString(100), nullable=True)
    state = Column(EncryptedString(50), nullable=True)
    zip_code = Column(EncryptedString(20), nullable=True)
    
    # Financial information (encrypted)
    bank_account_number = Column(EncryptedString(50), nullable=True)
    routing_number = Column(EncryptedString(20), nullable=True)
    tax_id = Column(EncryptedString(20), nullable=True)
    
    # Emergency contact (encrypted)
    emergency_contact_name = Column(EncryptedString(100), nullable=True)
    emergency_contact_phone = Column(EncryptedString(20), nullable=True)
    
    def __repr__(self) -> str:
        return f"<EncryptedUserProfile(user_id='{self.user_id}')>"