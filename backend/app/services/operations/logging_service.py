"""
Application logging service.
"""
from datetime import datetime
from typing import Dict, Any, Optional
import json

from sqlalchemy import Column, String, DateTime, Text, JSON
from sqlalchemy.orm import Session
import logging

from app.models.base import BaseModel, GUID



class SystemLog(BaseModel):
    """System log entries."""
    __tablename__ = "system_logs"
    
    level = Column(String(20), nullable=False)
    message = Column(Text, nullable=False)
    module = Column(String(100), nullable=True)
    user_id = Column(GUID(), nullable=True)
    log_metadata = Column(JSON, nullable=True)


class LoggingService:
    """Service for application logging."""
    
    def __init__(self, db: Session):
        """  Init  ."""
        self.db = db
        self.logger = logging.getLogger(__name__)
    
    def log_info(self, message: str, module: Optional[str] = None, user_id: Optional[str] = None, metadata: Optional[Dict] = None):
        """Log Info."""
        """Log info message."""
        self._log("INFO", message, module, user_id, metadata)
    
    def log_warning(self, message: str, module: Optional[str] = None, user_id: Optional[str] = None, metadata: Optional[Dict] = None):
        """Log Warning."""
        """Log warning message."""
        self._log("WARNING", message, module, user_id, metadata)
    
    def log_error(self, message: str, module: Optional[str] = None, user_id: Optional[str] = None, metadata: Optional[Dict] = None):
        """Log Error."""
        """Log error message."""
        self._log("ERROR", message, module, user_id, metadata)
    
    def _log(self, level: str, message: str, module: Optional[str], user_id: Optional[str], metadata: Optional[Dict]):
        """ Log."""
        """Internal logging method."""
        try:
            log_entry = SystemLog(
                level=level,
                message=message,
                module=module,
                user_id=user_id,
                log_metadata=metadata
            )
            self.db.add(log_entry)
            self.db.commit()
        except Exception as e:
            self.logger.error(f"Failed to log to database: {e}")
    
    def get_logs(self, level: Optional[str] = None, limit: int = 100):
        """Get Logs."""
        """Get system logs."""
        query = self.db.query(SystemLog)
        if level:
            query = query.filter(SystemLog.level == level)
        return query.order_by(SystemLog.created_at.desc()).limit(limit).all()