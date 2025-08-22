"""
Tenant management API endpoints.
"""
from typing import Any, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.session import get_db
from app.core.api_response import success_response, error_response
from app.core.permissions import require_permission, Permission
from app.middleware.tenant_context import get_current_tenant_id
from app.services.tenant_migration import tenant_migration_service
from app.services.background_jobs import job_queue

router = APIRouter()

@router.get("/current")
async def get_current_tenant(
    request: Request,
    _: bool = Depends(require_permission(Permission.READ))
) -> Any:
    """Get current tenant information."""
    try:
        tenant_id = get_current_tenant_id(request)
        
        # Mock tenant data - in production, fetch from database
        tenant_info = {
            "id": tenant_id,
            "name": "Sample Company",
            "domain": "sample.com",
            "settings": {
                "currency": "USD",
                "timezone": "UTC",
                "date_format": "MM/DD/YYYY"
            },
            "features": [
                "invoicing",
                "accounting",
                "hrm",
                "procurement",
                "inventory"
            ]
        }
        
        return success_response(data=tenant_info)
        
    except Exception as e:
        return error_response(
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@router.get("/stats")
async def get_tenant_stats(
    request: Request,
    _: bool = Depends(require_permission(Permission.ADMIN))
) -> Any:
    """Get tenant statistics."""
    try:
        tenant_id = UUID(get_current_tenant_id(request))
        stats = await tenant_migration_service.get_tenant_stats(tenant_id)
        
        return success_response(data=stats)
        
    except Exception as e:
        return error_response(
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@router.post("/setup")
async def setup_tenant_environment(
    request: Request,
    _: bool = Depends(require_permission(Permission.ADMIN))
) -> Any:
    """Setup database environment for current tenant."""
    try:
        tenant_id = UUID(get_current_tenant_id(request))
        
        # Queue setup job
        job_id = await job_queue.enqueue(
            "tenant_setup",
            {"tenant_id": str(tenant_id)},
            tenant_id=str(tenant_id)
        )
        
        return success_response(
            data={"job_id": job_id, "message": "Tenant setup queued"},
            status_code=status.HTTP_202_ACCEPTED
        )
        
    except Exception as e:
        return error_response(
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@router.post("/migrate/{migration_name}")
async def run_tenant_migration(
    migration_name: str,
    request: Request,
    _: bool = Depends(require_permission(Permission.ADMIN))
) -> Any:
    """Run specific migration for current tenant."""
    try:
        tenant_id = UUID(get_current_tenant_id(request))
        
        success = await tenant_migration_service.migrate_tenant_data(
            tenant_id, migration_name
        )
        
        if success:
            return success_response(
                data={"message": f"Migration {migration_name} completed"}
            )
        else:
            return error_response(
                message=f"Migration {migration_name} failed",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except Exception as e:
        return error_response(
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@router.get("/permissions")
async def get_tenant_permissions(
    request: Request,
    _: bool = Depends(require_permission(Permission.READ))
) -> Any:
    """Get current user's permissions for the tenant."""
    try:
        tenant_id = get_current_tenant_id(request)
        
        # Mock permissions - in production, fetch from database
        permissions = {
            "tenant_id": tenant_id,
            "user_permissions": [
                "invoicing:read",
                "invoicing:write",
                "accounting:read",
                "hrm:read",
                "reports:read"
            ],
            "role": "manager",
            "can_switch_companies": True,
            "accessible_modules": [
                "dashboard",
                "invoicing",
                "accounting",
                "hrm",
                "reports"
            ]
        }
        
        return success_response(data=permissions)
        
    except Exception as e:
        return error_response(
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@router.get("/audit-log")
async def get_tenant_audit_log(
    request: Request,
    limit: int = 50,
    _: bool = Depends(require_permission(Permission.ADMIN))
) -> Any:
    """Get audit log for current tenant."""
    try:
        tenant_id = get_current_tenant_id(request)
        
        # Mock audit log - in production, fetch from database
        audit_entries = [
            {
                "id": "1",
                "timestamp": "2024-01-15T10:30:00Z",
                "user_id": "user123",
                "action": "invoice_created",
                "resource": "invoice_001",
                "details": {"amount": 1500.00, "customer": "ABC Corp"}
            },
            {
                "id": "2",
                "timestamp": "2024-01-15T09:15:00Z",
                "user_id": "user456",
                "action": "employee_updated",
                "resource": "emp_789",
                "details": {"field": "salary", "old_value": 50000, "new_value": 55000}
            }
        ]
        
        return success_response(data={
            "tenant_id": tenant_id,
            "entries": audit_entries[:limit],
            "total_count": len(audit_entries)
        })
        
    except Exception as e:
        return error_response(
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# Background job handlers
async def tenant_setup_job(payload: dict, tenant_id: str):
    """Background job for tenant setup."""
    tenant_uuid = UUID(tenant_id)
    success = await tenant_migration_service.setup_tenant_environment(tenant_uuid)
    
    if success:
        logger.info(f"Tenant setup completed for {tenant_id}")
    else:
        logger.error(f"Tenant setup failed for {tenant_id}")

# Register job handler
job_queue.register_handler("tenant_setup", tenant_setup_job)