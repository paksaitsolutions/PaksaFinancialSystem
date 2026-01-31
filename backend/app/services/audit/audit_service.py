"""
Audit logging service.
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import json

from sqlalchemy import and_, or_, desc, func
from sqlalchemy.orm import Session
from uuid import UUID

from app.models.audit import AuditLog, AuditConfig, AuditAction
from app.models.user import User





class AuditService:
    """Service for managing audit logs."""
    
    def __init__(self, db: Session):
        """  Init  ."""
        self.db = db
    
    def log_action(
        """Log Action."""
        self,
        action: str,
        resource_type: str,
        user_id: Optional[UUID] = None,
        resource_id: Optional[str] = None,
        old_values: Optional[Dict] = None,
        new_values: Optional[Dict] = None,
        endpoint: Optional[str] = None,
        method: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
        session_id: Optional[UUID] = None
    ) -> AuditLog:
        """Log Action."""
        """Log an audit action."""
        config = self.get_active_config()
        
        if not self._should_log_action(action, resource_type, config):
            return None
        
        old_values = self._clean_sensitive_data(old_values, resource_type)
        new_values = self._clean_sensitive_data(new_values, resource_type)
        
        audit_log = AuditLog(
            user_id=user_id,
            session_id=session_id,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id else None,
            endpoint=endpoint,
            method=method,
            ip_address=ip_address,
            user_agent=user_agent,
            old_values=old_values,
            new_values=new_values,
            description=description,
            metadata=metadata,
            timestamp=datetime.utcnow()
        )
        
        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)
        
        return audit_log
    
    def get_audit_logs(
        """Get Audit Logs."""
        self,
        user_id: Optional[UUID] = None,
        resource_type: Optional[str] = None,
        action: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[AuditLog]:
        """Get Audit Logs."""
        """Get audit logs with filters."""
        query = self.db.query(AuditLog)
        
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
        
        if action:
            query = query.filter(AuditLog.action == action)
        
        if start_date:
            query = query.filter(AuditLog.timestamp >= start_date)
        
        if end_date:
            query = query.filter(AuditLog.timestamp <= end_date)
        
        return query.order_by(desc(AuditLog.timestamp))\
                   .offset(skip).limit(limit).all()
    
    def get_user_activity(self, user_id: UUID, days: int = 30) -> List[AuditLog]:
        """Get User Activity."""
        """Get recent activity for a user."""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        return self.db.query(AuditLog).filter(
            and_(
                AuditLog.user_id == user_id,
                AuditLog.timestamp >= start_date
            )
        ).order_by(desc(AuditLog.timestamp)).all()
    
    def get_resource_history(self, resource_type: str, resource_id: str) -> List[AuditLog]:
        """Get Resource History."""
        """Get audit history for a specific resource."""
        return self.db.query(AuditLog).filter(
            and_(
                AuditLog.resource_type == resource_type,
                AuditLog.resource_id == str(resource_id)
            )
        ).order_by(desc(AuditLog.timestamp)).all()
    
    def get_audit_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get Audit Statistics."""
        """Get audit statistics."""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        total_logs = self.db.query(func.count(AuditLog.id)).filter(
            AuditLog.timestamp >= start_date
        ).scalar()
        
        action_stats = self.db.query(
            AuditLog.action,
            func.count(AuditLog.id).label('count')
        ).filter(
            AuditLog.timestamp >= start_date
        ).group_by(AuditLog.action).all()
        
        resource_stats = self.db.query(
            AuditLog.resource_type,
            func.count(AuditLog.id).label('count')
        ).filter(
            AuditLog.timestamp >= start_date
        ).group_by(AuditLog.resource_type).all()
        
        active_users = self.db.query(func.count(func.distinct(AuditLog.user_id))).filter(
            and_(
                AuditLog.timestamp >= start_date,
                AuditLog.user_id.isnot(None)
            )
        ).scalar()
        
        return {
            'total_logs': total_logs,
            'active_users': active_users,
            'actions': {action: count for action, count in action_stats},
            'resources': {resource: count for resource, count in resource_stats},
            'period_days': days
        }
    
    def cleanup_old_logs(self) -> int:
        """Cleanup Old Logs."""
        """Clean up old audit logs based on retention policy."""
        config = self.get_active_config()
        retention_days = int(config.retention_days)
        
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        
        old_logs = self.db.query(AuditLog).filter(
            AuditLog.timestamp < cutoff_date
        ).all()
        
        count = len(old_logs)
        
        for log in old_logs:
            self.db.delete(log)
        
        self.db.commit()
        return count
    
    def get_active_config(self) -> AuditConfig:
        """Get Active Config."""
        """Get active audit configuration."""
        config = self.db.query(AuditConfig).filter(
            AuditConfig.is_active == "true"
        ).first()
        
        if not config:
            config = self._create_default_config()
        
        return config
    
    def _should_log_action(self, action: str, resource_type: str, config: AuditConfig) -> bool:
        """ Should Log Action."""
        """Check if action should be logged based on configuration."""
        if action in [AuditAction.CREATE, AuditAction.UPDATE, AuditAction.DELETE]:
            return True
        
        if action == AuditAction.READ:
            if config.log_read_operations == "false":
                return False
            elif config.log_read_operations == "sensitive":
                sensitive_resources = config.sensitive_resources or []
                return resource_type in sensitive_resources
        
        excluded_resources = config.excluded_resources or []
        if resource_type in excluded_resources:
            return False
        
        return True
    
    def _clean_sensitive_data(self, data: Optional[Dict], resource_type: str) -> Optional[Dict]:
        """ Clean Sensitive Data."""
        """Clean sensitive data from audit logs."""
        if not data:
            return data
        
        sensitive_fields = [
            'password', 'hashed_password', 'token', 'secret', 'key',
            'ssn', 'social_security_number', 'credit_card', 'bank_account'
        ]
        
        cleaned_data = data.copy()
        
        for field in sensitive_fields:
            if field in cleaned_data:
                cleaned_data[field] = "[REDACTED]"
        
        return cleaned_data
    
    def _create_default_config(self) -> AuditConfig:
        """ Create Default Config."""
        """Create default audit configuration."""
        config = AuditConfig(
            name="Default Audit Configuration",
            description="Default audit logging settings",
            log_read_operations="sensitive",
            log_failed_attempts="true",
            retention_days="2555",
            excluded_resources=["health_check", "metrics"],
            sensitive_resources=["users", "payroll", "financial_statements"],
            is_active="true"
        )
        
        self.db.add(config)
        self.db.commit()
        self.db.refresh(config)
        
        return config