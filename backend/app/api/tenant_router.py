from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.core.db.tenant_middleware import get_current_tenant
from app.services.tenant_service import tenant_service
from typing import Any, Dict

def create_tenant_aware_router(prefix: str, tags: list = None) -> APIRouter:
    """Create a router with automatic tenant context"""
    router = APIRouter(prefix=prefix, tags=tags or [])
    
    @router.middleware("http")
    async def add_tenant_context(request: Request, call_next):
        try:
            tenant_id = get_current_tenant()
            request.state.tenant_id = tenant_id
            response = await call_next(request)
            return response
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Tenant context error: {str(e)}")
    
    return router

def tenant_required(func):
    """Decorator to ensure tenant context is available"""
    async def wrapper(*args, **kwargs):
        try:
            tenant_id = get_current_tenant()
            return await func(*args, **kwargs)
        except Exception:
            raise HTTPException(status_code=400, detail="Tenant context required")
    return wrapper

def get_tenant_stats(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Get current tenant statistics"""
    tenant_id = get_current_tenant()
    return tenant_service.get_tenant_stats(db, tenant_id)