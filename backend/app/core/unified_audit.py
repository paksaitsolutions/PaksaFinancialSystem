"""
Unified Audit Trail System
Cross-module audit logging and tracking
"""
from typing import Dict, Any, Optional, List
from sqlalchemy import Column, String, Text, DateTime, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.models.base import Base, BaseModel
from datetime import datetime
import json

class UnifiedAuditLog(BaseModel):
    """Unified audit log for all modules"""
    __tablename__ = "unified_audit_logs"
    
    # Core audit fields
    company_id = Column(String, ForeignKey("companies.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    session_id = Column(String(100), index=True)
    
    # Action details
    module_name = Column(String(50), nullable=False, index=True)
    action_type = Column(String(50), nullable=False, index=True)  # CREATE, UPDATE, DELETE, VIEW, APPROVE, etc.
    resource_type = Column(String(100), nullable=False, index=True)  # invoice, payment, journal_entry, etc.
    resource_id = Column(String, nullable=True, index=True)
    
    # Change tracking
    old_values = Column(JSON)
    new_values = Column(JSON)
    changed_fields = Column(JSON)  # Array of field names that changed
    
    # Context
    description = Column(Text)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    request_id = Column(String(100), index=True)
    
    # Metadata
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    severity = Column(String(20), default="INFO")  # DEBUG, INFO, WARN, ERROR, CRITICAL
    tags = Column(JSON)  # Array of tags for categorization
    
    # Relationships
    company = relationship("Company", viewonly=True)
    user = relationship("User", viewonly=True)
    
    __table_args__ = (
        Index('idx_audit_company_module_time', 'company_id', 'module_name', 'timestamp'),
        Index('idx_audit_resource', 'resource_type', 'resource_id'),
        Index('idx_audit_user_time', 'user_id', 'timestamp'),
        {"extend_existing": True}
    )

class AuditRule(BaseModel):
    """Rules for audit logging"""
    __tablename__ = "audit_rules"
    
    rule_name = Column(String(100), nullable=False, unique=True)
    module_name = Column(String(50), nullable=False)
    resource_type = Column(String(100), nullable=False)
    actions = Column(JSON, nullable=False)  # Array of actions to audit
    fields_to_track = Column(JSON)  # Specific fields to track, null = all fields
    is_active = Column(Boolean, default=True)
    retention_days = Column(Integer, default=2555)  # 7 years default
    
    __table_args__ = (
        {"extend_existing": True},
    )

class UnifiedAuditService:
    """Service for unified audit logging"""
    
    def __init__(self, db_session):
        self.db = db_session
    
    async def log_action(self, 
                        company_id: str,
                        user_id: Optional[str],
                        module_name: str,
                        action_type: str,
                        resource_type: str,
                        resource_id: Optional[str] = None,
                        old_values: Optional[Dict] = None,
                        new_values: Optional[Dict] = None,
                        description: Optional[str] = None,
                        ip_address: Optional[str] = None,
                        user_agent: Optional[str] = None,
                        request_id: Optional[str] = None,
                        severity: str = "INFO",
                        tags: Optional[List[str]] = None) -> UnifiedAuditLog:
        """Log an audit event"""
        
        # Calculate changed fields
        changed_fields = []
        if old_values and new_values:
            for key in new_values:
                if key in old_values and old_values[key] != new_values[key]:
                    changed_fields.append(key)
                elif key not in old_values:
                    changed_fields.append(key)
        
        audit_log = UnifiedAuditLog(
            company_id=company_id,
            user_id=user_id,
            module_name=module_name,
            action_type=action_type,
            resource_type=resource_type,
            resource_id=resource_id,
            old_values=old_values,
            new_values=new_values,
            changed_fields=changed_fields,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
            severity=severity,
            tags=tags or []
        )
        
        self.db.add(audit_log)
        await self.db.commit()
        return audit_log
    
    async def get_audit_trail(self, 
                             company_id: str,
                             resource_type: Optional[str] = None,
                             resource_id: Optional[str] = None,
                             user_id: Optional[str] = None,
                             module_name: Optional[str] = None,
                             start_date: Optional[datetime] = None,
                             end_date: Optional[datetime] = None,
                             limit: int = 100) -> List[UnifiedAuditLog]:
        """Get audit trail with filters"""
        
        query = self.db.query(UnifiedAuditLog).filter(
            UnifiedAuditLog.company_id == company_id
        )
        
        if resource_type:
            query = query.filter(UnifiedAuditLog.resource_type == resource_type)
        
        if resource_id:
            query = query.filter(UnifiedAuditLog.resource_id == resource_id)
        
        if user_id:
            query = query.filter(UnifiedAuditLog.user_id == user_id)
        
        if module_name:
            query = query.filter(UnifiedAuditLog.module_name == module_name)
        
        if start_date:
            query = query.filter(UnifiedAuditLog.timestamp >= start_date)
        
        if end_date:
            query = query.filter(UnifiedAuditLog.timestamp <= end_date)
        
        return await query.order_by(UnifiedAuditLog.timestamp.desc()).limit(limit).all()
    
    async def get_user_activity(self, user_id: str, company_id: str, days: int = 30) -> List[UnifiedAuditLog]:
        """Get user activity for the last N days"""
        from datetime import timedelta
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        return await self.db.query(UnifiedAuditLog).filter(
            UnifiedAuditLog.user_id == user_id,
            UnifiedAuditLog.company_id == company_id,
            UnifiedAuditLog.timestamp >= start_date
        ).order_by(UnifiedAuditLog.timestamp.desc()).all()
    
    async def get_resource_history(self, resource_type: str, resource_id: str, company_id: str) -> List[UnifiedAuditLog]:
        """Get complete history of a resource"""
        return await self.db.query(UnifiedAuditLog).filter(
            UnifiedAuditLog.resource_type == resource_type,
            UnifiedAuditLog.resource_id == resource_id,
            UnifiedAuditLog.company_id == company_id
        ).order_by(UnifiedAuditLog.timestamp.asc()).all()

# Audit decorator for automatic logging
def audit_action(module_name: str, action_type: str, resource_type: str):
    """Decorator for automatic audit logging"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract context from function arguments
            # This would be implemented based on your specific needs
            result = await func(*args, **kwargs)
            
            # Log the action
            # Implementation would depend on how you pass audit service
            
            return result
        return wrapper
    return decorator

# Default audit rules for each module
DEFAULT_AUDIT_RULES = {
    "gl": {
        "journal_entry": ["CREATE", "UPDATE", "DELETE", "POST", "REVERSE"],
        "chart_of_accounts": ["CREATE", "UPDATE", "DELETE"],
        "period_close": ["CLOSE", "REOPEN"]
    },
    "ap": {
        "vendor": ["CREATE", "UPDATE", "DELETE"],
        "invoice": ["CREATE", "UPDATE", "DELETE", "APPROVE", "REJECT"],
        "payment": ["CREATE", "UPDATE", "DELETE", "APPROVE"]
    },
    "ar": {
        "customer": ["CREATE", "UPDATE", "DELETE"],
        "invoice": ["CREATE", "UPDATE", "DELETE", "SEND"],
        "payment": ["CREATE", "UPDATE", "DELETE"],
        "collection": ["CREATE", "UPDATE", "ESCALATE"]
    },
    "tax": {
        "tax_rate": ["CREATE", "UPDATE", "DELETE"],
        "tax_return": ["CREATE", "UPDATE", "FILE", "AMEND"],
        "exemption": ["CREATE", "UPDATE", "DELETE", "APPROVE"]
    },
    "payroll": {
        "employee": ["CREATE", "UPDATE", "DELETE", "TERMINATE"],
        "payroll_run": ["CREATE", "PROCESS", "APPROVE", "REVERSE"],
        "timesheet": ["CREATE", "UPDATE", "APPROVE", "REJECT"]
    },
    "inventory": {
        "item": ["CREATE", "UPDATE", "DELETE"],
        "adjustment": ["CREATE", "APPROVE"],
        "transfer": ["CREATE", "APPROVE", "RECEIVE"]
    },
    "hrm": {
        "employee": ["CREATE", "UPDATE", "DELETE"],
        "leave_request": ["CREATE", "APPROVE", "REJECT"],
        "performance_review": ["CREATE", "UPDATE", "SUBMIT", "APPROVE"]
    }
}