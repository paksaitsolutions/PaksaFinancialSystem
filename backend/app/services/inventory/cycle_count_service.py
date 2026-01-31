"""
Cycle counting service.
"""
from datetime import date, datetime
from typing import List, Dict, Any, Optional

from decimal import Decimal
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.models.inventory.item import InventoryItem
from app.models.inventory.transfer import CycleCount, CycleCountItem




class CycleCountService:
    """Cycle counting service."""
    
    async def create_cycle_count(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        count_data: Dict[str, Any]
    ) -> CycleCount:
        """Create Cycle Count."""
        """Create a new cycle count."""
        count_number = await self._generate_count_number(db, tenant_id)
        
        cycle_count = CycleCount(
            tenant_id=tenant_id,
            count_number=count_number,
            **count_data
        )
        db.add(cycle_count)
        await db.commit()
        await db.refresh(cycle_count)
        return cycle_count
    
    async def add_items_to_count(
        self,
        db: AsyncSession,
        cycle_count_id: UUID,
        item_ids: List[UUID]
    ) -> List[CycleCountItem]:
        """Add Items To Count."""
        """Add items to cycle count."""
        count_items = []
        
        for item_id in item_ids:
            # Get current system quantity
            result = await db.execute(
                select(InventoryItem).where(InventoryItem.id == item_id)
            )
            item = result.scalar_one_or_none()
            
            if item:
                count_item = CycleCountItem(
                    cycle_count_id=cycle_count_id,
                    item_id=item_id,
                    system_quantity=item.quantity_on_hand,
                    unit_cost=item.unit_cost
                )
                db.add(count_item)
                count_items.append(count_item)
        
        await db.commit()
        return count_items
    
    async def record_count(
        self,
        db: AsyncSession,
        cycle_count_id: UUID,
        item_id: UUID,
        counted_quantity: Decimal
    ) -> CycleCountItem:
        """Record Count."""
        """Record counted quantity for an item."""
        result = await db.execute(
            select(CycleCountItem).where(
                and_(
                    CycleCountItem.cycle_count_id == cycle_count_id,
                    CycleCountItem.item_id == item_id
                )
            )
        )
        count_item = result.scalar_one_or_none()
        
        if not count_item:
            raise ValueError("Count item not found")
        
        count_item.counted_quantity = counted_quantity
        count_item.variance_quantity = counted_quantity - count_item.system_quantity
        count_item.variance_value = count_item.variance_quantity * count_item.unit_cost
        count_item.is_counted = True
        
        await db.commit()
        await db.refresh(count_item)
        return count_item
    
    async def complete_cycle_count(
        self,
        db: AsyncSession,
        cycle_count_id: UUID,
        completed_by: UUID
    ) -> CycleCount:
        """Complete Cycle Count."""
        """Complete cycle count and calculate variances."""
        result = await db.execute(
            select(CycleCount).where(CycleCount.id == cycle_count_id)
        )
        cycle_count = result.scalar_one_or_none()
        
        if not cycle_count:
            raise ValueError("Cycle count not found")
        
        # Get all count items
        items_result = await db.execute(
            select(CycleCountItem).where(CycleCountItem.cycle_count_id == cycle_count_id)
        )
        items = items_result.scalars().all()
        
        # Calculate totals
        total_items = len(items)
        items_with_variances = len([item for item in items if item.variance_quantity != 0])
        total_variance_value = sum(item.variance_value or 0 for item in items)
        
        # Update cycle count
        cycle_count.status = "completed"
        cycle_count.total_items_counted = total_items
        cycle_count.items_with_variances = items_with_variances
        cycle_count.total_variance_value = total_variance_value
        cycle_count.completed_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(cycle_count)
        return cycle_count
    
    async def get_cycle_count_report(
        self,
        db: AsyncSession,
        cycle_count_id: UUID
    ) -> Dict[str, Any]:
        """Get Cycle Count Report."""
        """Get detailed cycle count report."""
        result = await db.execute(
            select(CycleCount).where(CycleCount.id == cycle_count_id)
        )
        cycle_count = result.scalar_one_or_none()
        
        if not cycle_count:
            raise ValueError("Cycle count not found")
        
        # Get count items with variances
        items_result = await db.execute(
            select(CycleCountItem).where(CycleCountItem.cycle_count_id == cycle_count_id)
        )
        items = items_result.scalars().all()
        
        variance_items = [item for item in items if item.variance_quantity != 0]
        
        return {
            "cycle_count_id": str(cycle_count.id),
            "count_number": cycle_count.count_number,
            "status": cycle_count.status,
            "count_date": cycle_count.count_date.isoformat() if cycle_count.count_date else None,
            "location_id": str(cycle_count.location_id),
            "total_items_counted": cycle_count.total_items_counted,
            "items_with_variances": cycle_count.items_with_variances,
            "total_variance_value": float(cycle_count.total_variance_value or 0),
            "variance_items": [self._serialize_count_item(item) for item in variance_items],
            "accuracy_percentage": self._calculate_accuracy(items)
        }
    
    async def get_location_cycle_counts(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        location_id: Optional[UUID] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get Location Cycle Counts."""
        """Get cycle counts for location."""
        filters = [CycleCount.tenant_id == tenant_id]
        
        if location_id:
            filters.append(CycleCount.location_id == location_id)
        
        if status:
            filters.append(CycleCount.status == status)
        
        result = await db.execute(
            select(CycleCount)
            .where(and_(*filters))
            .order_by(CycleCount.created_at.desc())
        )
        counts = result.scalars().all()
        
        return [self._serialize_cycle_count(count) for count in counts]
    
    async def _generate_count_number(self, db: AsyncSession, tenant_id: UUID) -> str:
        """Generate Count Number."""
        """Generate unique count number."""
        today = date.today()
        prefix = f"CC-{today.strftime('%Y%m%d')}"
        
        result = await db.execute(
            select(func.count(CycleCount.id))
            .where(
                and_(
                    CycleCount.tenant_id == tenant_id,
                    CycleCount.count_number.like(f"{prefix}%")
                )
            )
        )
        count = result.scalar() or 0
        
        return f"{prefix}-{count + 1:04d}"
    
    def _serialize_count_item(self, item: CycleCountItem) -> Dict[str, Any]:
        """ Serialize Count Item."""
        """Serialize count item."""
        return {
            "item_id": str(item.item_id),
            "system_quantity": float(item.system_quantity),
            "counted_quantity": float(item.counted_quantity or 0),
            "variance_quantity": float(item.variance_quantity or 0),
            "variance_value": float(item.variance_value or 0),
            "is_counted": item.is_counted
        }
    
    def _serialize_cycle_count(self, count: CycleCount) -> Dict[str, Any]:
        """ Serialize Cycle Count."""
        """Serialize cycle count."""
        return {
            "id": str(count.id),
            "count_number": count.count_number,
            "status": count.status,
            "count_date": count.count_date.isoformat() if count.count_date else None,
            "location_id": str(count.location_id),
            "total_items_counted": count.total_items_counted,
            "items_with_variances": count.items_with_variances,
            "total_variance_value": float(count.total_variance_value or 0)
        }
    
    def _calculate_accuracy(self, items: List[CycleCountItem]) -> float:
        """ Calculate Accuracy."""
        """Calculate count accuracy percentage."""
        if not items:
            return 100.0
        
        accurate_items = len([item for item in items if item.variance_quantity == 0])
        return (accurate_items / len(items)) * 100