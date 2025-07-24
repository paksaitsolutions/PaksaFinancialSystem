"""
API endpoints for credit memo management.
"""
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.session import get_db
from app.core.api_response import success_response, error_response
from app.crud.accounts_payable.credit_memo import credit_memo_crud
from app.schemas.accounts_payable.credit_memo import (
    CreditMemoCreate,
    CreditMemoUpdate,
    CreditMemoResponse,
    CreditMemoListResponse,
    CreditMemoApplicationRequest,
    CreditMemoVoidRequest,
)

router = APIRouter()

@router.post("/", response_model=CreditMemoResponse, status_code=status.HTTP_201_CREATED)
async def create_credit_memo(
    *,
    db: AsyncSession = Depends(get_db),
    credit_memo_in: CreditMemoCreate,
) -> Any:
    """
    Create a new credit memo.
    """
    try:
        credit_memo = await credit_memo_crud.create(db, obj_in=credit_memo_in)
        return success_response(
            data=credit_memo,
            message="Credit memo created successfully",
            status_code=status.HTTP_201_CREATED,
        )
    except ValueError as e:
        return error_response(
            message=str(e),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

@router.get("/", response_model=CreditMemoListResponse)
async def get_credit_memos(
    *,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_order: str = Query("desc", description="Sort order (asc or desc)"),
    vendor_id: Optional[UUID] = Query(None, description="Filter by vendor ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    from_date: Optional[str] = Query(None, description="Filter by credit date (from)"),
    to_date: Optional[str] = Query(None, description="Filter by credit date (to)"),
) -> Any:
    """
    Get list of credit memos with pagination and filtering.
    """
    # Build filters
    filters = {}
    if vendor_id:
        filters["vendor_id"] = vendor_id
    if status:
        filters["status"] = status
    if from_date:
        filters["credit_date_from"] = from_date
    if to_date:
        filters["credit_date_to"] = to_date
    
    result = await credit_memo_crud.get_paginated(
        db,
        page=page,
        page_size=page_size,
        filters=filters,
        sort_by=sort_by or "credit_date",
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

@router.get("/{credit_memo_id}", response_model=CreditMemoResponse)
async def get_credit_memo(
    *,
    db: AsyncSession = Depends(get_db),
    credit_memo_id: UUID,
) -> Any:
    """
    Get a specific credit memo by ID.
    """
    credit_memo = await credit_memo_crud.get(db, id=credit_memo_id)
    if not credit_memo:
        return error_response(
            message="Credit memo not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    
    return success_response(data=credit_memo)

@router.put("/{credit_memo_id}", response_model=CreditMemoResponse)
async def update_credit_memo(
    *,
    db: AsyncSession = Depends(get_db),
    credit_memo_id: UUID,
    credit_memo_in: CreditMemoUpdate,
) -> Any:
    """
    Update a credit memo.
    """
    credit_memo = await credit_memo_crud.get(db, id=credit_memo_id)
    if not credit_memo:
        return error_response(
            message="Credit memo not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    
    # Check if credit memo can be updated
    if credit_memo.status in ["voided"]:
        return error_response(
            message=f"Credit memo in '{credit_memo.status}' status cannot be updated",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    
    credit_memo = await credit_memo_crud.update(db, db_obj=credit_memo, obj_in=credit_memo_in)
    return success_response(
        data=credit_memo,
        message="Credit memo updated successfully",
    )

@router.post("/{credit_memo_id}/apply", response_model=CreditMemoResponse)
async def apply_credit_memo(
    *,
    db: AsyncSession = Depends(get_db),
    credit_memo_id: UUID,
    application_request: CreditMemoApplicationRequest = Body(...),
) -> Any:
    """
    Apply credit memo to invoices.
    """
    credit_memo = await credit_memo_crud.get(db, id=credit_memo_id)
    if not credit_memo:
        return error_response(
            message="Credit memo not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    
    try:
        credit_memo = await credit_memo_crud.apply_to_invoices(
            db, 
            db_obj=credit_memo, 
            application_request=application_request
        )
        return success_response(
            data=credit_memo,
            message="Credit memo applied successfully",
        )
    except ValueError as e:
        return error_response(
            message=str(e),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

@router.post("/{credit_memo_id}/void", response_model=CreditMemoResponse)
async def void_credit_memo(
    *,
    db: AsyncSession = Depends(get_db),
    credit_memo_id: UUID,
    void_data: CreditMemoVoidRequest = Body(...),
) -> Any:
    """
    Void a credit memo.
    """
    credit_memo = await credit_memo_crud.get(db, id=credit_memo_id)
    if not credit_memo:
        return error_response(
            message="Credit memo not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    
    try:
        credit_memo = await credit_memo_crud.void(db, db_obj=credit_memo, reason=void_data.reason)
        return success_response(
            data=credit_memo,
            message="Credit memo voided successfully",
        )
    except ValueError as e:
        return error_response(
            message=str(e),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

@router.get("/vendor/{vendor_id}", response_model=List[CreditMemoResponse])
async def get_vendor_credit_memos(
    *,
    db: AsyncSession = Depends(get_db),
    vendor_id: UUID,
    status: Optional[str] = Query("active", description="Filter by status"),
) -> Any:
    """
    Get all credit memos for a specific vendor.
    """
    filters = {"vendor_id": vendor_id}
    if status:
        filters["status"] = status
    
    credit_memos = await credit_memo_crud.get_multi(
        db,
        filters=filters,
        limit=100
    )
    
    return success_response(data=credit_memos)