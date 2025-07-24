"""
CRUD operations for inventory reports and analytics.
"""
from typing import List, Dict, Any, Optional
from datetime import date, datetime, timedelta

from sqlalchemy import select, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.inventory.item import InventoryItem, InventoryCategory
from app.models.inventory.transaction import InventoryTransaction
from app.schemas.inventory.reports import InventoryValueReport, StockLevelReport, TransactionSummary, InventoryAnalytics

class InventoryReportsCRUD:
    """CRUD operations for inventory reports."""
    
    async def get_inventory_valuation(
        self, 
        db: AsyncSession,
        *,
        category_id: Optional[str] = None,
        location_id: Optional[str] = None
    ) -> List[InventoryValueReport]:
        """Get inventory valuation report."""
        query = select(
            InventoryItem.id,
            InventoryItem.sku,
            InventoryItem.name,
            InventoryCategory.name.label("category_name"),
            InventoryItem.quantity_on_hand,
            InventoryItem.unit_cost,
            (InventoryItem.quantity_on_hand * InventoryItem.unit_cost).label("total_value")
        ).outerjoin(InventoryCategory)
        
        if category_id:
            query = query.where(InventoryItem.category_id == category_id)
        
        query = query.order_by(desc("total_value"))
        
        result = await db.execute(query)
        rows = result.fetchall()
        
        return [
            InventoryValueReport(
                item_id=str(row.id),
                sku=row.sku,
                name=row.name,
                category=row.category_name,
                quantity_on_hand=row.quantity_on_hand,
                unit_cost=row.unit_cost,
                total_value=row.total_value or 0
            )
            for row in rows
        ]
    
    async def get_stock_levels(
        self, 
        db: AsyncSession,
        *,
        low_stock_only: bool = False
    ) -> List[StockLevelReport]:
        """Get stock level report."""
        query = select(InventoryItem)
        
        if low_stock_only:
            query = query.where(InventoryItem.quantity_on_hand <= InventoryItem.reorder_point)
        
        query = query.order_by(InventoryItem.name)
        
        result = await db.execute(query)
        items = result.scalars().all()
        
        return [
            StockLevelReport(
                item_id=str(item.id),
                sku=item.sku,
                name=item.name,
                quantity_on_hand=item.quantity_on_hand,
                quantity_available=item.quantity_available,
                quantity_committed=item.quantity_committed,
                reorder_point=item.reorder_point,
                reorder_quantity=item.reorder_quantity,
                status="Low Stock" if item.quantity_on_hand <= item.reorder_point else "In Stock"
            )
            for item in items
        ]
    
    async def get_transaction_summary(
        self, 
        db: AsyncSession,
        *,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> List[TransactionSummary]:
        """Get transaction summary by type."""
        query = select(
            InventoryTransaction.transaction_type,
            func.sum(InventoryTransaction.quantity).label("total_quantity"),
            func.sum(InventoryTransaction.total_cost).label("total_value"),
            func.count().label("transaction_count")
        )
        
        if from_date:
            query = query.where(InventoryTransaction.transaction_date >= from_date)
        if to_date:
            query = query.where(InventoryTransaction.transaction_date <= to_date)
        
        query = query.group_by(InventoryTransaction.transaction_type)
        
        result = await db.execute(query)
        rows = result.fetchall()
        
        return [
            TransactionSummary(
                transaction_type=row.transaction_type,
                total_quantity=row.total_quantity or 0,
                total_value=row.total_value or 0,
                transaction_count=row.transaction_count
            )
            for row in rows
        ]
    
    async def get_analytics_dashboard(self, db: AsyncSession) -> InventoryAnalytics:
        """Get inventory analytics for dashboard."""
        # Total items
        total_items_query = select(func.count()).select_from(InventoryItem)
        total_items_result = await db.execute(total_items_query)
        total_items = total_items_result.scalar() or 0
        
        # Total inventory value
        total_value_query = select(
            func.sum(InventoryItem.quantity_on_hand * InventoryItem.unit_cost)
        ).select_from(InventoryItem)
        total_value_result = await db.execute(total_value_query)
        total_value = total_value_result.scalar() or 0
        
        # Low stock items
        low_stock_query = select(func.count()).select_from(InventoryItem).where(
            InventoryItem.quantity_on_hand <= InventoryItem.reorder_point
        )
        low_stock_result = await db.execute(low_stock_query)
        low_stock_items = low_stock_result.scalar() or 0
        
        # Out of stock items
        out_of_stock_query = select(func.count()).select_from(InventoryItem).where(
            InventoryItem.quantity_on_hand <= 0
        )
        out_of_stock_result = await db.execute(out_of_stock_query)
        out_of_stock_items = out_of_stock_result.scalar() or 0
        
        # Transaction summary (last 30 days)
        thirty_days_ago = datetime.now().date() - timedelta(days=30)
        transaction_summary = await self.get_transaction_summary(
            db, from_date=thirty_days_ago
        )
        
        # Top items by value (top 10)
        top_items = await self.get_inventory_valuation(db)
        top_items_by_value = top_items[:10]
        
        # Recent transactions (last 10)
        recent_transactions_query = select(
            InventoryTransaction.transaction_type,
            InventoryTransaction.transaction_date,
            InventoryTransaction.quantity,
            InventoryTransaction.total_cost,
            InventoryItem.name.label("item_name"),
            InventoryItem.sku
        ).join(InventoryItem).order_by(
            desc(InventoryTransaction.created_at)
        ).limit(10)
        
        recent_result = await db.execute(recent_transactions_query)
        recent_rows = recent_result.fetchall()
        
        recent_transactions = [
            {
                "transaction_type": row.transaction_type,
                "transaction_date": row.transaction_date.isoformat(),
                "quantity": float(row.quantity),
                "total_cost": float(row.total_cost or 0),
                "item_name": row.item_name,
                "sku": row.sku
            }
            for row in recent_rows
        ]
        
        return InventoryAnalytics(
            total_items=total_items,
            total_value=total_value,
            low_stock_items=low_stock_items,
            out_of_stock_items=out_of_stock_items,
            transaction_summary=transaction_summary,
            top_items_by_value=top_items_by_value,
            recent_transactions=recent_transactions
        )

# Create an instance for dependency injection
inventory_reports_crud = InventoryReportsCRUD()