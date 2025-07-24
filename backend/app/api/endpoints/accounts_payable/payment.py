"""
API endpoints for payment processing.
"""
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.session import get_db
from app.core.api_response import success_response, error_response
from app.crud.accounts_payable.payment import payment_crud
from app.crud.accounts_payable.invoice import invoice_crud
from app.schemas.accounts_payable.payment import (
    PaymentCreate,
    PaymentUpdate,
    PaymentResponse,
    PaymentListResponse,
    PaymentVoidRequest,
)

router = APIRouter()

@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    *,
    db: AsyncSession = Depends(get_db),
    payment_in: PaymentCreate,
) -> Any:
    """
    Create a new payment.
    """
    try:
        payment = await payment_crud.create(db, obj_in=payment_in)
        return success_response(
            data=payment,
            message="Payment created successfully",
            status_code=status.HTTP_201_CREATED,
        )
    except ValueError as e:
        return error_response(
            message=str(e),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

@router.get("/", response_model=PaymentListResponse)
async def get_payments(
    *,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_order: str = Query("desc", description="Sort order (asc or desc)"),
    vendor_id: Optional[UUID] = Query(None, description="Filter by vendor ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    from_date: Optional[str] = Query(None, description="Filter by payment date (from)"),
    to_date: Optional[str] = Query(None, description="Filter by payment date (to)"),
) -> Any:
    """
    Get list of payments with pagination and filtering.
    """
    # Build filters
    filters = {}
    if vendor_id:
        filters["vendor_id"] = vendor_id
    if status:
        filters["status"] = status
    if from_date:
        filters["payment_date_from"] = from_date
    if to_date:
        filters["payment_date_to"] = to_date
    
    result = await payment_crud.get_paginated(
        db,
        page=page,
        page_size=page_size,
        filters=filters,
        sort_by=sort_by or "payment_date",
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

@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    *,
    db: AsyncSession = Depends(get_db),
    payment_id: UUID,
) -> Any:
    """
    Get a specific payment by ID.
    """
    payment = await payment_crud.get(db, id=payment_id)
    if not payment:
        return error_response(
            message="Payment not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    
    return success_response(data=payment)

@router.put("/{payment_id}", response_model=PaymentResponse)
async def update_payment(
    *,
    db: AsyncSession = Depends(get_db),
    payment_id: UUID,
    payment_in: PaymentUpdate,
) -> Any:
    """
    Update a payment.
    """
    payment = await payment_crud.get(db, id=payment_id)
    if not payment:
        return error_response(
            message="Payment not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    
    # Check if payment can be updated (not in final status)
    if payment.status in ["voided"]:
        return error_response(
            message=f"Payment in '{payment.status}' status cannot be updated",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    
    payment = await payment_crud.update(db, db_obj=payment, obj_in=payment_in)
    return success_response(
        data=payment,
        message="Payment updated successfully",
    )

@router.post("/{payment_id}/void", response_model=PaymentResponse)
async def void_payment(
    *,
    db: AsyncSession = Depends(get_db),
    payment_id: UUID,
    void_data: PaymentVoidRequest = Body(...),
) -> Any:
    """
    Void a payment.
    """
    payment = await payment_crud.get(db, id=payment_id)
    if not payment:
        return error_response(
            message="Payment not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    
    try:
        payment = await payment_crud.void(db, db_obj=payment, reason=void_data.reason)
        return success_response(
            data=payment,
            message="Payment voided successfully",
        )
    except ValueError as e:
        return error_response(
            message=str(e),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

@router.get("/invoice/{invoice_id}", response_model=List[PaymentResponse])
async def get_payments_for_invoice(
    *,
    db: AsyncSession = Depends(get_db),
    invoice_id: UUID,
) -> Any:
    """
    Get all payments for a specific invoice.
    """
    # First check if invoice exists
    invoice = await invoice_crud.get(db, id=invoice_id)
    if not invoice:
        return error_response(
            message="Invoice not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    
    # Return payments
    return success_response(
        data=invoice.payments,
    )