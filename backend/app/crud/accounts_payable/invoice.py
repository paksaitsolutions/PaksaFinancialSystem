"""
CRUD operations for invoices.
"""
from typing import Any, Dict, List, Optional, Union
from uuid import UUID
from datetime import datetime, date

from sqlalchemy import select, and_, or_, between
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.db.query_helper import QueryHelper
from app.models import APInvoice, APInvoiceLineItem
from app.schemas.accounts_payable.invoice import InvoiceCreate, InvoiceUpdate

class InvoiceCRUD:
    """CRUD operations for invoices."""
    
    def __init__(self):
        """Initialize with query helper."""
        self.query_helper = QueryHelper(APInvoice)
    
    async def create(self, db: AsyncSession, *, obj_in: InvoiceCreate) -> APInvoice:
        """Create a new invoice."""
        # Extract line items data
        line_items_data = obj_in.line_items
        obj_in_data = obj_in.dict(exclude={"line_items"})
        
        # Calculate totals
        subtotal = sum(item.amount for item in line_items_data)
        tax_amount = 0  # Tax calculation would be implemented separately
        discount_amount = 0  # Discount calculation would be implemented separately
        total_amount = subtotal + tax_amount - discount_amount
        
        # Create invoice
        db_obj = APInvoice(
            **obj_in_data,
            status="draft",
            subtotal=subtotal,
            tax_amount=tax_amount,
            discount_amount=discount_amount,
            total_amount=total_amount,
            paid_amount=0,
            balance_due=total_amount
        )
        db.add(db_obj)
        await db.flush()
        
        # Create line items
        for item_data in line_items_data:
            line_item = APInvoiceLineItem(**item_data.dict(), invoice_id=db_obj.id)
            db.add(line_item)
        
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get(self, db: AsyncSession, id: UUID) -> Optional[APInvoice]:
        """Get an invoice by ID."""
        query = select(APInvoice).where(APInvoice.id == id).options(
            selectinload(APInvoice.line_items),
            selectinload(APInvoice.vendor),
            selectinload(APInvoice.currency),
            selectinload(APInvoice.approved_by),
        )
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_by_invoice_number(self, db: AsyncSession, vendor_id: UUID, invoice_number: str) -> Optional[APInvoice]:
        """Get an invoice by vendor ID and invoice number."""
        query = select(APInvoice).where(
            and_(
                APInvoice.vendor_id == vendor_id,
                APInvoice.invoice_number == invoice_number
            )
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
        sort_order: str = "asc"
    ) -> List[APInvoice]:
        """Get multiple invoices."""
        # Process special filters
        processed_filters = {}
        if filters:
            for key, value in filters.items():
                if key == "invoice_date_from" and value:
                    # Skip this, handled separately
                    continue
                elif key == "invoice_date_to" and value:
                    # Skip this, handled separately
                    continue
                else:
                    processed_filters[key] = value
        
        query = self.query_helper.build_query(
            filters=processed_filters,
            sort_by=sort_by or "invoice_date",
            sort_order=sort_order,
            skip=skip,
            limit=limit,
            eager_load=["line_items", "vendor", "currency"]
        )
        
        # Add date range filters if provided
        if filters:
            if "invoice_date_from" in filters and filters["invoice_date_from"]:
                from_date = filters["invoice_date_from"]
                if isinstance(from_date, str):
                    from_date = date.fromisoformat(from_date)
                query = query.where(APInvoice.invoice_date >= from_date)
            
            if "invoice_date_to" in filters and filters["invoice_date_to"]:
                to_date = filters["invoice_date_to"]
                if isinstance(to_date, str):
                    to_date = date.fromisoformat(to_date)
                query = query.where(APInvoice.invoice_date <= to_date)
        
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
        """Get paginated invoices."""
        return await self.query_helper.get_paginated(
            db,
            filters=filters,
            sort_by=sort_by or "invoice_date",
            sort_order=sort_order,
            page=page,
            page_size=page_size,
            eager_load=["line_items", "vendor", "currency"]
        )
    
    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: APInvoice,
        obj_in: Union[InvoiceUpdate, Dict[str, Any]]
    ) -> APInvoice:
        """Update an invoice."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        # Extract line items if present
        line_items_data = update_data.pop("line_items", None)
        
        # Update invoice attributes
        for field in update_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])
        
        # Update line items if provided
        if line_items_data is not None:
            # Delete existing line items
            await db.execute(
                select(APInvoiceLineItem).where(APInvoiceLineItem.invoice_id == db_obj.id)
            )
            for line_item in db_obj.line_items:
                await db.delete(line_item)
            
            # Create new line items
            for item_data in line_items_data:
                if isinstance(item_data, dict):
                    line_item = APInvoiceLineItem(**item_data, invoice_id=db_obj.id)
                else:
                    line_item = APInvoiceLineItem(**item_data.dict(), invoice_id=db_obj.id)
                db.add(line_item)
            
            # Recalculate totals
            subtotal = sum(item.amount for item in line_items_data)
            tax_amount = 0  # Tax calculation would be implemented separately
            discount_amount = 0  # Discount calculation would be implemented separately
            total_amount = subtotal + tax_amount - discount_amount
            
            db_obj.subtotal = subtotal
            db_obj.tax_amount = tax_amount
            db_obj.discount_amount = discount_amount
            db_obj.total_amount = total_amount
            db_obj.balance_due = total_amount - db_obj.paid_amount
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def delete(self, db: AsyncSession, *, id: UUID) -> Optional[APInvoice]:
        """Delete an invoice."""
        invoice = await self.get(db, id)
        if invoice:
            # Delete line items first
            for line_item in invoice.line_items:
                await db.delete(line_item)
            
            # Delete invoice
            await db.delete(invoice)
            await db.commit()
        return invoice
    
    async def submit(self, db: AsyncSession, *, db_obj: APInvoice) -> APInvoice:
        """Submit an invoice for approval."""
        db_obj.status = "pending"
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def approve(
        self, 
        db: AsyncSession, 
        *, 
        db_obj: APInvoice, 
        approved_by_id: UUID,
        notes: Optional[str] = None
    ) -> APInvoice:
        """Approve an invoice."""
        db_obj.status = "approved"
        db_obj.approved_by_id = approved_by_id
        db_obj.approved_at = datetime.utcnow()
        
        # Add notes if provided
        if notes:
            db_obj.description = f"{db_obj.description or ''}\n\nApproval notes: {notes}".strip()
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def reject(
        self, 
        db: AsyncSession, 
        *, 
        db_obj: APInvoice, 
        rejected_by_id: UUID,
        notes: Optional[str] = None
    ) -> APInvoice:
        """Reject an invoice."""
        db_obj.status = "rejected"
        
        # Add rejection notes
        rejection_note = f"Rejected by user ID: {rejected_by_id}"
        if notes:
            rejection_note += f"\nReason: {notes}"
        
        db_obj.description = f"{db_obj.description or ''}\n\n{rejection_note}".strip()
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def void(
        self, 
        db: AsyncSession, 
        *, 
        db_obj: APInvoice, 
        reason: str
    ) -> APInvoice:
        """Void an invoice."""
        db_obj.status = "voided"
        
        # Add void reason
        db_obj.description = f"{db_obj.description or ''}\n\nVoid reason: {reason}".strip()
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

# Create an instance for dependency injection
invoice_crud = InvoiceCRUD()