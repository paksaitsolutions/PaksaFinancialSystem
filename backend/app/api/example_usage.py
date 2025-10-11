"""
Example API Usage for Multi-Company, Multi-User, Multi-Role System
=================================================================
Shows how to use authentication context in API endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.auth_context import (
    AuthContext, 
    get_auth_context, 
    get_current_company_id,
    require_permission,
    require_superuser
)
from app.models import APInvoice, Customer

router = APIRouter()

@router.get("/invoices")
async def get_invoices(
    auth: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db)
):
    """Get invoices for current user's company only."""
    
    # Automatically filter by user's company
    query = select(APInvoice).where(APInvoice.company_id == auth.company_id)
    result = await db.execute(query)
    invoices = result.scalars().all()
    
    return {
        "user": f"{auth.user.first_name} {auth.user.last_name}",
        "company": auth.company.company_name,
        "role": auth.role_name,
        "invoices": len(invoices)
    }

@router.get("/customers")
async def get_customers(
    company_id: str = Depends(get_current_company_id),
    db: AsyncSession = Depends(get_db)
):
    """Get customers using company_id dependency."""
    
    query = select(Customer).where(Customer.company_id == company_id)
    result = await db.execute(query)
    customers = result.scalars().all()
    
    return {"customers": len(customers)}

@router.post("/invoices")
async def create_invoice(
    invoice_data: dict,
    auth: AuthContext = Depends(require_permission("create_invoice")),
    db: AsyncSession = Depends(get_db)
):
    """Create invoice - requires 'create_invoice' permission."""
    
    # Automatically set company_id from authenticated user
    invoice_data["company_id"] = auth.company_id
    
    # Create invoice logic here...
    return {"message": "Invoice created", "company": auth.company.company_name}

@router.delete("/system/cleanup")
async def system_cleanup(
    auth: AuthContext = Depends(require_superuser()),
    db: AsyncSession = Depends(get_db)
):
    """System cleanup - requires superuser access."""
    
    # Only superusers can access this endpoint
    return {"message": "System cleanup initiated by superuser"}

@router.get("/user/context")
async def get_user_context(auth: AuthContext = Depends(get_auth_context)):
    """Get current user context information."""
    
    return {
        "user_id": auth.user_id,
        "user_name": f"{auth.user.first_name} {auth.user.last_name}",
        "email": auth.user.email,
        "company_id": auth.company_id,
        "company_name": auth.company.company_name,
        "role": auth.role_name,
        "is_superuser": auth.is_superuser,
        "permissions": [perm.permission.name for perm in auth.role.permissions]
    }