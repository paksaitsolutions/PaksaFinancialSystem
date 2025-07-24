"""
API endpoints for inventory item management.
"""
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.session import get_db
from app.core.api_response import success_response, error_response
from app.crud.inventory.item import inventory_item_crud
from app.schemas.inventory.item import (
    InventoryItemCreate,
    InventoryItemUpdate,
    InventoryItemResponse,
)

router = APIRouter()

@router.post("/", response_model=InventoryItemResponse, status_code=status.HTTP_201_CREATED)
async def create_inventory_item(
    *,
    db: AsyncSession = Depends(get_db),
    item_in: InventoryItemCreate,
) -> Any:
    """
    Create a new inventory item.
    """
    # Check if item with same SKU already exists
    existing_item = await inventory_item_crud.get_by_sku(db, sku=item_in.sku)
    if existing_item:
        return error_response(
            message=f"Inventory item with SKU {item_in.sku} already exists",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    
    item = await inventory_item_crud.create(db, obj_in=item_in)
    return success_response(
        data=item,
        message="Inventory item created successfully",
        status_code=status.HTTP_201_CREATED,
    )

@router.get("/")
async def get_inventory_items(
    *,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_order: str = Query("asc", description="Sort order (asc or desc)"),
    name: Optional[str] = Query(None, description="Filter by name"),
    sku: Optional[str] = Query(None, description="Filter by SKU"),
    status: Optional[str] = Query(None, description="Filter by status"),
    category_id: Optional[UUID] = Query(None, description="Filter by category"),
) -> Any:
    """
    Get list of inventory items with pagination and filtering.
    """
    # Build filters
    filters = {}
    if name:
        filters["name"] = name
    if sku:
        filters["sku"] = sku
    if status:
        filters["status"] = status
    if category_id:
        filters["category_id"] = category_id
    
    result = await inventory_item_crud.get_paginated(
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

@router.get("/{item_id}", response_model=InventoryItemResponse)
async def get_inventory_item(
    *,
    db: AsyncSession = Depends(get_db),
    item_id: UUID,
) -> Any:
    """
    Get a specific inventory item by ID.
    """
    item = await inventory_item_crud.get(db, id=item_id)
    if not item:
        return error_response(
            message="Inventory item not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    
    return success_response(data=item)

@router.put("/{item_id}", response_model=InventoryItemResponse)
async def update_inventory_item(
    *,
    db: AsyncSession = Depends(get_db),
    item_id: UUID,
    item_in: InventoryItemUpdate,
) -> Any:
    """
    Update an inventory item.
    """
    item = await inventory_item_crud.get(db, id=item_id)
    if not item:
        return error_response(
            message="Inventory item not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    
    # Check if SKU is being changed and if it already exists
    if item_in.sku and item_in.sku != item.sku:
        existing_item = await inventory_item_crud.get_by_sku(db, sku=item_in.sku)
        if existing_item:
            return error_response(
                message=f"Inventory item with SKU {item_in.sku} already exists",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
    
    item = await inventory_item_crud.update(db, db_obj=item, obj_in=item_in)
    return success_response(
        data=item,
        message="Inventory item updated successfully",
    )

@router.delete("/{item_id}")
async def delete_inventory_item(
    *,
    db: AsyncSession = Depends(get_db),
    item_id: UUID,
) -> Any:
    """
    Delete an inventory item.
    """
    item = await inventory_item_crud.get(db, id=item_id)
    if not item:
        return error_response(
            message="Inventory item not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    
    await inventory_item_crud.delete(db, id=item_id)
    return success_response(
        message="Inventory item deleted successfully",
    )