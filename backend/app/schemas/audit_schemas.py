"""
Schemas for audit logging operations.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field


class AuditLogResponse(BaseModel):
    """Schema for audit log response."""
    id: UUID = Field(..., description="Audit log ID")
    user_id: Optional[UUID] = Field(None, description="User ID")
    session_id: Optional[UUID] = Field(None, description="Session ID")
    action: str = Field(..., description="Action performed")
    resource_type: str = Field(..., description="Resource type")
    resource_id: Optional[str] = Field(None, description="Resource ID")
    endpoint: Optional[str] = Field(None, description="API endpoint")
    method: Optional[str] = Field(None, description="HTTP method")
    ip_address: Optional[str] = Field(None, description="IP address")
    user_agent: Optional[str] = Field(None, description="User agent")
    old_values: Optional[Dict[str, Any]] = Field(None, description="Old values")
    new_values: Optional[Dict[str, Any]] = Field(None, description="New values")
    description: Optional[str] = Field(None, description="Description")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    timestamp: datetime = Field(..., description="Timestamp")

    class Config:
        orm_mode = True


class AuditLogRequest(BaseModel):
    """Schema for audit log creation request."""
    action: str = Field(..., description="Action performed")
    resource_type: str = Field(..., description="Resource type")
    resource_id: Optional[str] = Field(None, description="Resource ID")
    old_values: Optional[Dict[str, Any]] = Field(None, description="Old values")
    new_values: Optional[Dict[str, Any]] = Field(None, description="New values")
    description: Optional[str] = Field(None, description="Description")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class AuditLogFilter(BaseModel):
    """Schema for audit log filtering."""
    user_id: Optional[UUID] = Field(None, description="Filter by user ID")
    resource_type: Optional[str] = Field(None, description="Filter by resource type")
    action: Optional[str] = Field(None, description="Filter by action")
    start_date: Optional[datetime] = Field(None, description="Start date filter")
    end_date: Optional[datetime] = Field(None, description="End date filter")
    skip: int = Field(0, description="Number of records to skip")
    limit: int = Field(100, description="Maximum number of records to return")


class AuditStatisticsResponse(BaseModel):
    """Schema for audit statistics response."""
    total_logs: int = Field(..., description="Total number of logs")
    active_users: int = Field(..., description="Number of active users")
    actions: Dict[str, int] = Field(..., description="Actions breakdown")
    resources: Dict[str, int] = Field(..., description="Resources breakdown")
    period_days: int = Field(..., description="Period in days")


class AuditConfigResponse(BaseModel):
    """Schema for audit configuration response."""
    id: UUID = Field(..., description="Config ID")
    name: str = Field(..., description="Configuration name")
    description: Optional[str] = Field(None, description="Configuration description")
    log_read_operations: str = Field(..., description="Log read operations setting")
    log_failed_attempts: str = Field(..., description="Log failed attempts setting")
    retention_days: str = Field(..., description="Retention period in days")
    excluded_resources: Optional[List[str]] = Field(None, description="Excluded resources")
    sensitive_resources: Optional[List[str]] = Field(None, description="Sensitive resources")
    is_active: str = Field(..., description="Whether configuration is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        orm_mode = True


class UserActivityResponse(BaseModel):
    """Schema for user activity response."""
    user_id: UUID = Field(..., description="User ID")
    logs: List[AuditLogResponse] = Field(..., description="User activity logs")
    total_actions: int = Field(..., description="Total number of actions")
    period_days: int = Field(..., description="Period in days")


class ResourceHistoryResponse(BaseModel):
    """Schema for resource history response."""
    resource_type: str = Field(..., description="Resource type")
    resource_id: str = Field(..., description="Resource ID")
    logs: List[AuditLogResponse] = Field(..., description="Resource history logs")
    total_changes: int = Field(..., description="Total number of changes")