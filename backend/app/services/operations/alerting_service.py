"""
Alerting service for system notifications.
"""
from datetime import datetime
from typing import Dict, Any, List, Optional

from sqlalchemy import Column, String, DateTime, Boolean, Text, JSON
from sqlalchemy.orm import Session

from app.models.base import BaseModel, GUID



class SystemAlert(BaseModel):
    """System alert entries."""
    __tablename__ = "system_alerts"
    
    alert_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    resolved = Column(Boolean, nullable=False, default=False)
    resolved_at = Column(DateTime, nullable=True)
    metadata = Column(JSON, nullable=True)


class AlertingService:
    """Service for system alerting."""
    
    def __init__(self, db: Session):
        """  Init  ."""
        self.db = db
    
    def create_alert(
        self,
        alert_type: str,
        severity: str,
        title: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SystemAlert:
        """Create Alert."""
        """Create a new system alert."""
        alert = SystemAlert(
            alert_type=alert_type,
            severity=severity,
            title=title,
            message=message,
            metadata=metadata
        )
        
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        
        return alert
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve Alert."""
        """Resolve an alert."""
        alert = self.db.query(SystemAlert).filter(SystemAlert.id == alert_id).first()
        if alert:
            alert.resolved = True
            alert.resolved_at = datetime.utcnow()
            self.db.commit()
            return True
        return False
    
    def get_active_alerts(self) -> List[SystemAlert]:
        """Get Active Alerts."""
        """Get all active (unresolved) alerts."""
        return self.db.query(SystemAlert).filter(
            SystemAlert.resolved == False
        ).order_by(SystemAlert.created_at.desc()).all()
    
    def check_system_thresholds(self, metrics: Dict[str, Any]):
        """Check System Thresholds."""
        """Check system metrics against thresholds and create alerts."""
        # CPU threshold
        if metrics.get("cpu", {}).get("usage_percent", 0) > 80:
            self.create_alert(
                "system",
                "warning",
                "High CPU Usage",
                f"CPU usage is at {metrics['cpu']['usage_percent']}%"
            )
        
        # Memory threshold
        if metrics.get("memory", {}).get("usage_percent", 0) > 85:
            self.create_alert(
                "system",
                "critical",
                "High Memory Usage",
                f"Memory usage is at {metrics['memory']['usage_percent']}%"
            )