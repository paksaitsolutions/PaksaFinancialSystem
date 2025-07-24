"""
API endpoints for cycle count management.
"""
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.session import get_db
from app.core.api_response import success_response, error_response
from app.crud.inventory.cycle_count import cycle_count_crud
from app.schemas.inventory.cycle_count import (
    CycleCountCreate,
    CycleCountUpdate,
    CycleCountResponse,
    CycleCountLineItemUpdate,
)

router = APIRouter()

@router.post("/", response_model=CycleCountResponse, status_code=status.HTTP_201_CREATED)
async def create_cycle_count(
    *,
    db: AsyncSession = Depends(get_db),
    count_in: CycleCountCreate,
) -> Any:
    """
    Create a new cycle count.
    """
    try:
        count = await cycle_count_crud.create(db, obj_in=count_in)
        return success_response(
            data=count,
            message="Cycle count created successfully",
            status_code=status.HTTP_201_CREATED,
        )
    except ValueError as e:
        return error_response(
            message=str(e),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

@router.get("/")
async def get_cycle_counts(
    *,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_order: str = Query("desc", description="Sort order (asc or desc)"),
    location_id: Optional[UUID] = Query(None, description="Filter by location"),
    status: Optional[str] = Query(None, description="Filter by status"),
) -> Any:
    """
    Get list of cycle counts with pagination and filtering.
    """
    # Build filters
    filters = {}
    if location_id:
        filters["location_id"] = location_id
    if status:
        filters["status"] = status
    
    result = await cycle_count_crud.get_paginated(
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

@router.get("/{count_id}", response_model=CycleCountResponse)
async def get_cycle_count(
    *,
    db: AsyncSession = Depends(get_db),
    count_id: UUID,
) -> Any:
    """
    Get a specific cycle count by ID.
    """
    count = await cycle_count_crud.get(db, id=count_id)
    if not count:
        return error_response(
            message="Cycle count not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    
    return success_response(data=count)

@router.put("/{count_id}", response_model=CycleCountResponse)
async def update_cycle_count(
    *,
    db: AsyncSession = Depends(get_db),
    count_id: UUID,
    count_in: CycleCountUpdate,
) -> Any:
    """
    Update a cycle count.
    """
    count = await cycle_count_crud.get(db, id=count_id)
    if not count:
        return error_response(
            message="Cycle count not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    
    count = await cycle_count_crud.update(db, db_obj=count, obj_in=count_in)
    return success_response(
        data=count,
        message="Cycle count updated successfully",
    )

@router.put("/line-items/{line_item_id}")
async def update_line_item(
    *,
    db: AsyncSession = Depends(get_db),
    line_item_id: UUID,
    line_item_in: CycleCountLineItemUpdate,
) -> Any:
    """
    Update a cycle count line item.
    """
    try:
        line_item = await cycle_count_crud.update_line_item(
            db, line_item_id=line_item_id, obj_in=line_item_in
        )
        return success_response(
            data=line_item,
            message="Line item updated successfully",
        )
    except ValueError as e:
        return error_response(
            message=str(e),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

@router.post("/{count_id}/complete")
async def complete_cycle_count(
    *,
    db: AsyncSession = Depends(get_db),
    count_id: UUID,
) -> Any:
    """
    Complete a cycle count and create adjustments.
    """
    try:
        count = await cycle_count_crud.complete_count(db, count_id=count_id)
        return success_response(
            data=count,
            message="Cycle count completed successfully",
        )
    except ValueError as e:
        return error_response(
            message=str(e),
            status_code=status.HTTP_400_BAD_REQUEST,
        )