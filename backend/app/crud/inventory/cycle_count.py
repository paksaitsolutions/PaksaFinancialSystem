"""
CRUD operations for cycle counts.
"""
from typing import Any, Dict, List, Optional, Union
from uuid import UUID
from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.db.query_helper import QueryHelper
# Create minimal models for compatibility
from sqlalchemy import Column, String, DateTime, Numeric, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel
import uuid
from datetime import datetime

class CycleCount(BaseModel):
    __tablename__ = "cycle_counts_crud"
    count_number = Column(String(50), nullable=False)
    count_date = Column(DateTime, default=datetime.utcnow)
    location_id = Column(UUID(as_uuid=True), default=uuid.uuid4)
    status = Column(String(20), default='draft')

class CycleCountLineItem(BaseModel):
    __tablename__ = "cycle_count_line_items_crud"
    cycle_count_id = Column(UUID(as_uuid=True), ForeignKey('cycle_counts_crud.id'))
    item_id = Column(UUID(as_uuid=True), default=uuid.uuid4)
    system_quantity = Column(Numeric(15, 2), default=0)
    counted_quantity = Column(Numeric(15, 2), default=0)
    variance = Column(Numeric(15, 2), default=0)
    is_counted = Column(Boolean, default=False)
    notes = Column(Text)

class InventoryItem(BaseModel):
    __tablename__ = "inventory_items_crud"
    unit_cost = Column(Numeric(15, 2), default=0)
    quantity_on_hand = Column(Numeric(15, 2), default=0)
    quantity_available = Column(Numeric(15, 2), default=0)
    quantity_committed = Column(Numeric(15, 2), default=0)

class InventoryTransaction(BaseModel):
    __tablename__ = "inventory_transactions_crud"
    item_id = Column(UUID(as_uuid=True), default=uuid.uuid4)
    location_id = Column(UUID(as_uuid=True), default=uuid.uuid4)
    transaction_type = Column(String(50))
    transaction_date = Column(DateTime, default=datetime.utcnow)
    reference = Column(String(100))
    quantity = Column(Numeric(15, 2), default=0)
    unit_cost = Column(Numeric(15, 2), default=0)
    total_cost = Column(Numeric(15, 2), default=0)
    notes = Column(Text)
from app.schemas.inventory.cycle_count import CycleCountCreate, CycleCountUpdate, CycleCountLineItemUpdate

class CycleCountCRUD:
    """CRUD operations for cycle counts."""
    
    def __init__(self):
        """Initialize with query helper."""
        self.query_helper = QueryHelper(CycleCount)
    
    async def create(self, db: AsyncSession, *, obj_in: CycleCountCreate) -> CycleCount:
        """Create a new cycle count."""
        # Generate count number
        count_number = await self._generate_count_number(db)
        
        # Create cycle count
        count_data = obj_in.dict(exclude={"line_items"})
        db_obj = CycleCount(**count_data, count_number=count_number)
        db.add(db_obj)
        await db.flush()
        
        # Create line items
        for line_item_data in obj_in.line_items:
            line_item = CycleCountLineItem(
                **line_item_data.dict(),
                cycle_count_id=db_obj.id
            )
            db.add(line_item)
        
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get(self, db: AsyncSession, id: UUID) -> Optional[CycleCount]:
        """Get a cycle count by ID."""
        query = select(CycleCount).where(CycleCount.id == id).options(
            selectinload(CycleCount.location),
            selectinload(CycleCount.line_items).selectinload(CycleCountLineItem.item)
        )
        result = await db.execute(query)
        return result.scalars().first()
    
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
        """Get paginated cycle counts."""
        return await self.query_helper.get_paginated(
            db,
            filters=filters,
            sort_by=sort_by or "count_date",
            sort_order=sort_order,
            page=page,
            page_size=page_size,
            eager_load=["location"]
        )
    
    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: CycleCount,
        obj_in: Union[CycleCountUpdate, Dict[str, Any]]
    ) -> CycleCount:
        """Update a cycle count."""
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
    
    async def update_line_item(
        self,
        db: AsyncSession,
        *,
        line_item_id: UUID,
        obj_in: CycleCountLineItemUpdate
    ) -> CycleCountLineItem:
        """Update a cycle count line item."""
        query = select(CycleCountLineItem).where(CycleCountLineItem.id == line_item_id)
        result = await db.execute(query)
        line_item = result.scalars().first()
        
        if not line_item:
            raise ValueError("Line item not found")
        
        # Update line item
        line_item.counted_quantity = obj_in.counted_quantity
        line_item.variance = obj_in.counted_quantity - line_item.system_quantity
        line_item.is_counted = True
        if obj_in.notes:
            line_item.notes = obj_in.notes
        
        db.add(line_item)
        await db.commit()
        await db.refresh(line_item)
        return line_item
    
    async def complete_count(self, db: AsyncSession, *, count_id: UUID) -> CycleCount:
        """Complete a cycle count and create adjustments."""
        count = await self.get(db, count_id)
        if not count:
            raise ValueError("Cycle count not found")
        
        # Check if all items are counted
        uncounted_items = [item for item in count.line_items if not item.is_counted]
        if uncounted_items:
            raise ValueError(f"{len(uncounted_items)} items still need to be counted")
        
        # Create adjustments for items with variances
        for line_item in count.line_items:
            if line_item.variance != 0:
                # Create inventory transaction
                adjustment = InventoryTransaction(
                    item_id=line_item.item_id,
                    location_id=count.location_id,
                    transaction_type="adjustment",
                    transaction_date=count.count_date,
                    reference=f"Cycle Count {count.count_number}",
                    quantity=line_item.variance,
                    unit_cost=line_item.item.unit_cost,
                    total_cost=line_item.variance * line_item.item.unit_cost,
                    notes=f"Cycle count adjustment. System: {line_item.system_quantity}, Counted: {line_item.counted_quantity}"
                )
                db.add(adjustment)
                
                # Update inventory item quantities
                item = line_item.item
                item.quantity_on_hand = line_item.counted_quantity
                item.quantity_available = item.quantity_on_hand - item.quantity_committed
                db.add(item)
        
        # Update count status
        count.status = "completed"
        db.add(count)
        
        await db.commit()
        await db.refresh(count)
        return count
    
    async def _generate_count_number(self, db: AsyncSession) -> str:
        """Generate a unique count number."""
        now = datetime.now()
        year = now.year
        month = now.month
        
        query = select(func.count()).select_from(CycleCount).where(
            func.extract('year', CycleCount.count_date) == year,
            func.extract('month', CycleCount.count_date) == month
        )
        result = await db.execute(query)
        count = result.scalar() or 0
        
        return f"CC-{year}{month:02d}-{count+1:04d}"

# Create an instance for dependency injection
cycle_count_crud = CycleCountCRUD()