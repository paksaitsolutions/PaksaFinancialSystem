"""
CRUD operations for inventory locations.
"""
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.query_helper import QueryHelper
from app.models.inventory.item import InventoryLocation, InventoryItem
from app.schemas.inventory.location import InventoryLocationCreate, InventoryLocationUpdate

class InventoryLocationCRUD:
    """CRUD operations for inventory locations."""
    
    def __init__(self):
        """Initialize with query helper."""
        self.query_helper = QueryHelper(InventoryLocation)
    
    async def create(self, db: AsyncSession, *, obj_in: InventoryLocationCreate) -> InventoryLocation:
        """Create a new inventory location."""
        db_obj = InventoryLocation(**obj_in.dict())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get(self, db: AsyncSession, id: UUID) -> Optional[InventoryLocation]:
        """Get an inventory location by ID."""
        query = select(InventoryLocation).where(InventoryLocation.id == id)
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_by_code(self, db: AsyncSession, code: str) -> Optional[InventoryLocation]:
        """Get an inventory location by code."""
        query = select(InventoryLocation).where(InventoryLocation.code == code)
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
    ) -> List[InventoryLocation]:
        """Get multiple inventory locations."""
        query = self.query_helper.build_query(
            filters=filters,
            sort_by=sort_by or "name",
            sort_order=sort_order,
            skip=skip,
            limit=limit
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
        """Get paginated inventory locations."""
        return await self.query_helper.get_paginated(
            db,
            filters=filters,
            sort_by=sort_by or "name",
            sort_order=sort_order,
            page=page,
            page_size=page_size
        )
    
    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: InventoryLocation,
        obj_in: Union[InventoryLocationUpdate, Dict[str, Any]]
    ) -> InventoryLocation:
        """Update an inventory location."""
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
    
    async def delete(self, db: AsyncSession, *, id: UUID) -> Optional[InventoryLocation]:
        """Delete an inventory location."""
        location = await self.get(db, id)
        if location:
            # Check if location has items
            item_count_query = select(func.count()).select_from(InventoryItem).where(InventoryItem.default_location_id == id)
            item_count_result = await db.execute(item_count_query)
            item_count = item_count_result.scalar()
            
            if item_count > 0:
                raise ValueError(f"Cannot delete location with {item_count} items")
            
            await db.delete(location)
            await db.commit()
        return location

# Create an instance for dependency injection
inventory_location_crud = InventoryLocationCRUD()