"""
Base model with common fields and audit functionality
"""
from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class AuditMixin:
    """Mixin for audit trail functionality"""
    created_by = Column(String)
    updated_by = Column(String)
    
    def create_audit_log(self, db, user_id: str, action: str, old_values=None, new_values=None):
        from app.models.user_enhanced import AuditLog
        import json
        
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=self.__class__.__name__,
            resource_id=str(self.id),
            old_values=json.dumps(old_values) if old_values else None,
            new_values=json.dumps(new_values) if new_values else None
        )
        db.add(audit_log)
        return audit_log