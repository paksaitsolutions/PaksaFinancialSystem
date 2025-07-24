from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db.tenant_middleware import get_current_tenant
from typing import Any, List
import logging

logger = logging.getLogger(__name__)

class TenantDataIsolation:
    @staticmethod
    async def enforce_isolation(db: AsyncSession, model_class: Any, query_params: dict):
        """Enforce tenant isolation on database queries"""
        tenant_id = get_current_tenant()
        
        if hasattr(model_class, 'tenant_id'):
            query_params['tenant_id'] = tenant_id
        
        return query_params
    
    @staticmethod
    async def validate_data_access(db: AsyncSession, record: Any):
        """Validate that record belongs to current tenant"""
        if not hasattr(record, 'tenant_id'):
            return True
        
        current_tenant = get_current_tenant()
        if record.tenant_id != current_tenant:
            logger.warning(f"Cross-tenant access attempt: {current_tenant} -> {record.tenant_id}")
            raise PermissionError("Cross-tenant data access denied")
        
        return True

class CrossTenantAccessPrevention:
    blocked_attempts = {}
    
    @classmethod
    def log_blocked_attempt(cls, tenant_id: str, target_tenant: str, resource: str):
        """Log blocked cross-tenant access attempt"""
        key = f"{tenant_id}:{target_tenant}"
        cls.blocked_attempts[key] = cls.blocked_attempts.get(key, 0) + 1
        
        logger.warning(f"Blocked cross-tenant access: {tenant_id} -> {target_tenant} ({resource})")
        
        if cls.blocked_attempts[key] > 5:
            logger.critical(f"Multiple cross-tenant attempts from {tenant_id}")
    
    @classmethod
    def check_access_pattern(cls, tenant_id: str) -> bool:
        """Check if tenant has suspicious access patterns"""
        suspicious_count = sum(
            count for key, count in cls.blocked_attempts.items() 
            if key.startswith(f"{tenant_id}:")
        )
        return suspicious_count > 10

def setup_tenant_isolation_events():
    """Setup SQLAlchemy events for tenant isolation"""
    
    @event.listens_for(AsyncSession, "before_flush")
    def validate_tenant_isolation(session, flush_context, instances):
        try:
            current_tenant = get_current_tenant()
            
            for instance in session.new | session.dirty | session.deleted:
                if hasattr(instance, 'tenant_id'):
                    if instance.tenant_id != current_tenant:
                        CrossTenantAccessPrevention.log_blocked_attempt(
                            current_tenant, instance.tenant_id, type(instance).__name__
                        )
                        raise PermissionError("Cross-tenant operation blocked")
        except Exception as e:
            logger.error(f"Tenant isolation validation failed: {e}")
            raise