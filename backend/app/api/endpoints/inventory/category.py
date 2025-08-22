"""
API endpoints for inventory category management.
"""
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.session import get_db
from app.core.api_response import success_response, error_response
from app.crud.inventory.category import inventory_category_crud
from app.schemas.inventory.category import (
    InventoryCategoryCreate,
    InventoryCategoryUpdate,
    InventoryCategoryResponse,
)

router = APIRouter()

@router.post("/", response_model=InventoryCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    *,
    db: AsyncSession = Depends(get_db),
    category_in: InventoryCategoryCreate,
) -> Any:
    """
    Create a new inventory category.
    """
    # Check if category with same code already exists
    existing_category = await inventory_category_crud.get_by_code(db, code=category_in.code)
    if existing_category:
        return error_response(
            message=f"Category with code {category_in.code} already exists",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    
    category = await inventory_category_crud.create(db, obj_in=category_in)
    return success_response(
        data=category,
        message="Category created successfully",
        status_code=status.HTTP_201_CREATED,
    )

@router.get("/")
async def get_categories(
    *,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_order: str = Query("asc", description="Sort order (asc or desc)"),
    name: Optional[str] = Query(None, description="Filter by name"),
    code: Optional[str] = Query(None, description="Filter by code"),
) -> Any:
    """
    Get list of inventory categories with pagination and filtering.
    """
    # Build filters
    filters = {}
    if name:
        filters["name"] = name
    if code:
        filters["code"] = code
    
    result = await inventory_category_crud.get_paginated(
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

@router.get("/{category_id}", response_model=InventoryCategoryResponse)
async def get_category(
    *,
    db: AsyncSession = Depends(get_db),
    category_id: UUID,
) -> Any:
    """
    Get a specific inventory category by ID.
    """
    category = await inventory_category_crud.get(db, id=category_id)
    if not category:
        return error_response(
            message="Category not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    
    return success_response(data=category)

@router.put("/{category_id}", response_model=InventoryCategoryResponse)
async def update_category(
    *,
    db: AsyncSession = Depends(get_db),
    category_id: UUID,
    category_in: InventoryCategoryUpdate,
) -> Any:
    """
    Update an inventory category.
    """
    category = await inventory_category_crud.get(db, id=category_id)
    if not category:
        return error_response(
            message="Category not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    
    # Check if code is being changed and if it already exists
    if category_in.code and category_in.code != category.code:
        existing_category = await inventory_category_crud.get_by_code(db, code=category_in.code)
        if existing_category:
            return error_response(
                message=f"Category with code {category_in.code} already exists",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
    
    category = await inventory_category_crud.update(db, db_obj=category, obj_in=category_in)
    return success_response(
        data=category,
        message="Category updated successfully",
    )

@router.delete("/{category_id}")
async def delete_category(
    *,
    db: AsyncSession = Depends(get_db),
    category_id: UUID,
) -> Any:
    """
    Delete an inventory category.
    """
    try:
        category = await inventory_category_crud.delete(db, id=category_id)
        if not category:
            return error_response(
                message="Category not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        
        return success_response(
            message="Category deleted successfully",
        )
    except ValueError as e:
        return error_response(
            message=str(e),
            status_code=status.HTTP_400_BAD_REQUEST,
        )