"""
API endpoints for purchase order management.
"""
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.session import get_db
from app.core.api_response import success_response, error_response
from app.crud.inventory.purchase_order import purchase_order_crud
from app.schemas.inventory.purchase_order import (
    PurchaseOrderCreate,
    PurchaseOrderUpdate,
    PurchaseOrderResponse,
    PurchaseOrderReceiptCreate,
)

router = APIRouter()

@router.post("/", response_model=PurchaseOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_purchase_order(
    *,
    db: AsyncSession = Depends(get_db),
    po_in: PurchaseOrderCreate,
) -> Any:
    """
    Create a new purchase order.
    """
    try:
        po = await purchase_order_crud.create(db, obj_in=po_in)
        return success_response(
            data=po,
            message="Purchase order created successfully",
            status_code=status.HTTP_201_CREATED,
        )
    except ValueError as e:
        return error_response(
            message=str(e),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

@router.get("/")
async def get_purchase_orders(
    *,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_order: str = Query("desc", description="Sort order (asc or desc)"),
    vendor_id: Optional[UUID] = Query(None, description="Filter by vendor"),
    status: Optional[str] = Query(None, description="Filter by status"),
) -> Any:
    """
    Get list of purchase orders with pagination and filtering.
    """
    # Build filters
    filters = {}
    if vendor_id:
        filters["vendor_id"] = vendor_id
    if status:
        filters["status"] = status
    
    result = await purchase_order_crud.get_paginated(
        db,
        page=page,
        page_size=page_size,
        filters=filters,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    
    return success_response(
        data=result["items"],
        meta={
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": result["pagination"]["total"],
                "pages": result["pagination"]["total_pages"],
            }
        },
    )

@router.get("/{po_id}", response_model=PurchaseOrderResponse)
async def get_purchase_order(
    *,
    db: AsyncSession = Depends(get_db),
    po_id: UUID,
) -> Any:
    """
    Get a specific purchase order by ID.
    """
    po = await purchase_order_crud.get(db, id=po_id)
    if not po:
        return error_response(
            message="Purchase order not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    
    return success_response(data=po)

@router.put("/{po_id}", response_model=PurchaseOrderResponse)
async def update_purchase_order(
    *,
    db: AsyncSession = Depends(get_db),
    po_id: UUID,
    po_in: PurchaseOrderUpdate,
) -> Any:
    """
    Update a purchase order.
    """
    po = await purchase_order_crud.get(db, id=po_id)
    if not po:
        return error_response(
            message="Purchase order not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    
    po = await purchase_order_crud.update(db, db_obj=po, obj_in=po_in)
    return success_response(
        data=po,
        message="Purchase order updated successfully",
    )

@router.post("/{po_id}/receive")
async def receive_purchase_order(
    *,
    db: AsyncSession = Depends(get_db),
    po_id: UUID,
    receipt_in: PurchaseOrderReceiptCreate,
) -> Any:
    """
    Receive items from a purchase order.
    """
    try:
        # Ensure the receipt is for the correct PO
        receipt_in.purchase_order_id = po_id
        
        receipt = await purchase_order_crud.receive_items(db, receipt_in=receipt_in)
        return success_response(
            data=receipt,
            message="Items received successfully",
        )
    except ValueError as e:
        return error_response(
            message=str(e),
            status_code=status.HTTP_400_BAD_REQUEST,
        )