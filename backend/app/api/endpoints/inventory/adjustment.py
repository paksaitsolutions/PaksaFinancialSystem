"""
API endpoints for inventory adjustments.
"""
from typing import Any
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.session import get_db
from app.core.api_response import success_response, error_response
from app.crud.inventory.adjustment import inventory_adjustment_crud
from app.schemas.inventory.adjustment import (
    InventoryAdjustmentCreate,
    InventoryAdjustmentResponse,
)

router = APIRouter()

@router.post("/", response_model=InventoryAdjustmentResponse, status_code=status.HTTP_201_CREATED)
async def create_adjustment(
    *,
    db: AsyncSession = Depends(get_db),
    adjustment_in: InventoryAdjustmentCreate,
) -> Any:
    """
    Create an inventory adjustment.
    """
    try:
        adjustment = await inventory_adjustment_crud.create_adjustment(db, adjustment_in=adjustment_in)
        return success_response(
            data=adjustment,
            message="Inventory adjustment created successfully",
            status_code=status.HTTP_201_CREATED,
        )
    except ValueError as e:
        return error_response(
            message=str(e),
            status_code=status.HTTP_400_BAD_REQUEST,
        )