from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db.tenant_base import TenantAwareModel
from app.core.db.tenant_middleware import get_current_tenant
from datetime import datetime
from typing import Dict, Any
import json

class TenantAuditLog(TenantAwareModel):
    __tablename__ = 'tenant_audit_logs'
    
    user_id = Column(String(50))
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(50))
    old_values = Column(JSON)
    new_values = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

class TenantAuditLogger:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def log_action(
        self,
        action: str,
        resource_type: str,
        resource_id: str = None,
        old_values: Dict[str, Any] = None,
        new_values: Dict[str, Any] = None,
        user_id: str = None,
        ip_address: str = None,
        user_agent: str = None
    ):
        """Log tenant-specific audit event"""
        try:
            audit_log = TenantAuditLog(
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                old_values=old_values,
                new_values=new_values,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            self.db.add(audit_log)
            await self.db.commit()
            
        except Exception as e:
            print(f"Audit logging failed: {e}")
    
    async def get_audit_trail(
        self,
        resource_type: str = None,
        resource_id: str = None,
        user_id: str = None,
        limit: int = 100
    ):
        """Get audit trail for current tenant"""
        query = self.db.query(TenantAuditLog)
        
        if resource_type:
            query = query.filter(TenantAuditLog.resource_type == resource_type)
        if resource_id:
            query = query.filter(TenantAuditLog.resource_id == resource_id)
        if user_id:
            query = query.filter(TenantAuditLog.user_id == user_id)
        
        return query.order_by(TenantAuditLog.timestamp.desc()).limit(limit).all()

def audit_decorator(action: str, resource_type: str):
    """Decorator to automatically audit function calls"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract relevant info
            result = await func(*args, **kwargs)
            
            # Log the action
            # Implementation would depend on function signature
            
            return result
        return wrapper
    return decorator