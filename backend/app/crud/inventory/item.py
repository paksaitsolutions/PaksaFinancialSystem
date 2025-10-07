"""
CRUD operations for inventory items.
"""
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.db.query_helper import QueryHelper
from app.models.inventory import InventoryItem
from app.schemas.inventory.item import InventoryItemCreate, InventoryItemUpdate

class InventoryItemCRUD:
    """CRUD operations for inventory items."""
    
    def __init__(self):
        """Initialize with query helper."""
        self.query_helper = QueryHelper(InventoryItem)
    
    async def create(self, db: AsyncSession, *, obj_in: InventoryItemCreate) -> InventoryItem:
        """Create a new inventory item."""
        db_obj = InventoryItem(**obj_in.dict())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get(self, db: AsyncSession, id: UUID) -> Optional[InventoryItem]:
        """Get an inventory item by ID."""
        query = select(InventoryItem).where(InventoryItem.id == id).options(
            selectinload(InventoryItem.category),
            selectinload(InventoryItem.default_location)
        )
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_by_sku(self, db: AsyncSession, sku: str) -> Optional[InventoryItem]:
        """Get an inventory item by SKU."""
        query = select(InventoryItem).where(InventoryItem.sku == sku)
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> List[InventoryItem]:
        """Get multiple inventory items."""
        query = self.query_helper.build_query(
            filters=filters,
            sort_by=sort_by or "name",
            sort_order=sort_order,
            skip=skip,
            limit=limit,
            eager_load=["category", "default_location"]
        )
        return await self.query_helper.execute_query(db, query)
    
    async def get_paginated(
        self,
        db: AsyncSession,
        *,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> Dict[str, Any]:
        """Get paginated inventory items."""
        return await self.query_helper.get_paginated(
            db,
            filters=filters,
            sort_by=sort_by or "name",
            sort_order=sort_order,
            page=page,
            page_size=page_size,
            eager_load=["category", "default_location"]
        )
    
    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: InventoryItem,
        obj_in: Union[InventoryItemUpdate, Dict[str, Any]]
    ) -> InventoryItem:
        """Update an inventory item."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        for field in update_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def delete(self, db: AsyncSession, *, id: UUID) -> Optional[InventoryItem]:
        """Delete an inventory item."""
        item = await self.get(db, id)
        if item:
            await db.delete(item)
            await db.commit()
        return item

# Create an instance for dependency injection
inventory_item_crud = InventoryItemCRUD()