"""
Paksa Financial System - Compliance & Security Models
Version: 1.0.0
Copyright (c) 2025 Paksa IT Solutions. All rights reserved.

This software is the proprietary information of Paksa IT Solutions.
Use is subject to license terms and restrictions.

Database models for the Compliance & Security module.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Boolean, Integer, JSON, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import relationship, backref

<<<<<<< HEAD
from app.core.database import Base
=======
from app.core.db.base import Base
>>>>>>> e96df7278ce4216131b6c65d411c0723f4de7f91


class AuditActionType(str, Enum):
    """Types of audit actions"""
    CREATE = 'create'
    READ = 'read'
    UPDATE = 'update'
    DELETE = 'delete'
    LOGIN = 'login'
    LOGOUT = 'logout'
    PASSWORD_CHANGE = 'password_change'
    PERMISSION_CHANGE = 'permission_change'
    DATA_EXPORT = 'data_export'
    DATA_ACCESS = 'data_access'
    CONFIG_CHANGE = 'config_change'
    SECURITY_EVENT = 'security_event'


class AuditLog(Base):
    """Audit log for tracking all significant system events"""
    __tablename__ = 'audit_logs'
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    user_id = Column(PG_UUID(as_uuid=True), index=True, nullable=True)  # Null for system events
    username = Column(String(255), index=True, nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 can be up to 45 chars
    user_agent = Column(Text, nullable=True)
    action = Column(SQLEnum(AuditActionType), nullable=False, index=True)
    resource_type = Column(String(100), index=True, nullable=False)  # e.g., 'user', 'account', 'transaction'
    resource_id = Column(String(100), index=True, nullable=True)  # ID of the affected resource
    status_code = Column(Integer, nullable=True)  # HTTP status code if applicable
    details = Column(JSONB, nullable=True)  # Additional context about the event
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class DataSubjectType(str, Enum):
    """Types of data subjects under GDPR/CCPA"""
    CUSTOMER = 'customer'
    EMPLOYEE = 'employee'
    VENDOR = 'vendor'
    USER = 'user'
    OTHER = 'other'


class DataSubjectRightsRequest(Base):
    """Track data subject rights requests (GDPR/CCPA)"""
    __tablename__ = 'data_subject_rights_requests'
    
    class RequestType(str, Enum):
        ACCESS = 'access'
        RECTIFICATION = 'rectification'
        ERASURE = 'erasure'
        RESTRICTION = 'restriction'
        PORTABILITY = 'portability'
        OBJECTION = 'objection'
        WITHDRAW_CONSENT = 'withdraw_consent'
    
    class RequestStatus(str, Enum):
        PENDING = 'pending'
        IN_PROGRESS = 'in_progress'
        COMPLETED = 'completed'
        REJECTED = 'rejected'
        CANCELLED = 'cancelled'
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    request_type = Column(SQLEnum(RequestType), nullable=False, index=True)
    status = Column(SQLEnum(RequestStatus), default=RequestStatus.PENDING, nullable=False, index=True)
    
    # Data subject information
    subject_type = Column(SQLEnum(DataSubjectType), nullable=False, index=True)
    subject_name = Column(String(255), nullable=False)
    subject_email = Column(String(255), nullable=False, index=True)
    subject_phone = Column(String(50), nullable=True)
    subject_address = Column(Text, nullable=True)
    
    # Request details
    description = Column(Text, nullable=True)
    requested_data = Column(JSONB, nullable=True)  # Specific data being requested
    
    # Processing information
    assigned_to = Column(PG_UUID(as_uuid=True), nullable=True)  # User ID
    due_date = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Verification
    verification_method = Column(String(100), nullable=True)  # How the subject was verified
    verification_notes = Column(Text, nullable=True)
    
    # Response
    response_notes = Column(Text, nullable=True)
    response_data = Column(JSONB, nullable=True)  # Any data provided in response
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(PG_UUID(as_uuid=True), nullable=True)  # User who created the request (if different from subject)
    
    # Relationships
    audit_logs = relationship('AuditLog', 
                             primaryjoin=f"AuditLog.resource_id == cast(foreign(DataSubjectRightsRequest.id) as String)",
                             viewonly=True)


class SecurityPolicy(Base):
    """System security policies and configurations"""
    __tablename__ = 'security_policies'
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_enabled = Column(Boolean, default=True, nullable=False, index=True)
    config = Column(JSONB, nullable=False, default=dict)  # Policy-specific configuration
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(PG_UUID(as_uuid=True), nullable=True)
    updated_by = Column(PG_UUID(as_uuid=True), nullable=True)


class EncryptionKey(Base):
    """Encryption keys for data at rest"""
    __tablename__ = 'encryption_keys'
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    key_type = Column(String(50), nullable=False, index=True)  # e.g., 'aes-256', 'rsa-4096'
    key_data = Column(Text, nullable=False)  # Encrypted key material
    key_version = Column(Integer, default=1, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Key rotation
    rotation_interval_days = Column(Integer, default=90, nullable=False)
    last_rotated_at = Column(DateTime, nullable=True)
    next_rotation_due = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(PG_UUID(as_uuid=True), nullable=True)


class SecurityEvent(Base):
    """Security-related events and alerts"""
    __tablename__ = 'security_events'
    
    class EventSeverity(str, Enum):
        INFO = 'info'
        LOW = 'low'
        MEDIUM = 'medium'
        HIGH = 'high'
        CRITICAL = 'critical'
    
    class EventStatus(str, Enum):
        OPEN = 'open'
        INVESTIGATING = 'investigating'
        RESOLVED = 'resolved'
        FALSE_POSITIVE = 'false_positive'
        IGNORED = 'ignored'
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    event_type = Column(String(100), nullable=False, index=True)  # e.g., 'failed_login', 'brute_force', 'suspicious_activity'
    severity = Column(SQLEnum(EventSeverity), default=EventSeverity.MEDIUM, nullable=False, index=True)
    status = Column(SQLEnum(EventStatus), default=EventStatus.OPEN, nullable=False, index=True)
    
    # Event details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    source = Column(String(100), nullable=True)  # What system/component generated this event
    details = Column(JSONB, nullable=True)  # Raw event data
    
    # Related entities
    user_id = Column(PG_UUID(as_uuid=True), nullable=True, index=True)
    ip_address = Column(String(45), nullable=True, index=True)
    user_agent = Column(Text, nullable=True)
    
    # Resolution
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(PG_UUID(as_uuid=True), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
