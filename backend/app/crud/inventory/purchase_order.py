"""
CRUD operations for purchase orders.
"""
from typing import Any, Dict, List, Optional, Union
from uuid import UUID
from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.db.query_helper import QueryHelper
from app.models.inventory.purchase_order import PurchaseOrder, PurchaseOrderLineItem, PurchaseOrderReceipt, PurchaseOrderReceiptLineItem
from app.models.inventory.item import InventoryItem
from app.models.inventory.transaction import InventoryTransaction
from app.schemas.inventory.purchase_order import PurchaseOrderCreate, PurchaseOrderUpdate, PurchaseOrderReceiptCreate

class PurchaseOrderCRUD:
    """CRUD operations for purchase orders."""
    
    def __init__(self):
        """Initialize with query helper."""
        self.query_helper = QueryHelper(PurchaseOrder)
    
    async def create(self, db: AsyncSession, *, obj_in: PurchaseOrderCreate) -> PurchaseOrder:
        """Create a new purchase order."""
        # Generate PO number
        po_number = await self._generate_po_number(db)
        
        # Calculate totals
        subtotal = sum(item.quantity_ordered * item.unit_cost for item in obj_in.line_items)
        
        # Create purchase order
        po_data = obj_in.dict(exclude={"line_items"})
        db_obj = PurchaseOrder(
            **po_data,
            po_number=po_number,
            subtotal=subtotal,
            total_amount=subtotal  # No tax calculation for now
        )
        db.add(db_obj)
        await db.flush()
        
        # Create line items
        for line_item_data in obj_in.line_items:
            line_total = line_item_data.quantity_ordered * line_item_data.unit_cost
            line_item = PurchaseOrderLineItem(
                **line_item_data.dict(),
                purchase_order_id=db_obj.id,
                line_total=line_total
            )
            db.add(line_item)
        
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get(self, db: AsyncSession, id: UUID) -> Optional[PurchaseOrder]:
        """Get a purchase order by ID."""
        query = select(PurchaseOrder).where(PurchaseOrder.id == id).options(
            selectinload(PurchaseOrder.vendor),
            selectinload(PurchaseOrder.line_items).selectinload(PurchaseOrderLineItem.item)
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
        """Get paginated purchase orders."""
        return await self.query_helper.get_paginated(
            db,
            filters=filters,
            sort_by=sort_by or "order_date",
            sort_order=sort_order,
            page=page,
            page_size=page_size,
            eager_load=["vendor", "line_items"]
        )
    
    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: PurchaseOrder,
        obj_in: Union[PurchaseOrderUpdate, Dict[str, Any]]
    ) -> PurchaseOrder:
        """Update a purchase order."""
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
    
    async def receive_items(
        self,
        db: AsyncSession,
        *,
        receipt_in: PurchaseOrderReceiptCreate
    ) -> PurchaseOrderReceipt:
        """Receive items from a purchase order."""
        # Get the purchase order
        po = await self.get(db, receipt_in.purchase_order_id)
        if not po:
            raise ValueError("Purchase order not found")
        
        # Generate receipt number
        receipt_number = await self._generate_receipt_number(db)
        
        # Create receipt
        receipt = PurchaseOrderReceipt(
            purchase_order_id=receipt_in.purchase_order_id,
            receipt_number=receipt_number,
            receipt_date=receipt_in.receipt_date,
            received_by=receipt_in.received_by,
            notes=receipt_in.notes
        )
        db.add(receipt)
        await db.flush()
        
        # Process line items
        for line_data in receipt_in.line_items:
            po_line_item_id = line_data["po_line_item_id"]
            quantity_received = line_data["quantity_received"]
            unit_cost = line_data.get("unit_cost", 0)
            
            # Get PO line item
            po_line_query = select(PurchaseOrderLineItem).where(PurchaseOrderLineItem.id == po_line_item_id)
            po_line_result = await db.execute(po_line_query)
            po_line = po_line_result.scalars().first()
            
            if not po_line:
                continue
            
            # Create receipt line item
            receipt_line = PurchaseOrderReceiptLineItem(
                receipt_id=receipt.id,
                po_line_item_id=po_line_item_id,
                quantity_received=quantity_received,
                unit_cost=unit_cost or po_line.unit_cost
            )
            db.add(receipt_line)
            
            # Update PO line item received quantity
            po_line.quantity_received += quantity_received
            db.add(po_line)
            
            # Create inventory transaction
            inventory_transaction = InventoryTransaction(
                item_id=po_line.item_id,
                location_id=po_line.item.default_location_id,  # Use item's default location
                transaction_type="receipt",
                transaction_date=receipt_in.receipt_date,
                reference=f"PO {po.po_number} - Receipt {receipt_number}",
                quantity=quantity_received,
                unit_cost=unit_cost or po_line.unit_cost,
                total_cost=quantity_received * (unit_cost or po_line.unit_cost),
                notes=f"Received from PO {po.po_number}"
            )
            db.add(inventory_transaction)
            
            # Update inventory item quantities
            item_query = select(InventoryItem).where(InventoryItem.id == po_line.item_id)
            item_result = await db.execute(item_query)
            item = item_result.scalars().first()
            
            if item:
                item.quantity_on_hand += quantity_received
                item.quantity_available = item.quantity_on_hand - item.quantity_committed
                db.add(item)
        
        # Update PO status
        total_ordered = sum(line.quantity_ordered for line in po.line_items)
        total_received = sum(line.quantity_received for line in po.line_items)
        
        if total_received >= total_ordered:
            po.status = "received"
        elif total_received > 0:
            po.status = "partially_received"
        
        db.add(po)
        await db.commit()
        await db.refresh(receipt)
        return receipt
    
    async def _generate_po_number(self, db: AsyncSession) -> str:
        """Generate a unique PO number."""
        now = datetime.now()
        year = now.year
        month = now.month
        
        query = select(func.count()).select_from(PurchaseOrder).where(
            func.extract('year', PurchaseOrder.order_date) == year,
            func.extract('month', PurchaseOrder.order_date) == month
        )
        result = await db.execute(query)
        count = result.scalar() or 0
        
        return f"PO-{year}{month:02d}-{count+1:04d}"
    
    async def _generate_receipt_number(self, db: AsyncSession) -> str:
        """Generate a unique receipt number."""
        now = datetime.now()
        year = now.year
        month = now.month
        
        query = select(func.count()).select_from(PurchaseOrderReceipt).where(
            func.extract('year', PurchaseOrderReceipt.receipt_date) == year,
            func.extract('month', PurchaseOrderReceipt.receipt_date) == month
        )
        result = await db.execute(query)
        count = result.scalar() or 0
        
        return f"REC-{year}{month:02d}-{count+1:04d}"

# Create an instance for dependency injection
purchase_order_crud = PurchaseOrderCRUD()