"""
Backup and restore models.
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text, JSON
from sqlalchemy.orm import relationship

from .base import BaseModel, GUID


class BackupType(str, Enum):
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"


class BackupStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class RestoreStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Backup(BaseModel):
    """
    Database backup record.
    """
    __tablename__ = "backups"
    
    # Backup identification
    backup_name = Column(String(200), nullable=False)
    backup_type = Column(String(20), nullable=False, default=BackupType.FULL)
    
    # Backup details
    file_path = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True)
    compression_type = Column(String(20), nullable=True)
    
    # Backup status
    status = Column(String(20), nullable=False, default=BackupStatus.PENDING)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Metadata
    tables_included = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    checksum = Column(String(64), nullable=True)
    
    # User information
    initiated_by = Column(GUID(), nullable=False)
    
    def __repr__(self) -> str:
        return f"<Backup(name='{self.backup_name}', type='{self.backup_type}', status='{self.status}')>"


class RestoreOperation(BaseModel):
    """
    Database restore operation record.
    """
    __tablename__ = "restore_operations"
    
    # Restore identification
    restore_name = Column(String(200), nullable=False)
    backup_id = Column(GUID(), nullable=False)
    
    # Restore options
    restore_point = Column(DateTime, nullable=True)
    tables_to_restore = Column(JSON, nullable=True)
    overwrite_existing = Column(Boolean, nullable=False, default=False)
    
    # Restore status
    status = Column(String(20), nullable=False, default=RestoreStatus.PENDING)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Results
    records_restored = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # User information
    initiated_by = Column(GUID(), nullable=False)
    
    def __repr__(self) -> str:
        return f"<RestoreOperation(name='{self.restore_name}', status='{self.status}')>"


class BackupSchedule(BaseModel):
    """
    Automated backup schedule configuration.
    """
    __tablename__ = "backup_schedules"
    
    # Schedule identification
    schedule_name = Column(String(200), nullable=False)
    backup_type = Column(String(20), nullable=False, default=BackupType.FULL)
    
    # Schedule configuration
    cron_expression = Column(String(100), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Backup settings
    retention_days = Column(Integer, nullable=False, default=30)
    compression_enabled = Column(Boolean, nullable=False, default=True)
    
    # Status
    last_run = Column(DateTime, nullable=True)
    next_run = Column(DateTime, nullable=True)
    
    def __repr__(self) -> str:
        return f"<BackupSchedule(name='{self.schedule_name}', active={self.is_active})>"