"""
CRUD operations for barcode scanning.
"""
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inventory import InventoryItem

class BarcodeCRUD:
    """CRUD operations for barcode scanning."""
    
    async def get_item_by_barcode(self, db: AsyncSession, barcode: str) -> Optional[InventoryItem]:
        """Get inventory item by barcode."""
        query = select(InventoryItem).where(InventoryItem.barcode == barcode)
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_item_by_sku_or_barcode(self, db: AsyncSession, code: str) -> Optional[InventoryItem]:
        """Get inventory item by SKU or barcode."""
        query = select(InventoryItem).where(
            (InventoryItem.sku == code) | (InventoryItem.barcode == code)
        )
        result = await db.execute(query)
        return result.scalars().first()

# Create an instance for dependency injection
barcode_crud = BarcodeCRUD()