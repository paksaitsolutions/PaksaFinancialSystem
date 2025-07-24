"""
Backup and recovery service.
"""
import os
import subprocess
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer
from app.models.base import BaseModel


class BackupRecord(BaseModel):
    """Backup record entries."""
    __tablename__ = "backup_records"
    
    backup_type = Column(String(50), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)
    status = Column(String(20), nullable=False, default="completed")
    error_message = Column(Text, nullable=True)


class BackupService:
    """Service for backup and recovery operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.backup_dir = "/app/backups"
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def create_database_backup(self) -> BackupRecord:
        """Create a database backup."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_file = f"{self.backup_dir}/db_backup_{timestamp}.sql"
        
        try:
            # PostgreSQL backup command
            cmd = [
                "pg_dump",
                "-h", os.getenv("DB_HOST", "localhost"),
                "-U", os.getenv("DB_USER", "postgres"),
                "-d", os.getenv("DB_NAME", "paksa_financial"),
                "-f", backup_file
            ]
            
            subprocess.run(cmd, check=True, env={
                **os.environ,
                "PGPASSWORD": os.getenv("DB_PASSWORD", "")
            })
            
            file_size = os.path.getsize(backup_file)
            
            backup_record = BackupRecord(
                backup_type="database",
                file_path=backup_file,
                file_size=file_size,
                status="completed"
            )
            
        except Exception as e:
            backup_record = BackupRecord(
                backup_type="database",
                file_path=backup_file,
                status="failed",
                error_message=str(e)
            )
        
        self.db.add(backup_record)
        self.db.commit()
        self.db.refresh(backup_record)
        
        return backup_record
    
    def restore_database_backup(self, backup_file: str) -> bool:
        """Restore database from backup."""
        try:
            cmd = [
                "psql",
                "-h", os.getenv("DB_HOST", "localhost"),
                "-U", os.getenv("DB_USER", "postgres"),
                "-d", os.getenv("DB_NAME", "paksa_financial"),
                "-f", backup_file
            ]
            
            subprocess.run(cmd, check=True, env={
                **os.environ,
                "PGPASSWORD": os.getenv("DB_PASSWORD", "")
            })
            
            return True
            
        except Exception as e:
            print(f"Restore failed: {e}")
            return False
    
    def get_backup_history(self, limit: int = 50) -> List[BackupRecord]:
        """Get backup history."""
        return self.db.query(BackupRecord).order_by(
            BackupRecord.created_at.desc()
        ).limit(limit).all()
    
    def cleanup_old_backups(self, keep_days: int = 30):
        """Clean up old backup files."""
        cutoff_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        cutoff_date = cutoff_date.replace(day=cutoff_date.day - keep_days)
        
        old_backups = self.db.query(BackupRecord).filter(
            BackupRecord.created_at < cutoff_date
        ).all()
        
        for backup in old_backups:
            try:
                if os.path.exists(backup.file_path):
                    os.remove(backup.file_path)
                self.db.delete(backup)
            except Exception as e:
                print(f"Failed to cleanup backup {backup.file_path}: {e}")
        
        self.db.commit()