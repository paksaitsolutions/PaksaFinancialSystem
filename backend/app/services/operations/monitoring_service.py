"""
System monitoring service.
"""
import psutil
import time
from datetime import datetime
from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text


class MonitoringService:
    """Service for system monitoring and health checks."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status."""
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "cpu": self._get_cpu_metrics(),
            "memory": self._get_memory_metrics(),
            "database": self._get_database_metrics()
        }
    
    def _get_cpu_metrics(self) -> Dict[str, Any]:
        """Get CPU metrics."""
        return {
            "usage_percent": psutil.cpu_percent(interval=1),
            "count": psutil.cpu_count()
        }
    
    def _get_memory_metrics(self) -> Dict[str, Any]:
        """Get memory metrics."""
        memory = psutil.virtual_memory()
        return {
            "total": memory.total,
            "used": memory.used,
            "usage_percent": memory.percent
        }
    
    def _get_database_metrics(self) -> Dict[str, Any]:
        """Get database metrics."""
        try:
            self.db.execute(text("SELECT 1"))
            return {"status": "connected"}
        except Exception as e:
            return {"status": "error", "error": str(e)}