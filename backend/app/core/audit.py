"""
Enterprise-level audit logging system for compliance and security.
"""
import json
import uuid
from datetime import datetime
from typing import Any, Dict, Optional, List
from enum import Enum
from sqlalchemy import Column, String, DateTime, Text, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Session
from app.core.database import Base
from app.models.user import User


class AuditAction(str, Enum):
    """Audit action types."""
    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    EXPORT = "EXPORT"
    IMPORT = "IMPORT"
    BACKUP = "BACKUP"
    RESTORE = "RESTORE"
    CONFIGURE = "CONFIGURE"


class AuditLevel(str, Enum):
    """Audit severity levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AuditLog(Base):
    """Audit log model for tracking all system activities."""
    
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=True)
    session_id = Column(String(255), nullable=True)
    action = Column(String(50), nullable=False)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(255), nullable=True)
    resource_name = Column(String(255), nullable=True)
    old_values = Column(JSONB, nullable=True)
    new_values = Column(JSONB, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    endpoint = Column(String(255), nullable=True)
    method = Column(String(10), nullable=True)
    status_code = Column(Integer, nullable=True)
    level = Column(String(20), default=AuditLevel.MEDIUM)
    message = Column(Text, nullable=True)
    audit_metadata = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    company_id = Column(String(255), nullable=True)
    tenant_id = Column(String(255), nullable=True)


class AuditLogger:
    """Centralized audit logging service."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def log(
        self,
        action: AuditAction,
        resource_type: str,
        user_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        resource_name: Optional[str] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        level: AuditLevel = AuditLevel.MEDIUM,
        message: Optional[str] = None,
        audit_metadata: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        endpoint: Optional[str] = None,
        method: Optional[str] = None,
        status_code: Optional[int] = None,
        session_id: Optional[str] = None,
        company_id: Optional[str] = None,
        tenant_id: Optional[str] = None
    ) -> AuditLog:
        """Log an audit event."""
        
        audit_entry = AuditLog(
            user_id=user_id,
            session_id=session_id,
            action=action.value,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            level=level.value,
            message=message,
            audit_metadata=audit_metadata,
            company_id=company_id,
            tenant_id=tenant_id
        )
        
        self.db.add(audit_entry)
        self.db.commit()
        return audit_entry
    
    def log_create(
        self,
        resource_type: str,
        resource_id: str,
        new_values: Dict[str, Any],
        user_id: Optional[str] = None,
        **kwargs
    ) -> AuditLog:
        """Log resource creation."""
        return self.log(
            action=AuditAction.CREATE,
            resource_type=resource_type,
            resource_id=resource_id,
            new_values=new_values,
            user_id=user_id,
            level=AuditLevel.MEDIUM,
            message=f"Created {resource_type} with ID {resource_id}",
            **kwargs
        )


def get_audit_logger(db: Session) -> AuditLogger:
    """Get audit logger instance."""
    return AuditLogger(db)