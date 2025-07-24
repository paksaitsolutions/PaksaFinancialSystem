from app.core.db.tenant_middleware import set_tenant_context
from typing import Any, Callable
import logging

logger = logging.getLogger(__name__)

class TenantAwareJob:
    def task(self, tenant_id: str):
        def decorator(func: Callable):
            def wrapper(*args, **kwargs):
                set_tenant_context(tenant_id)
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Tenant job failed for {tenant_id}: {e}")
                    raise
            return wrapper
        return decorator

def process_tenant_reports(tenant_id: str):
    set_tenant_context(tenant_id)
    pass

def cleanup_tenant_data(tenant_id: str):
    set_tenant_context(tenant_id)
    pass