"""
MFA (Multi-Factor Authentication) models.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base

class MFADevice(Base):
    """MFA device model."""
    
    __tablename__ = "mfa_device"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    device_name = Column(String(100), nullable=False)
    device_type = Column(String(20), nullable=False)  # totp, sms, email
    secret_key = Column(String(32))  # For TOTP
    phone_number = Column(String(20))  # For SMS
    email = Column(String(100))  # For email
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    backup_codes = Column(String(500))  # JSON backup codes
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime)

class MFAAttempt(Base):
    """MFA attempt tracking."""
    
    __tablename__ = "mfa_attempt"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    device_id = Column(UUID(as_uuid=True), ForeignKey("mfa_device.id"))
    attempt_type = Column(String(20), nullable=False)
    code_used = Column(String(10))
    is_successful = Column(Boolean, default=False)
    ip_address = Column(String(45))
    attempted_at = Column(DateTime, default=datetime.utcnow)
    
    device = relationship("MFADevice")