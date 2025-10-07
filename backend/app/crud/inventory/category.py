"""
CRUD operations for inventory categories.
"""
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.db.query_helper import QueryHelper
from app.models.inventory import InventoryCategory, InventoryItem
from app.schemas.inventory.category import InventoryCategoryCreate, InventoryCategoryUpdate

class InventoryCategoryCRUD:
    """CRUD operations for inventory categories."""
    
    def __init__(self):
        """Initialize with query helper."""
        self.query_helper = QueryHelper(InventoryCategory)
    
    async def create(self, db: AsyncSession, *, obj_in: InventoryCategoryCreate) -> InventoryCategory:
        """Create a new inventory category."""
        db_obj = InventoryCategory(**obj_in.dict())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get(self, db: AsyncSession, id: UUID) -> Optional[InventoryCategory]:
        """Get an inventory category by ID."""
        query = select(InventoryCategory).where(InventoryCategory.id == id).options(
            selectinload(InventoryCategory.parent)
        )
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_by_code(self, db: AsyncSession, code: str) -> Optional[InventoryCategory]:
        """Get an inventory category by code."""
        query = select(InventoryCategory).where(InventoryCategory.code == code)
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
    ) -> List[InventoryCategory]:
        """Get multiple inventory categories."""
        query = self.query_helper.build_query(
            filters=filters,
            sort_by=sort_by or "name",
            sort_order=sort_order,
            skip=skip,
            limit=limit,
            eager_load=["parent"]
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
        """Get paginated inventory categories."""
        return await self.query_helper.get_paginated(
            db,
            filters=filters,
            sort_by=sort_by or "name",
            sort_order=sort_order,
            page=page,
            page_size=page_size,
            eager_load=["parent"]
        )
    
    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: InventoryCategory,
        obj_in: Union[InventoryCategoryUpdate, Dict[str, Any]]
    ) -> InventoryCategory:
        """Update an inventory category."""
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
    
    async def delete(self, db: AsyncSession, *, id: UUID) -> Optional[InventoryCategory]:
        """Delete an inventory category."""
        category = await self.get(db, id)
        if category:
            # Check if category has items
            item_count_query = select(func.count()).select_from(InventoryItem).where(InventoryItem.category_id == id)
            item_count_result = await db.execute(item_count_query)
            item_count = item_count_result.scalar()
            
            if item_count > 0:
                raise ValueError(f"Cannot delete category with {item_count} items")
            
            await db.delete(category)
            await db.commit()
        return category

# Create an instance for dependency injection
inventory_category_crud = InventoryCategoryCRUD()