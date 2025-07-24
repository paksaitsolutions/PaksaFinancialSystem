"""
Audit logging models.
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship

from .base import BaseModel, GUID


class AuditAction(str, Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    EXPORT = "export"
    IMPORT = "import"
    APPROVE = "approve"
    REJECT = "reject"


class AuditLog(BaseModel):
    """
    Audit log for tracking user actions and system changes.
    """
    __tablename__ = "audit_logs"
    
    # User and session information
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=True)
    session_id = Column(GUID(), nullable=True)
    
    # Action details
    action = Column(String(20), nullable=False)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(String(100), nullable=True)
    
    # Request details
    endpoint = Column(String(200), nullable=True)
    method = Column(String(10), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Data changes
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    
    # Additional context
    description = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)
    
    # Timestamp
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    
    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, action='{self.action}', resource='{self.resource_type}')>"


class AuditConfig(BaseModel):
    """
    Audit configuration settings.
    """
    __tablename__ = "audit_configs"
    
    # Configuration details
    name = Column(String(100), nullable=False, default="Default Audit Config")
    description = Column(Text, nullable=True)
    
    # Audit settings
    log_read_operations = Column(String(10), nullable=False, default="false")  # true/false/sensitive
    log_failed_attempts = Column(String(10), nullable=False, default="true")
    retention_days = Column(String(10), nullable=False, default="2555")  # 7 years default
    
    # Resource-specific settings
    excluded_resources = Column(JSON, nullable=True)  # Resources to exclude from audit
    sensitive_resources = Column(JSON, nullable=True)  # Resources requiring detailed audit
    
    # Status
    is_active = Column(String(10), nullable=False, default="true")
    
    def __repr__(self) -> str:
        return f"<AuditConfig(name='{self.name}', active={self.is_active})>"