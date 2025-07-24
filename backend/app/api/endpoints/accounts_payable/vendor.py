"""
API endpoints for vendor management.
"""
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.session import get_db
from app.core.api_response import success_response, error_response, paginated_response
from app.crud.accounts_payable.vendor import vendor_crud
from app.schemas.accounts_payable.vendor import (
    VendorCreate,
    VendorUpdate,
    VendorResponse,
    VendorListResponse,
)

router = APIRouter()

@router.post("/", response_model=VendorResponse, status_code=status.HTTP_201_CREATED)
async def create_vendor(
    *,
    db: AsyncSession = Depends(get_db),
    vendor_in: VendorCreate,
) -> Any:
    """
    Create a new vendor.
    """
    # Check if vendor with same code already exists
    existing_vendor = await vendor_crud.get_by_code(db, code=vendor_in.code)
    if existing_vendor:
        return error_response(
            message=f"Vendor with code {vendor_in.code} already exists",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    
    vendor = await vendor_crud.create(db, obj_in=vendor_in)
    return success_response(
        data=vendor,
        message="Vendor created successfully",
        status_code=status.HTTP_201_CREATED,
    )

@router.get("/", response_model=VendorListResponse)
async def get_vendors(
    *,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_order: str = Query("asc", description="Sort order (asc or desc)"),
    name: Optional[str] = Query(None, description="Filter by name"),
    code: Optional[str] = Query(None, description="Filter by code"),
    status: Optional[str] = Query(None, description="Filter by status"),
    is_1099: Optional[bool] = Query(None, description="Filter by 1099 status"),
) -> Any:
    """
    Get list of vendors with pagination and filtering.
    """
    # Build filters
    filters = {}
    if name:
        filters["name"] = name
    if code:
        filters["code"] = code
    if status:
        filters["status"] = status
    if is_1099 is not None:
        filters["is_1099"] = is_1099
    
    result = await vendor_crud.get_paginated(
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

@router.get("/{vendor_id}", response_model=VendorResponse)
async def get_vendor(
    *,
    db: AsyncSession = Depends(get_db),
    vendor_id: UUID,
) -> Any:
    """
    Get a specific vendor by ID.
    """
    vendor = await vendor_crud.get(db, id=vendor_id)
    if not vendor:
        return error_response(
            message="Vendor not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    
    return success_response(data=vendor)

@router.put("/{vendor_id}", response_model=VendorResponse)
async def update_vendor(
    *,
    db: AsyncSession = Depends(get_db),
    vendor_id: UUID,
    vendor_in: VendorUpdate,
) -> Any:
    """
    Update a vendor.
    """
    vendor = await vendor_crud.get(db, id=vendor_id)
    if not vendor:
        return error_response(
            message="Vendor not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    
    # Check if code is being changed and if it already exists
    if vendor_in.code and vendor_in.code != vendor.code:
        existing_vendor = await vendor_crud.get_by_code(db, code=vendor_in.code)
        if existing_vendor:
            return error_response(
                message=f"Vendor with code {vendor_in.code} already exists",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
    
    vendor = await vendor_crud.update(db, db_obj=vendor, obj_in=vendor_in)
    return success_response(
        data=vendor,
        message="Vendor updated successfully",
    )

@router.delete("/{vendor_id}", response_model=Dict[str, Any])
async def delete_vendor(
    *,
    db: AsyncSession = Depends(get_db),
    vendor_id: UUID,
) -> Any:
    """
    Delete a vendor.
    """
    vendor = await vendor_crud.get(db, id=vendor_id)
    if not vendor:
        return error_response(
            message="Vendor not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    
    await vendor_crud.delete(db, id=vendor_id)
    return success_response(
        message="Vendor deleted successfully",
    )