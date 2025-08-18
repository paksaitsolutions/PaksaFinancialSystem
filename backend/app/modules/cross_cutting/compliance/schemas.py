"""
Paksa Financial System - Compliance & Security Schemas
Version: 1.0.0
Copyright (c) 2025 Paksa IT Solutions. All rights reserved.

This software is the proprietary information of Paksa IT Solutions.
Use is subject to license terms and restrictions.

Pydantic schemas for the Compliance & Security module.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from uuid import UUID

from pydantic import BaseModel, Field, validator, root_validator
from sqlalchemy import JSON

from app.core.schemas import BaseResponse, PaginatedResponse
from .models import (
    AuditActionType, 
    DataSubjectType, 
    DataSubjectRightsRequest as DataSubjectRightsRequestModel,
    SecurityPolicy as SecurityPolicyModel,
    EncryptionKey as EncryptionKeyModel,
    SecurityEvent as SecurityEventModel
)

# Base schemas for common fields
class AuditLogBase(BaseModel):
    """Base schema for audit log entries"""
    user_id: Optional[UUID] = None
    username: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    action: AuditActionType
    resource_type: str = Field(..., max_length=100)
    resource_id: Optional[str] = Field(None, max_length=100)
    status_code: Optional[int] = None
    details: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True
        use_enum_values = True


class AuditLogCreate(AuditLogBase):
    """Schema for creating a new audit log entry"""
    pass


class AuditLogResponse(AuditLogBase, BaseResponse):
    """Schema for audit log responses"""
    id: UUID
    timestamp: datetime
    created_at: datetime
    updated_at: datetime


class AuditLogList(PaginatedResponse):
    """Paginated list of audit logs"""
    items: List[AuditLogResponse] = []


class DataSubjectRightsRequestBase(BaseModel):
    """Base schema for data subject rights requests"""
    request_type: DataSubjectRightsRequestModel.RequestType
    subject_type: DataSubjectType
    subject_name: str = Field(..., max_length=255)
    subject_email: str = Field(..., max_length=255)
    subject_phone: Optional[str] = Field(None, max_length=50)
    subject_address: Optional[str] = None
    description: Optional[str] = None
    requested_data: Optional[Dict[str, Any]] = None
    due_date: Optional[datetime] = None

    class Config:
        from_attributes = True
        use_enum_values = True


class DataSubjectRightsRequestCreate(DataSubjectRightsRequestBase):
    """Schema for creating a new data subject rights request"""
    pass


class DataSubjectRightsRequestUpdate(BaseModel):
    """Schema for updating a data subject rights request"""
    status: Optional[DataSubjectRightsRequestModel.RequestStatus] = None
    assigned_to: Optional[UUID] = None
    due_date: Optional[datetime] = None
    verification_method: Optional[str] = None
    verification_notes: Optional[str] = None
    response_notes: Optional[str] = None
    response_data: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True
        use_enum_values = True


class DataSubjectRightsRequestResponse(DataSubjectRightsRequestBase, BaseResponse):
    """Schema for data subject rights request responses"""
    id: UUID
    status: DataSubjectRightsRequestModel.RequestStatus
    assigned_to: Optional[UUID] = None
    completed_at: Optional[datetime] = None
    verification_method: Optional[str] = None
    verification_notes: Optional[str] = None
    response_notes: Optional[str] = None
    response_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None


class DataSubjectRightsRequestList(PaginatedResponse):
    """Paginated list of data subject rights requests"""
    items: List[DataSubjectRightsRequestResponse] = []


class SecurityPolicyBase(BaseModel):
    """Base schema for security policies"""
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    is_enabled: bool = True
    config: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True


class SecurityPolicyCreate(SecurityPolicyBase):
    """Schema for creating a new security policy"""
    pass


class SecurityPolicyUpdate(BaseModel):
    """Schema for updating a security policy"""
    description: Optional[str] = None
    is_enabled: Optional[bool] = None
    config: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class SecurityPolicyResponse(SecurityPolicyBase, BaseResponse):
    """Schema for security policy responses"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None


class SecurityPolicyList(PaginatedResponse):
    """Paginated list of security policies"""
    items: List[SecurityPolicyResponse] = []


class EncryptionKeyBase(BaseModel):
    """Base schema for encryption keys"""
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    key_type: str = Field(..., max_length=50)
    key_version: int = 1
    is_active: bool = True
    rotation_interval_days: int = 90

    class Config:
        from_attributes = True


class EncryptionKeyCreate(EncryptionKeyBase):
    """Schema for creating a new encryption key"""
    key_data: str  # Encrypted key material


class EncryptionKeyUpdate(BaseModel):
    """Schema for updating an encryption key"""
    description: Optional[str] = None
    is_active: Optional[bool] = None
    rotation_interval_days: Optional[int] = None

    class Config:
        from_attributes = True


class EncryptionKeyResponse(EncryptionKeyBase, BaseResponse):
    """Schema for encryption key responses"""
    id: UUID
    last_rotated_at: Optional[datetime] = None
    next_rotation_due: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None


class EncryptionKeyList(PaginatedResponse):
    """Paginated list of encryption keys"""
    items: List[EncryptionKeyResponse] = []


class SecurityEventBase(BaseModel):
    """Base schema for security events"""
    event_type: str = Field(..., max_length=100)
    severity: SecurityEventModel.EventSeverity = SecurityEventModel.EventSeverity.MEDIUM
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    source: Optional[str] = Field(None, max_length=100)
    details: Optional[Dict[str, Any]] = None
    user_id: Optional[UUID] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    class Config:
        from_attributes = True
        use_enum_values = True


class SecurityEventCreate(SecurityEventBase):
    """Schema for creating a new security event"""
    pass


class SecurityEventUpdate(BaseModel):
    """Schema for updating a security event"""
    status: Optional[SecurityEventModel.EventStatus] = None
    assigned_to: Optional[UUID] = None
    resolution_notes: Optional[str] = None

    class Config:
        from_attributes = True
        use_enum_values = True


class SecurityEventResponse(SecurityEventBase, BaseResponse):
    """Schema for security event responses"""
    id: UUID
    status: SecurityEventModel.EventStatus
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[UUID] = None
    resolution_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class SecurityEventList(PaginatedResponse):
    """Paginated list of security events"""
    items: List[SecurityEventResponse] = []


# Additional schemas for specific operations
class DataExportRequest(BaseModel):
    """Schema for data export requests"""
    data_types: List[str] = Field(..., description="List of data types to export")
    format: str = Field("json", description="Export format (json, csv, xml)")
    include_related: bool = Field(True, description="Include related data")
    encryption_key_id: Optional[UUID] = Field(None, description="Optional encryption key ID")


class DataExportResponse(BaseResponse):
    """Schema for data export responses"""
    export_id: UUID
    status: str
    download_url: Optional[str] = None
    expires_at: Optional[datetime] = None


class AuditLogFilter(BaseModel):
    """Schema for filtering audit logs"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    user_id: Optional[UUID] = None
    action: Optional[AuditActionType] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    status_code: Optional[int] = None


class SecurityEventFilter(BaseModel):
    """Schema for filtering security events"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    event_type: Optional[str] = None
    severity: Optional[SecurityEventModel.EventSeverity] = None
    status: Optional[SecurityEventModel.EventStatus] = None
    user_id: Optional[UUID] = None
    ip_address: Optional[str] = None
