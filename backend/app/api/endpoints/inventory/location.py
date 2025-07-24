"""
API endpoints for inventory location management.
"""
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.session import get_db
from app.core.api_response import success_response, error_response
from app.crud.inventory.location import inventory_location_crud
from app.schemas.inventory.location import (
    InventoryLocationCreate,
    InventoryLocationUpdate,
    InventoryLocationResponse,
)

router = APIRouter()

@router.post("/", response_model=InventoryLocationResponse, status_code=status.HTTP_201_CREATED)
async def create_location(
    *,
    db: AsyncSession = Depends(get_db),
    location_in: InventoryLocationCreate,
) -> Any:
    """
    Create a new inventory location.
    """
    # Check if location with same code already exists
    existing_location = await inventory_location_crud.get_by_code(db, code=location_in.code)
    if existing_location:
        return error_response(
            message=f"Location with code {location_in.code} already exists",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    
    location = await inventory_location_crud.create(db, obj_in=location_in)
    return success_response(
        data=location,
        message="Location created successfully",
        status_code=status.HTTP_201_CREATED,
    )

@router.get("/")
async def get_locations(
    *,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_order: str = Query("asc", description="Sort order (asc or desc)"),
    name: Optional[str] = Query(None, description="Filter by name"),
    code: Optional[str] = Query(None, description="Filter by code"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
) -> Any:
    """
    Get list of inventory locations with pagination and filtering.
    """
    # Build filters
    filters = {}
    if name:
        filters["name"] = name
    if code:
        filters["code"] = code
    if is_active is not None:
        filters["is_active"] = is_active
    
    result = await inventory_location_crud.get_paginated(
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

@router.get("/{location_id}", response_model=InventoryLocationResponse)
async def get_location(
    *,
    db: AsyncSession = Depends(get_db),
    location_id: UUID,
) -> Any:
    """
    Get a specific inventory location by ID.
    """
    location = await inventory_location_crud.get(db, id=location_id)
    if not location:
        return error_response(
            message="Location not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    
    return success_response(data=location)

@router.put("/{location_id}", response_model=InventoryLocationResponse)
async def update_location(
    *,
    db: AsyncSession = Depends(get_db),
    location_id: UUID,
    location_in: InventoryLocationUpdate,
) -> Any:
    """
    Update an inventory location.
    """
    location = await inventory_location_crud.get(db, id=location_id)
    if not location:
        return error_response(
            message="Location not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    
    # Check if code is being changed and if it already exists
    if location_in.code and location_in.code != location.code:
        existing_location = await inventory_location_crud.get_by_code(db, code=location_in.code)
        if existing_location:
            return error_response(
                message=f"Location with code {location_in.code} already exists",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
    
    location = await inventory_location_crud.update(db, db_obj=location, obj_in=location_in)
    return success_response(
        data=location,
        message="Location updated successfully",
    )

@router.delete("/{location_id}")
async def delete_location(
    *,
    db: AsyncSession = Depends(get_db),
    location_id: UUID,
) -> Any:
    """
    Delete an inventory location.
    """
    try:
        location = await inventory_location_crud.delete(db, id=location_id)
        if not location:
            return error_response(
                message="Location not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        
        return success_response(
            message="Location deleted successfully",
        )
    except ValueError as e:
        return error_response(
            message=str(e),
            status_code=status.HTTP_400_BAD_REQUEST,
        )