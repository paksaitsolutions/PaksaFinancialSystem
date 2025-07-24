from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.core.auth.tenant_auth import validate_tenant_access
from app.core.monitoring.tenant_usage import usage_tracker
from app.api.tenant_router import tenant_required

router = APIRouter()

@router.get("/tenant/info")
@tenant_required
async def get_tenant_info(
    tenant = Depends(validate_tenant_access),
    db: AsyncSession = Depends(get_db)
):
    return {
        "tenant_id": tenant.tenant_id,
        "name": tenant.name,
        "status": tenant.status,
        "subscription_plan": tenant.subscription_plan
    }

@router.get("/tenant/usage")
@tenant_required
async def get_tenant_usage(
    db: AsyncSession = Depends(get_db),
    tenant = Depends(validate_tenant_access)
):
    return await usage_tracker.get_usage_stats(db)

@router.post("/tenant/track-api")
async def track_api_usage(
    endpoint: str,
    tenant = Depends(validate_tenant_access)
):
    await usage_tracker.track_api_call(endpoint)
    return {"status": "tracked"}