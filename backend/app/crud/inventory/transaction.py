"""
CRUD operations for inventory transactions.
"""
from typing import Any, Dict, List, Optional
from uuid import UUID
from datetime import date

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.db.query_helper import QueryHelper
from app.models.inventory import InventoryTransaction, InventoryItem, InventoryLocation

class InventoryTransactionCRUD:
    """CRUD operations for inventory transactions."""
    
    def __init__(self):
        """Initialize with query helper."""
        self.query_helper = QueryHelper(InventoryTransaction)
    
    async def get(self, db: AsyncSession, id: UUID) -> Optional[InventoryTransaction]:
        """Get an inventory transaction by ID."""
        query = select(InventoryTransaction).where(InventoryTransaction.id == id).options(
            selectinload(InventoryTransaction.item),
            selectinload(InventoryTransaction.location)
        )
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
        sort_order: str = "desc"
    ) -> List[InventoryTransaction]:
        """Get multiple inventory transactions."""
        query = self.query_helper.build_query(
            filters=filters,
            sort_by=sort_by or "transaction_date",
            sort_order=sort_order,
            skip=skip,
            limit=limit,
            eager_load=["item", "location"]
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
        sort_order: str = "desc"
    ) -> Dict[str, Any]:
        """Get paginated inventory transactions."""
        return await self.query_helper.get_paginated(
            db,
            filters=filters,
            sort_by=sort_by or "transaction_date",
            sort_order=sort_order,
            page=page,
            page_size=page_size,
            eager_load=["item", "location"]
        )
    
    async def get_by_item(
        self,
        db: AsyncSession,
        *,
        item_id: UUID,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        limit: int = 100
    ) -> List[InventoryTransaction]:
        """Get transactions for a specific item."""
        query = select(InventoryTransaction).where(InventoryTransaction.item_id == item_id)
        
        if from_date:
            query = query.where(InventoryTransaction.transaction_date >= from_date)
        if to_date:
            query = query.where(InventoryTransaction.transaction_date <= to_date)
        
        query = query.order_by(InventoryTransaction.transaction_date.desc()).limit(limit)
        query = query.options(
            selectinload(InventoryTransaction.item),
            selectinload(InventoryTransaction.location)
        )
        
        result = await db.execute(query)
        return result.scalars().all()

# Create an instance for dependency injection
inventory_transaction_crud = InventoryTransactionCRUD()