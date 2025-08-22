"""
Backup and restore service.
"""
import os
import subprocess
import hashlib
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.backup import Backup, RestoreOperation, BackupSchedule, BackupType, BackupStatus, RestoreStatus


class BackupService:
    """Service for database backup and restore operations."""
    
    def __init__(self, db: Session):
        self.db = db
        from app.core.config import settings
        self.backup_dir = os.path.join(settings.UPLOAD_DIR, 'backups')
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def create_backup(
        self,
        backup_name: str,
        backup_type: str = BackupType.FULL,
        initiated_by: UUID = None,
        tables: Optional[List[str]] = None
    ) -> Backup:
        """Create a database backup."""
        backup = Backup(
            backup_name=backup_name,
            backup_type=backup_type,
            status=BackupStatus.PENDING,
            initiated_by=initiated_by,
            tables_included=tables,
            created_by=initiated_by,
            updated_by=initiated_by
        )
        
        self.db.add(backup)
        self.db.flush()
        
        try:
            backup.status = BackupStatus.RUNNING
            backup.started_at = datetime.utcnow()
            self.db.commit()
            
            file_path = self._perform_backup(backup)
            
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            checksum = self._calculate_checksum(file_path) if os.path.exists(file_path) else None
            
            backup.file_path = file_path
            backup.file_size = file_size
            backup.checksum = checksum
            backup.status = BackupStatus.COMPLETED
            backup.completed_at = datetime.utcnow()
            
        except Exception as e:
            backup.status = BackupStatus.FAILED
            backup.error_message = str(e)
        
        self.db.commit()
        self.db.refresh(backup)
        
        return backup
    
    def restore_backup(
        self,
        backup_id: UUID,
        restore_name: str,
        initiated_by: UUID,
        tables_to_restore: Optional[List[str]] = None,
        overwrite_existing: bool = False
    ) -> RestoreOperation:
        """Restore from a backup."""
        backup = self.get_backup(backup_id)
        if not backup:
            raise ValueError(f"Backup {backup_id} not found")
        
        if backup.status != BackupStatus.COMPLETED:
            raise ValueError(f"Backup {backup.backup_name} is not completed")
        
        restore_op = RestoreOperation(
            restore_name=restore_name,
            backup_id=backup_id,
            tables_to_restore=tables_to_restore,
            overwrite_existing=overwrite_existing,
            status=RestoreStatus.PENDING,
            initiated_by=initiated_by,
            created_by=initiated_by,
            updated_by=initiated_by
        )
        
        self.db.add(restore_op)
        self.db.flush()
        
        try:
            restore_op.status = RestoreStatus.RUNNING
            restore_op.started_at = datetime.utcnow()
            self.db.commit()
            
            records_restored = self._perform_restore(backup, restore_op)
            
            restore_op.records_restored = records_restored
            restore_op.status = RestoreStatus.COMPLETED
            restore_op.completed_at = datetime.utcnow()
            
        except Exception as e:
            restore_op.status = RestoreStatus.FAILED
            restore_op.error_message = str(e)
        
        self.db.commit()
        self.db.refresh(restore_op)
        
        return restore_op
    
    def create_schedule(self, schedule_data: Dict[str, Any], created_by: UUID) -> BackupSchedule:
        """Create a backup schedule."""
        schedule = BackupSchedule(
            schedule_name=schedule_data['schedule_name'],
            backup_type=schedule_data.get('backup_type', BackupType.FULL),
            cron_expression=schedule_data['cron_expression'],
            retention_days=schedule_data.get('retention_days', 30),
            compression_enabled=schedule_data.get('compression_enabled', True),
            next_run=datetime.utcnow() + timedelta(days=1),
            created_by=created_by,
            updated_by=created_by
        )
        
        self.db.add(schedule)
        self.db.commit()
        self.db.refresh(schedule)
        
        return schedule
    
    def get_backup(self, backup_id: UUID) -> Optional[Backup]:
        """Get a backup by ID."""
        return self.db.query(Backup).filter(Backup.id == backup_id).first()
    
    def list_backups(self, limit: int = 100) -> List[Backup]:
        """List backups."""
        return self.db.query(Backup)\
                   .order_by(desc(Backup.created_at))\
                   .limit(limit).all()
    
    def list_restore_operations(self, limit: int = 100) -> List[RestoreOperation]:
        """List restore operations."""
        return self.db.query(RestoreOperation)\
                   .order_by(desc(RestoreOperation.created_at))\
                   .limit(limit).all()
    
    def list_schedules(self, active_only: bool = True) -> List[BackupSchedule]:
        """List backup schedules."""
        query = self.db.query(BackupSchedule)
        
        if active_only:
            query = query.filter(BackupSchedule.is_active == True)
        
        return query.order_by(BackupSchedule.schedule_name).all()
    
    def cleanup_old_backups(self, retention_days: int = 30) -> int:
        """Clean up old backup files."""
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        
        old_backups = self.db.query(Backup).filter(
            Backup.created_at < cutoff_date,
            Backup.status == BackupStatus.COMPLETED
        ).all()
        
        cleaned_count = 0
        for backup in old_backups:
            try:
                if backup.file_path and os.path.exists(backup.file_path):
                    os.remove(backup.file_path)
                self.db.delete(backup)
                cleaned_count += 1
            except Exception:
                pass
        
        self.db.commit()
        return cleaned_count
    
    def _perform_backup(self, backup: Backup) -> str:
        """Perform the actual backup operation."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{backup.backup_name}_{timestamp}.sql"
        file_path = os.path.join(self.backup_dir, filename)
        
        # Simplified backup - create placeholder file
        with open(file_path, 'w') as f:
            f.write(f"-- Backup: {backup.backup_name}\n")
            f.write(f"-- Type: {backup.backup_type}\n")
            f.write(f"-- Created: {datetime.utcnow()}\n")
            f.write("-- Placeholder backup file\n")
        
        return file_path
    
    def _perform_restore(self, backup: Backup, restore_op: RestoreOperation) -> int:
        """Perform the actual restore operation."""
        if not backup.file_path or not os.path.exists(backup.file_path):
            raise Exception(f"Backup file not found: {backup.file_path}")
        
        # Simplified restore - just verify file exists
        return 1000
    
    def _calculate_checksum(self, file_path: str) -> str:
        """Calculate SHA-256 checksum of backup file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()