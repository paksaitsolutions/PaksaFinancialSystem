from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.core.db.tenant_middleware import get_current_tenant
from app.services.tenant_service import tenant_service

async def validate_tenant_access(db: AsyncSession = Depends(get_db)):
    tenant_id = get_current_tenant()
    tenant = await tenant_service.get_tenant_by_id(db, tenant_id)
    
    if not tenant or tenant.status != 'active':
        raise HTTPException(status_code=403, detail="Tenant access denied")
    
    return tenant

def require_tenant_permission(permission: str):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        return wrapper
    return decorator