"""
CRUD operations for inventory adjustments.
"""
from typing import Any, Dict, List, Optional
from uuid import UUID
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inventory.item import InventoryItem
from app.models.inventory.transaction import InventoryTransaction
from app.schemas.inventory.adjustment import InventoryAdjustmentCreate

class InventoryAdjustmentCRUD:
    """CRUD operations for inventory adjustments."""
    
    async def create_adjustment(
        self, 
        db: AsyncSession, 
        *, 
        adjustment_in: InventoryAdjustmentCreate
    ) -> InventoryTransaction:
        """Create an inventory adjustment."""
        # Get the inventory item
        item_query = select(InventoryItem).where(InventoryItem.id == adjustment_in.item_id)
        item_result = await db.execute(item_query)
        item = item_result.scalars().first()
        
        if not item:
            raise ValueError("Inventory item not found")
        
        # Calculate quantities
        quantity_before = item.quantity_on_hand
        quantity_after = quantity_before + adjustment_in.quantity_adjustment
        
        # Create adjustment transaction
        adjustment = InventoryTransaction(
            item_id=adjustment_in.item_id,
            location_id=adjustment_in.location_id,
            transaction_type="adjustment",
            transaction_date=adjustment_in.adjustment_date,
            reference=adjustment_in.reference,
            quantity=adjustment_in.quantity_adjustment,
            unit_cost=item.unit_cost,
            total_cost=adjustment_in.quantity_adjustment * item.unit_cost,
            quantity_before=quantity_before,
            quantity_after=quantity_after,
            notes=f"{adjustment_in.reason}. {adjustment_in.notes or ''}".strip()
        )
        
        # Update item quantities
        item.quantity_on_hand = quantity_after
        item.quantity_available = quantity_after - item.quantity_committed
        
        db.add(adjustment)
        db.add(item)
        await db.commit()
        await db.refresh(adjustment)
        
        return adjustment

# Create an instance for dependency injection
inventory_adjustment_crud = InventoryAdjustmentCRUD()