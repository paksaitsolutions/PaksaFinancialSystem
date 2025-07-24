"""
API endpoints for inventory transaction history.
"""
from typing import Any, Dict, List, Optional
from uuid import UUID
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.session import get_db
from app.core.api_response import success_response, error_response
from app.crud.inventory.transaction import inventory_transaction_crud
from app.schemas.inventory.transaction import InventoryTransactionResponse

router = APIRouter()

@router.get("/", response_model=List[InventoryTransactionResponse])
async def get_transactions(
    *,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_order: str = Query("desc", description="Sort order (asc or desc)"),
    item_id: Optional[UUID] = Query(None, description="Filter by item"),
    location_id: Optional[UUID] = Query(None, description="Filter by location"),
    transaction_type: Optional[str] = Query(None, description="Filter by transaction type"),
    from_date: Optional[date] = Query(None, description="Start date"),
    to_date: Optional[date] = Query(None, description="End date"),
) -> Any:
    """
    Get inventory transaction history with pagination and filtering.
    """
    # Build filters
    filters = {}
    if item_id:
        filters["item_id"] = item_id
    if location_id:
        filters["location_id"] = location_id
    if transaction_type:
        filters["transaction_type"] = transaction_type
    if from_date:
        filters["transaction_date__gte"] = from_date
    if to_date:
        filters["transaction_date__lte"] = to_date
    
    result = await inventory_transaction_crud.get_paginated(
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

@router.get("/{transaction_id}", response_model=InventoryTransactionResponse)
async def get_transaction(
    *,
    db: AsyncSession = Depends(get_db),
    transaction_id: UUID,
) -> Any:
    """
    Get a specific inventory transaction by ID.
    """
    transaction = await inventory_transaction_crud.get(db, id=transaction_id)
    if not transaction:
        return error_response(
            message="Transaction not found",
            status_code=404,
        )
    
    return success_response(data=transaction)

@router.get("/item/{item_id}", response_model=List[InventoryTransactionResponse])
async def get_item_transactions(
    *,
    db: AsyncSession = Depends(get_db),
    item_id: UUID,
    from_date: Optional[date] = Query(None, description="Start date"),
    to_date: Optional[date] = Query(None, description="End date"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of transactions"),
) -> Any:
    """
    Get transaction history for a specific item.
    """
    transactions = await inventory_transaction_crud.get_by_item(
        db,
        item_id=item_id,
        from_date=from_date,
        to_date=to_date,
        limit=limit,
    )
    
    return success_response(data=transactions)