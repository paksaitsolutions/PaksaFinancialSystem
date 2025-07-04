"""
Accounts Payable API Endpoints
"""
from datetime import date
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.security import (
    get_current_active_superuser,
    get_current_active_user,
    get_current_user,
)
from crud.accounts_payable import bill as crud_bill
from crud.accounts_payable import payment as crud_payment
from models.user import User
from schemas.accounts_payable import (
    BillCreate,
    BillInDB,
    BillStatus,
    BillUpdate,
    BillWithPayments,
    PaymentCreate,
    PaymentInDB,
    PaymentMethod,
    PaymentUpdate,
    PaymentWithBill,
)
from schemas.base import Message, PaginatedResponse

router = APIRouter()

# Helper functions
async def get_bill_or_404(db: AsyncSession, bill_id: UUID) -> BillInDB:
    """Get a bill by ID or raise 404"""
    bill = await crud_bill.get(db, bill_id)
    if not bill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bill not found"
        )
    return bill

async def get_payment_or_404(db: AsyncSession, payment_id: UUID) -> PaymentInDB:
    """Get a payment by ID or raise 404"""
    payment = await crud_payment.get(db, payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    return payment

# Bill endpoints
@router.get(
    "/bills/",
    response_model=PaginatedResponse[BillInDB],
    summary="List bills",
    description="Retrieve a list of bills with optional filtering and pagination."
)
async def list_bills(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    vendor_id: Optional[UUID] = Query(None, description="Filter by vendor ID"),
    status: Optional[BillStatus] = Query(None, description="Filter by status"),
    start_date: Optional[date] = Query(None, description="Filter by start date (inclusive)"),
    end_date: Optional[date] = Query(None, description="Filter by end date (inclusive)"),
    search: Optional[str] = Query(None, description="Search in reference or notes"),
    current_user: User = Depends(get_current_active_user),
):
    """
    List bills with optional filtering and pagination.
    """
    # Apply filters
    filters = {}
    if vendor_id:
        filters["vendor_id"] = vendor_id
    if status:
        filters["status"] = status
    if start_date:
        filters["bill_date__gte"] = start_date
    if end_date:
        filters["bill_date__lte"] = end_date
    
    # Get bills with pagination
    bills, total = await crud_bill.get_multi(
        db,
        skip=skip,
        limit=limit,
        filters=filters,
        search=search,
        order_by="-bill_date"
    )
    
    return {
        "data": bills,
        "total": total,
        "skip": skip,
        "limit": limit,
    }

@router.post(
    "/bills/",
    response_model=BillInDB,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new bill",
    description="Create a new bill with line items."
)
async def create_bill(
    *,
    db: AsyncSession = Depends(get_db),
    bill_in: BillCreate,
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new bill.
    """
    try:
        bill = await crud_bill.create_with_items(
            db,
            obj_in=bill_in,
            created_by_id=current_user.id
        )
        return bill
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get(
    "/bills/{bill_id}",
    response_model=BillWithPayments,
    summary="Get a bill by ID",
    description="Retrieve a specific bill by its ID."
)
async def get_bill(
    *,
    db: AsyncSession = Depends(get_db),
    bill_id: UUID,
    current_user: User = Depends(get_current_active_user),
):
    """
    Get a specific bill by ID.
    """
    bill = await get_bill_or_404(db, bill_id)
    return bill

@router.put(
    "/bills/{bill_id}",
    response_model=BillInDB,
    summary="Update a bill",
    description="Update an existing bill."
)
async def update_bill(
    *,
    db: AsyncSession = Depends(get_db),
    bill_id: UUID,
    bill_in: BillUpdate,
    current_user: User = Depends(get_current_active_user),
):
    """
    Update a bill.
    """
    bill = await get_bill_or_404(db, bill_id)
    
    try:
        updated_bill = await crud_bill.update_with_items(
            db,
            db_obj=bill,
            obj_in=bill_in,
            updated_by_id=current_user.id
        )
        return updated_bill
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete(
    "/bills/{bill_id}",
    response_model=Message,
    summary="Delete a bill",
    description="Delete a bill (soft delete by marking as cancelled)."
)
async def delete_bill(
    *,
    db: AsyncSession = Depends(get_db),
    bill_id: UUID,
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete a bill (soft delete by marking as cancelled).
    """
    bill = await get_bill_or_404(db, bill_id)
    
    try:
        await crud_bill.remove(db, id=bill_id)
        return {"message": "Bill deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post(
    "/bills/{bill_id}/submit",
    response_model=BillInDB,
    summary="Submit a bill for approval",
    description="Submit a draft bill for approval."
)
async def submit_bill_for_approval(
    *,
    db: AsyncSession = Depends(get_db),
    bill_id: UUID,
    current_user: User = Depends(get_current_active_user),
):
    """
    Submit a draft bill for approval.
    """
    bill = await get_bill_or_404(db, bill_id)
    
    try:
        updated_bill = await crud_bill.submit_for_approval(
            db,
            bill_id=bill_id,
            user_id=current_user.id
        )
        return updated_bill
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post(
    "/bills/{bill_id}/approve",
    response_model=BillInDB,
    summary="Approve a bill",
    description="Approve a bill that's awaiting approval."
)
async def approve_bill(
    *,
    db: AsyncSession = Depends(get_db),
    bill_id: UUID,
    current_user: User = Depends(get_current_active_user),
):
    """
    Approve a bill that's awaiting approval.
    """
    bill = await get_bill_or_404(db, bill_id)
    
    try:
        updated_bill = await crud_bill.approve(
            db,
            bill_id=bill_id,
            user_id=current_user.id
        )
        return updated_bill
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# Payment endpoints
@router.get(
    "/payments/",
    response_model=PaginatedResponse[PaymentInDB],
    summary="List payments",
    description="Retrieve a list of payments with optional filtering and pagination."
)
async def list_payments(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    bill_id: Optional[UUID] = Query(None, description="Filter by bill ID"),
    vendor_id: Optional[UUID] = Query(None, description="Filter by vendor ID"),
    method: Optional[PaymentMethod] = Query(None, description="Filter by payment method"),
    start_date: Optional[date] = Query(None, description="Filter by start date (inclusive)"),
    end_date: Optional[date] = Query(None, description="Filter by end date (inclusive)"),
    current_user: User = Depends(get_current_active_user),
):
    """
    List payments with optional filtering and pagination.
    """
    # Apply filters
    filters = {}
    if bill_id:
        filters["bill_id"] = bill_id
    if vendor_id:
        filters["bill__vendor_id"] = vendor_id
    if method:
        filters["payment_method"] = method
    if start_date:
        filters["payment_date__gte"] = start_date
    if end_date:
        filters["payment_date__lte"] = end_date
    
    # Get payments with pagination
    payments, total = await crud_payment.get_multi(
        db,
        skip=skip,
        limit=limit,
        filters=filters,
        order_by="-payment_date"
    )
    
    return {
        "data": payments,
        "total": total,
        "skip": skip,
        "limit": limit,
    }

@router.post(
    "/payments/",
    response_model=PaymentInDB,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new payment",
    description="Create a new payment for a bill."
)
async def create_payment(
    *,
    db: AsyncSession = Depends(get_db),
    payment_in: PaymentCreate,
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new payment for a bill.
    """
    try:
        payment = await crud_payment.create_with_validation(
            db,
            obj_in=payment_in,
            created_by_id=current_user.id
        )
        return payment
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get(
    "/payments/{payment_id}",
    response_model=PaymentWithBill,
    summary="Get a payment by ID",
    description="Retrieve a specific payment by its ID."
)
async def get_payment(
    *,
    db: AsyncSession = Depends(get_db),
    payment_id: UUID,
    current_user: User = Depends(get_current_active_user),
):
    """
    Get a specific payment by ID.
    """
    payment = await get_payment_or_404(db, payment_id)
    return payment

@router.post(
    "/payments/{payment_id}/post",
    response_model=PaymentInDB,
    summary="Post a payment to GL",
    description="Post a payment to the general ledger."
)
async def post_payment(
    *,
    db: AsyncSession = Depends(get_db),
    payment_id: UUID,
    current_user: User = Depends(get_current_active_user),
):
    """
    Post a payment to the general ledger.
    """
    payment = await get_payment_or_404(db, payment_id)
    
    try:
        posted_payment = await crud_payment.post_payment(
            db,
            payment_id=payment_id,
            user_id=current_user.id
        )
        return posted_payment
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# Add vendor endpoints here in the future
# @router.get("/vendors/")
# @router.post("/vendors/")
# etc.
