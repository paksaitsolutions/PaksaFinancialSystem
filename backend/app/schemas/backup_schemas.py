"""
Schemas for backup and restore operations.
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field


class BackupRequest(BaseModel):
    """Schema for backup creation request."""
    backup_name: str = Field(..., description="Backup name")
    backup_type: str = Field("full", description="Backup type")
    tables: Optional[List[str]] = Field(None, description="Tables to backup")


class BackupResponse(BaseModel):
    """Schema for backup response."""
    id: UUID = Field(..., description="Backup ID")
    backup_name: str = Field(..., description="Backup name")
    backup_type: str = Field(..., description="Backup type")
    file_path: Optional[str] = Field(None, description="Backup file path")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    compression_type: Optional[str] = Field(None, description="Compression type")
    status: str = Field(..., description="Backup status")
    started_at: Optional[datetime] = Field(None, description="Start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    tables_included: Optional[List[str]] = Field(None, description="Tables included")
    error_message: Optional[str] = Field(None, description="Error message")
    checksum: Optional[str] = Field(None, description="File checksum")
    initiated_by: UUID = Field(..., description="User who initiated backup")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        orm_mode = True


class RestoreRequest(BaseModel):
    """Schema for restore operation request."""
    restore_name: str = Field(..., description="Restore operation name")
    backup_id: UUID = Field(..., description="Backup ID to restore from")
    tables_to_restore: Optional[List[str]] = Field(None, description="Tables to restore")
    overwrite_existing: bool = Field(False, description="Overwrite existing data")


class RestoreResponse(BaseModel):
    """Schema for restore operation response."""
    id: UUID = Field(..., description="Restore operation ID")
    restore_name: str = Field(..., description="Restore operation name")
    backup_id: UUID = Field(..., description="Backup ID")
    restore_point: Optional[datetime] = Field(None, description="Restore point timestamp")
    tables_to_restore: Optional[List[str]] = Field(None, description="Tables to restore")
    overwrite_existing: bool = Field(..., description="Overwrite existing data")
    status: str = Field(..., description="Restore status")
    started_at: Optional[datetime] = Field(None, description="Start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    records_restored: Optional[int] = Field(None, description="Number of records restored")
    error_message: Optional[str] = Field(None, description="Error message")
    initiated_by: UUID = Field(..., description="User who initiated restore")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        orm_mode = True


class BackupScheduleRequest(BaseModel):
    """Schema for backup schedule creation request."""
    schedule_name: str = Field(..., description="Schedule name")
    backup_type: str = Field("full", description="Backup type")
    cron_expression: str = Field(..., description="Cron expression for scheduling")
    retention_days: int = Field(30, description="Backup retention in days")
    compression_enabled: bool = Field(True, description="Enable compression")


class BackupScheduleResponse(BaseModel):
    """Schema for backup schedule response."""
    id: UUID = Field(..., description="Schedule ID")
    schedule_name: str = Field(..., description="Schedule name")
    backup_type: str = Field(..., description="Backup type")
    cron_expression: str = Field(..., description="Cron expression")
    is_active: bool = Field(..., description="Whether schedule is active")
    retention_days: int = Field(..., description="Backup retention in days")
    compression_enabled: bool = Field(..., description="Compression enabled")
    last_run: Optional[datetime] = Field(None, description="Last run timestamp")
    next_run: Optional[datetime] = Field(None, description="Next run timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        orm_mode = True


class BackupDashboardResponse(BaseModel):
    """Schema for backup dashboard data."""
    total_backups: int = Field(..., description="Total number of backups")
    successful_backups: int = Field(..., description="Number of successful backups")
    failed_backups: int = Field(..., description="Number of failed backups")
    total_storage_mb: float = Field(..., description="Total storage used in MB")
    recent_backups: List[BackupResponse] = Field(..., description="Recent backups")
    active_schedules: int = Field(..., description="Number of active schedules")
    last_backup_date: Optional[datetime] = Field(None, description="Last backup date")