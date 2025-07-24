"""
API endpoints for procurement.
"""
from typing import Any, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.session import get_db
from app.core.db.router import db_router
from app.core.api_response import success_response, error_response
from app.core.permissions import require_permission, Permission
from app.crud.procurement.procurement_crud import procurement_crud
from app.schemas.procurement.procurement_schemas import (
    VendorCreate, VendorUpdate, VendorResponse,
    PurchaseOrderCreate, PurchaseOrderUpdate, PurchaseOrderResponse,
    VendorPaymentCreate, VendorPaymentResponse,
    PurchaseAnalytics
)

router = APIRouter()

# Mock tenant and user IDs
MOCK_TENANT_ID = UUID("12345678-1234-5678-9012-123456789012")
MOCK_USER_ID = UUID("12345678-1234-5678-9012-123456789012")

# Vendor endpoints
@router.post("/vendors", response_model=VendorResponse, status_code=status.HTTP_201_CREATED)
async def create_vendor(
    *,
    db: AsyncSession = Depends(get_db),
    vendor_in: VendorCreate,
    _: bool = Depends(require_permission(Permission.WRITE)),
) -> Any:
    """Create vendor."""
    vendor = await procurement_crud.create_vendor(
        db, tenant_id=MOCK_TENANT_ID, obj_in=vendor_in
    )
    return success_response(
        data=vendor,
        message="Vendor created successfully",
        status_code=status.HTTP_201_CREATED,
    )

@router.get("/vendors", response_model=List[VendorResponse])
async def get_vendors(
    *,
    db: AsyncSession = Depends(db_router.get_read_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(True),
    _: bool = Depends(require_permission(Permission.READ)),
) -> Any:
    """Get vendors."""
    filters = {}
    if active_only:
        filters["is_active"] = True
    
    vendors = await procurement_crud.get_vendors(
        db, tenant_id=MOCK_TENANT_ID, skip=skip, limit=limit, filters=filters
    )
    return success_response(data=vendors)

@router.get("/vendors/{vendor_id}", response_model=VendorResponse)
async def get_vendor(
    *,
    db: AsyncSession = Depends(db_router.get_read_session),
    vendor_id: UUID,
    _: bool = Depends(require_permission(Permission.READ)),
) -> Any:
    """Get vendor by ID."""
    vendor = await procurement_crud.get_vendor(
        db, tenant_id=MOCK_TENANT_ID, id=vendor_id
    )
    if not vendor:
        return error_response(
            message="Vendor not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return success_response(data=vendor)

@router.put("/vendors/{vendor_id}", response_model=VendorResponse)
async def update_vendor(
    *,
    db: AsyncSession = Depends(get_db),
    vendor_id: UUID,
    vendor_in: VendorUpdate,
    _: bool = Depends(require_permission(Permission.WRITE)),
) -> Any:
    """Update vendor."""
    vendor = await procurement_crud.get_vendor(
        db, tenant_id=MOCK_TENANT_ID, id=vendor_id
    )
    if not vendor:
        return error_response(
            message="Vendor not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    
    vendor = await procurement_crud.update_vendor(db, db_obj=vendor, obj_in=vendor_in)
    return success_response(
        data=vendor,
        message="Vendor updated successfully",
    )

# Purchase Order endpoints
@router.post("/purchase-orders", response_model=PurchaseOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_purchase_order(
    *,
    db: AsyncSession = Depends(get_db),
    po_in: PurchaseOrderCreate,
    _: bool = Depends(require_permission(Permission.WRITE)),
) -> Any:
    """Create purchase order."""
    po = await procurement_crud.create_purchase_order(
        db, tenant_id=MOCK_TENANT_ID, created_by=MOCK_USER_ID, obj_in=po_in
    )
    return success_response(
        data=po,
        message="Purchase order created successfully",
        status_code=status.HTTP_201_CREATED,
    )

@router.get("/purchase-orders", response_model=List[PurchaseOrderResponse])
async def get_purchase_orders(
    *,
    db: AsyncSession = Depends(db_router.get_read_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_filter: Optional[str] = Query(None, alias="status"),
    _: bool = Depends(require_permission(Permission.READ)),
) -> Any:
    """Get purchase orders."""
    filters = {}
    if status_filter:
        filters["status"] = status_filter
    
    orders = await procurement_crud.get_purchase_orders(
        db, tenant_id=MOCK_TENANT_ID, skip=skip, limit=limit, filters=filters
    )
    return success_response(data=orders)

@router.post("/purchase-orders/{po_id}/approve")
async def approve_purchase_order(
    *,
    db: AsyncSession = Depends(get_db),
    po_id: UUID,
    _: bool = Depends(require_permission(Permission.WRITE)),
) -> Any:
    """Approve purchase order."""
    # Get PO
    po = await procurement_crud.get_vendor(db, tenant_id=MOCK_TENANT_ID, id=po_id)  # This should be get_purchase_order when implemented
    if not po:
        return error_response(
            message="Purchase order not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    
    try:
        po = await procurement_crud.approve_purchase_order(
            db, purchase_order=po, approved_by=MOCK_USER_ID
        )
        return success_response(
            data=po,
            message="Purchase order approved successfully",
        )
    except ValueError as e:
        return error_response(
            message=str(e),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

# Vendor Payment endpoints
@router.post("/vendor-payments", response_model=VendorPaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_vendor_payment(
    *,
    db: AsyncSession = Depends(get_db),
    payment_in: VendorPaymentCreate,
    _: bool = Depends(require_permission(Permission.WRITE)),
) -> Any:
    """Create vendor payment."""
    payment = await procurement_crud.create_vendor_payment(
        db, tenant_id=MOCK_TENANT_ID, created_by=MOCK_USER_ID, obj_in=payment_in
    )
    return success_response(
        data=payment,
        message="Vendor payment created successfully",
        status_code=status.HTTP_201_CREATED,
    )

# Analytics endpoints
@router.get("/analytics", response_model=PurchaseAnalytics)
async def get_purchase_analytics(
    *,
    db: AsyncSession = Depends(db_router.get_read_session),
    _: bool = Depends(require_permission(Permission.READ)),
) -> Any:
    """Get purchase analytics."""
    analytics = await procurement_crud.get_purchase_analytics(
        db, tenant_id=MOCK_TENANT_ID
    )
    return success_response(data=analytics)