"""
CRUD operations for procurement.
"""
from typing import Any, Dict, List, Optional
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal

from sqlalchemy import select, and_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.db.query_helper import QueryHelper
from app.models.procurement.vendor import Vendor
from app.models.procurement.purchase_order import PurchaseOrder, PurchaseOrderItem, VendorPayment
from app.schemas.procurement.procurement_schemas import (
    VendorCreate, VendorUpdate, PurchaseOrderCreate, PurchaseOrderUpdate,
    VendorPaymentCreate, PurchaseAnalytics
)

class ProcurementCRUD:
    """CRUD operations for procurement."""
    
    def __init__(self):
        self.vendor_helper = QueryHelper(Vendor)
        self.po_helper = QueryHelper(PurchaseOrder)
    
    # Vendor Management
    async def create_vendor(
        self, 
        db: AsyncSession, 
        *, 
        tenant_id: UUID, 
        obj_in: VendorCreate
    ) -> Vendor:
        """Create vendor."""
        vendor = Vendor(
            tenant_id=tenant_id,
            **obj_in.dict()
        )
        
        db.add(vendor)
        await db.commit()
        await db.refresh(vendor)
        return vendor
    
    async def get_vendor(self, db: AsyncSession, *, tenant_id: UUID, id: UUID) -> Optional[Vendor]:
        """Get vendor by ID."""
        query = select(Vendor).where(
            and_(Vendor.id == id, Vendor.tenant_id == tenant_id)
        )
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_vendors(
        self,
        db: AsyncSession,
        *,
        tenant_id: UUID,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Vendor]:
        """Get vendors for tenant."""
        base_filters = {"tenant_id": tenant_id}
        if filters:
            base_filters.update(filters)
        
        query = self.vendor_helper.build_query(
            filters=base_filters,
            sort_by="vendor_name",
            sort_order="asc",
            skip=skip,
            limit=limit
        )
        return await self.vendor_helper.execute_query(db, query)
    
    async def update_vendor(
        self,
        db: AsyncSession,
        *,
        db_obj: Vendor,
        obj_in: VendorUpdate
    ) -> Vendor:
        """Update vendor."""
        update_data = obj_in.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    # Purchase Order Management
    async def create_purchase_order(
        self,
        db: AsyncSession,
        *,
        tenant_id: UUID,
        created_by: UUID,
        obj_in: PurchaseOrderCreate
    ) -> PurchaseOrder:
        """Create purchase order."""
        # Generate PO number
        po_number = await self._generate_po_number(db, tenant_id)
        
        # Create purchase order
        po_data = obj_in.dict(exclude={"items"})
        purchase_order = PurchaseOrder(
            tenant_id=tenant_id,
            po_number=po_number,
            created_by=created_by,
            **po_data
        )
        
        db.add(purchase_order)
        await db.flush()
        
        # Create items
        for item_data in obj_in.items:
            item = PurchaseOrderItem(
                purchase_order_id=purchase_order.id,
                **item_data.dict()
            )
            db.add(item)
        
        await db.commit()
        await db.refresh(purchase_order)
        return purchase_order
    
    async def get_purchase_orders(
        self,
        db: AsyncSession,
        *,
        tenant_id: UUID,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[PurchaseOrder]:
        """Get purchase orders for tenant."""
        base_filters = {"tenant_id": tenant_id}
        if filters:
            base_filters.update(filters)
        
        query = self.po_helper.build_query(
            filters=base_filters,
            sort_by="order_date",
            sort_order="desc",
            skip=skip,
            limit=limit,
            eager_load=["vendor", "items"]
        )
        return await self.po_helper.execute_query(db, query)
    
    async def approve_purchase_order(
        self,
        db: AsyncSession,
        *,
        purchase_order: PurchaseOrder,
        approved_by: UUID
    ) -> PurchaseOrder:
        """Approve purchase order."""
        if purchase_order.approval_status != "pending":
            raise ValueError("Only pending orders can be approved")
        
        purchase_order.approval_status = "approved"
        purchase_order.status = "approved"
        purchase_order.approved_by = approved_by
        purchase_order.approved_at = datetime.utcnow()
        purchase_order.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(purchase_order)
        return purchase_order
    
    async def reject_purchase_order(
        self,
        db: AsyncSession,
        *,
        purchase_order: PurchaseOrder,
        rejected_by: UUID
    ) -> PurchaseOrder:
        """Reject purchase order."""
        if purchase_order.approval_status != "pending":
            raise ValueError("Only pending orders can be rejected")
        
        purchase_order.approval_status = "rejected"
        purchase_order.status = "cancelled"
        purchase_order.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(purchase_order)
        return purchase_order
    
    # Vendor Payment Processing
    async def create_vendor_payment(
        self,
        db: AsyncSession,
        *,
        tenant_id: UUID,
        created_by: UUID,
        obj_in: VendorPaymentCreate
    ) -> VendorPayment:
        """Create vendor payment."""
        # Generate payment number
        payment_number = await self._generate_payment_number(db, tenant_id)
        
        payment = VendorPayment(
            tenant_id=tenant_id,
            payment_number=payment_number,
            created_by=created_by,
            **obj_in.dict()
        )
        
        db.add(payment)
        await db.commit()
        await db.refresh(payment)
        return payment
    
    # Purchase Analytics
    async def get_purchase_analytics(
        self,
        db: AsyncSession,
        *,
        tenant_id: UUID
    ) -> PurchaseAnalytics:
        """Get purchase analytics."""
        # Total orders
        total_orders_query = select(func.count()).select_from(PurchaseOrder).where(
            PurchaseOrder.tenant_id == tenant_id
        )
        total_orders_result = await db.execute(total_orders_query)
        total_orders = total_orders_result.scalar() or 0
        
        # Total amount
        total_amount_query = select(func.sum(PurchaseOrder.total_amount)).where(
            PurchaseOrder.tenant_id == tenant_id
        )
        total_amount_result = await db.execute(total_amount_query)
        total_amount = total_amount_result.scalar() or Decimal("0")
        
        # Pending approvals
        pending_query = select(func.count()).select_from(PurchaseOrder).where(
            and_(
                PurchaseOrder.tenant_id == tenant_id,
                PurchaseOrder.approval_status == "pending"
            )
        )
        pending_result = await db.execute(pending_query)
        pending_approvals = pending_result.scalar() or 0
        
        # Top vendors
        top_vendors_query = select(
            Vendor.vendor_name,
            func.sum(PurchaseOrder.total_amount).label("total_spent")
        ).select_from(
            PurchaseOrder
        ).join(Vendor).where(
            PurchaseOrder.tenant_id == tenant_id
        ).group_by(
            Vendor.vendor_name
        ).order_by(
            desc("total_spent")
        ).limit(5)
        
        top_vendors_result = await db.execute(top_vendors_query)
        top_vendors = [
            {"vendor_name": row.vendor_name, "total_spent": float(row.total_spent)}
            for row in top_vendors_result
        ]
        
        # Monthly spending (mock data)
        monthly_spending = [
            {"month": "Jan", "amount": 15000},
            {"month": "Feb", "amount": 18000},
            {"month": "Mar", "amount": 22000},
        ]
        
        return PurchaseAnalytics(
            total_orders=total_orders,
            total_amount=total_amount,
            pending_approvals=pending_approvals,
            top_vendors=top_vendors,
            monthly_spending=monthly_spending
        )
    
    # Inventory Integration
    async def update_inventory_from_receipt(
        self,
        db: AsyncSession,
        *,
        tenant_id: UUID,
        receipt_items: List[dict]
    ):
        """Update inventory quantities from purchase receipt."""
        # This would integrate with inventory module
        # For now, just a placeholder
        pass
    
    async def _generate_po_number(self, db: AsyncSession, tenant_id: UUID) -> str:
        """Generate purchase order number."""
        query = select(func.count()).select_from(PurchaseOrder).where(
            PurchaseOrder.tenant_id == tenant_id
        )
        result = await db.execute(query)
        count = result.scalar() or 0
        
        return f"PO-{count + 1:06d}"
    
    async def _generate_payment_number(self, db: AsyncSession, tenant_id: UUID) -> str:
        """Generate payment number."""
        query = select(func.count()).select_from(VendorPayment).where(
            VendorPayment.tenant_id == tenant_id
        )
        result = await db.execute(query)
        count = result.scalar() or 0
        
        return f"PAY-{count + 1:06d}"

# Create instance
procurement_crud = ProcurementCRUD()