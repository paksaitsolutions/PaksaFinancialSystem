"""GL Audit Trail Service"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Column, String, DateTime, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from app.core.database.base import Base
from app.core.logging.config import get_logger
import uuid
from datetime import datetime

logger = get_logger("gl_audit")

class GLAuditLog(Base):
    """GL audit trail model"""
    __tablename__ = "gl_audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(String(50), nullable=False)
    action = Column(String(50), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(50), nullable=False)
    old_values = Column(Text)
    new_values = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

class GLAuditService:
    """Service for GL audit trail logging"""
    
    @staticmethod
    async def log_action(
        db: AsyncSession,
        tenant_id: str,
        user_id: str,
        action: str,
        entity_type: str,
        entity_id: str,
        old_values: dict = None,
        new_values: dict = None
    ):
        """Log audit trail entry"""
        import json
        
        audit_log = GLAuditLog(
            tenant_id=tenant_id,
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_values=json.dumps(old_values) if old_values else None,
            new_values=json.dumps(new_values) if new_values else None
        )
        
        db.add(audit_log)
        await db.commit()
        
        logger.info(f"Audit log created: {action} on {entity_type} {entity_id} by {user_id}")
    
    @staticmethod
    async def log_journal_entry_action(
        db: AsyncSession,
        tenant_id: str,
        user_id: str,
        action: str,
        entry_id: str,
        entry_data: dict = None
    ):
        """Log journal entry specific actions"""
        await GLAuditService.log_action(
            db, tenant_id, user_id, action, "journal_entry", entry_id, None, entry_data
        )
    
    @staticmethod
    async def log_account_action(
        db: AsyncSession,
        tenant_id: str,
        user_id: str,
        action: str,
        account_id: str,
        old_data: dict = None,
        new_data: dict = None
    ):
        """Log account specific actions"""
        await GLAuditService.log_action(
            db, tenant_id, user_id, action, "account", account_id, old_data, new_data
        )