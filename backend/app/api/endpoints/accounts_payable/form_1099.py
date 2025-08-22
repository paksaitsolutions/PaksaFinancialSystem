"""
API endpoints for 1099 reporting.
"""
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.session import get_db
from app.core.api_response import success_response, error_response
from app.crud.accounts_payable.form_1099 import form_1099_crud
from app.schemas.accounts_payable.form_1099 import (
    Form1099Create,
    Form1099Update,
    Form1099Response,
    Form1099ListResponse,
    Form1099GenerateRequest,
    Form1099SummaryResponse,
)

router = APIRouter()

@router.post("/", response_model=Form1099Response, status_code=status.HTTP_201_CREATED)
async def create_1099_form(
    *,
    db: AsyncSession = Depends(get_db),
    form_in: Form1099Create,
) -> Any:
    """
    Create a new 1099 form.
    """
    try:
        form = await form_1099_crud.create(db, obj_in=form_in)
        return success_response(
            data=form,
            message="1099 form created successfully",
            status_code=status.HTTP_201_CREATED,
        )
    except ValueError as e:
        return error_response(
            message=str(e),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

@router.get("/", response_model=Form1099ListResponse)
async def get_1099_forms(
    *,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_order: str = Query("desc", description="Sort order (asc or desc)"),
    tax_year: Optional[int] = Query(None, description="Filter by tax year"),
    vendor_id: Optional[UUID] = Query(None, description="Filter by vendor ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
) -> Any:
    """
    Get list of 1099 forms with pagination and filtering.
    """
    # Build filters
    filters = {}
    if tax_year:
        filters["tax_year"] = tax_year
    if vendor_id:
        filters["vendor_id"] = vendor_id
    if status:
        filters["status"] = status
    
    result = await form_1099_crud.get_paginated(
        db,
        page=page,
        page_size=page_size,
        filters=filters,
        sort_by=sort_by or "tax_year",
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

@router.get("/{form_id}", response_model=Form1099Response)
async def get_1099_form(
    *,
    db: AsyncSession = Depends(get_db),
    form_id: UUID,
) -> Any:
    """
    Get a specific 1099 form by ID.
    """
    form = await form_1099_crud.get(db, id=form_id)
    if not form:
        return error_response(
            message="1099 form not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    
    return success_response(data=form)

@router.put("/{form_id}", response_model=Form1099Response)
async def update_1099_form(
    *,
    db: AsyncSession = Depends(get_db),
    form_id: UUID,
    form_in: Form1099Update,
) -> Any:
    """
    Update a 1099 form.
    """
    form = await form_1099_crud.get(db, id=form_id)
    if not form:
        return error_response(
            message="1099 form not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    
    # Check if form can be updated
    if form.status in ["filed", "voided"]:
        return error_response(
            message=f"1099 form in '{form.status}' status cannot be updated",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    
    form = await form_1099_crud.update(db, db_obj=form, obj_in=form_in)
    return success_response(
        data=form,
        message="1099 form updated successfully",
    )

@router.post("/generate", response_model=List[Form1099Response])
async def generate_1099_forms(
    *,
    db: AsyncSession = Depends(get_db),
    generate_request: Form1099GenerateRequest = Body(...),
) -> Any:
    """
    Generate 1099 forms for a tax year.
    """
    try:
        forms = await form_1099_crud.generate_forms(db, request=generate_request)
        return success_response(
            data=forms,
            message=f"Generated {len(forms)} 1099 forms",
        )
    except ValueError as e:
        return error_response(
            message=str(e),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

@router.post("/{form_id}/file", response_model=Form1099Response)
async def file_1099_form(
    *,
    db: AsyncSession = Depends(get_db),
    form_id: UUID,
) -> Any:
    """
    Mark a 1099 form as filed.
    """
    form = await form_1099_crud.get(db, id=form_id)
    if not form:
        return error_response(
            message="1099 form not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    
    try:
        form = await form_1099_crud.file_form(db, db_obj=form)
        return success_response(
            data=form,
            message="1099 form filed successfully",
        )
    except ValueError as e:
        return error_response(
            message=str(e),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

@router.post("/{form_id}/void", response_model=Form1099Response)
async def void_1099_form(
    *,
    db: AsyncSession = Depends(get_db),
    form_id: UUID,
    reason: str = Body(..., embed=True),
) -> Any:
    """
    Void a 1099 form.
    """
    form = await form_1099_crud.get(db, id=form_id)
    if not form:
        return error_response(
            message="1099 form not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    
    try:
        form = await form_1099_crud.void_form(db, db_obj=form, reason=reason)
        return success_response(
            data=form,
            message="1099 form voided successfully",
        )
    except ValueError as e:
        return error_response(
            message=str(e),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

@router.get("/summary/{tax_year}", response_model=Form1099SummaryResponse)
async def get_1099_summary(
    *,
    db: AsyncSession = Depends(get_db),
    tax_year: int,
) -> Any:
    """
    Get 1099 summary for a tax year.
    """
    summary = await form_1099_crud.get_summary(db, tax_year=tax_year)
    return success_response(data=summary)