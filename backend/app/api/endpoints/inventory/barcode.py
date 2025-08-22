"""
API endpoints for barcode scanning.
"""
from typing import Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.session import get_db
from app.core.api_response import success_response, error_response
from app.crud.inventory.barcode import barcode_crud
from app.schemas.inventory.item import InventoryItemResponse

router = APIRouter()

@router.get("/lookup", response_model=InventoryItemResponse)
async def lookup_item_by_barcode(
    *,
    db: AsyncSession = Depends(get_db),
    code: str = Query(..., description="Barcode or SKU to lookup"),
) -> Any:
    """
    Lookup inventory item by barcode or SKU.
    """
    item = await barcode_crud.get_item_by_sku_or_barcode(db, code=code)
    if not item:
        return error_response(
            message="Item not found",
            status_code=404,
        )
    
    return success_response(data=item)