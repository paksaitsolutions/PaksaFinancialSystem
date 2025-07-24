"""
CRUD operations for payments.
"""
from typing import Any, Dict, List, Optional, Union
from uuid import UUID
from datetime import datetime

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.db.query_helper import QueryHelper
from app.models.accounts_payable.invoice import APInvoice, APInvoicePayment
from app.models.accounts_payable.payment import APPayment
from app.schemas.accounts_payable.payment import PaymentCreate, PaymentUpdate

class PaymentCRUD:
    """CRUD operations for payments."""
    
    def __init__(self):
        """Initialize with query helper."""
        self.query_helper = QueryHelper(APPayment)
    
    async def create(self, db: AsyncSession, *, obj_in: PaymentCreate) -> APPayment:
        """Create a new payment."""
        # Extract invoices data
        invoices_data = obj_in.invoices
        obj_in_data = obj_in.dict(exclude={"invoices"})
        
        # Generate payment number
        payment_number = await self._generate_payment_number(db)
        
        # Create payment
        db_obj = APPayment(
            **obj_in_data,
            payment_number=payment_number,
            status="pending"
        )
        db.add(db_obj)
        await db.flush()
        
        # Process invoices
        for invoice_data in invoices_data:
            # Get invoice
            invoice = await self._get_invoice(db, invoice_data.invoice_id)
            if not invoice:
                continue
            
            # Create payment-invoice association
            payment_invoice = APInvoicePayment(
                invoice_id=invoice_data.invoice_id,
                payment_id=db_obj.id,
                amount=invoice_data.amount
            )
            db.add(payment_invoice)
            
            # Update invoice paid amount and balance
            invoice.paid_amount += invoice_data.amount
            invoice.balance_due = invoice.total_amount - invoice.paid_amount
            
            # Update invoice status
            if invoice.balance_due <= 0:
                invoice.status = "paid"
            elif invoice.paid_amount > 0:
                invoice.status = "partially_paid"
            
            db.add(invoice)
        
        # Complete payment
        db_obj.status = "completed"
        db.add(db_obj)
        
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get(self, db: AsyncSession, id: UUID) -> Optional[APPayment]:
        """Get a payment by ID."""
        query = select(APPayment).where(APPayment.id == id).options(
            selectinload(APPayment.vendor),
            selectinload(APPayment.invoices)
        )
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_by_payment_number(self, db: AsyncSession, payment_number: str) -> Optional[APPayment]:
        """Get a payment by payment number."""
        query = select(APPayment).where(APPayment.payment_number == payment_number)
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
    ) -> List[APPayment]:
        """Get multiple payments."""
        query = self.query_helper.build_query(
            filters=filters,
            sort_by=sort_by or "payment_date",
            sort_order=sort_order,
            skip=skip,
            limit=limit,
            eager_load=["vendor", "invoices"]
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
        """Get paginated payments."""
        return await self.query_helper.get_paginated(
            db,
            filters=filters,
            sort_by=sort_by or "payment_date",
            sort_order=sort_order,
            page=page,
            page_size=page_size,
            eager_load=["vendor", "invoices"]
        )
    
    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: APPayment,
        obj_in: Union[PaymentUpdate, Dict[str, Any]]
    ) -> APPayment:
        """Update a payment."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        # Update payment attributes
        for field in update_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def void(
        self, 
        db: AsyncSession, 
        *, 
        db_obj: APPayment, 
        reason: str
    ) -> APPayment:
        """Void a payment."""
        # Can only void completed payments
        if db_obj.status != "completed":
            raise ValueError(f"Cannot void payment with status: {db_obj.status}")
        
        # Update payment status
        db_obj.status = "voided"
        db_obj.memo = f"{db_obj.memo or ''}\n\nVoid reason: {reason}".strip()
        db.add(db_obj)
        
        # Revert invoice payments
        for payment_invoice in db_obj.invoices:
            invoice = await self._get_invoice(db, payment_invoice.invoice_id)
            if not invoice:
                continue
            
            # Update invoice paid amount and balance
            invoice.paid_amount -= payment_invoice.amount
            invoice.balance_due = invoice.total_amount - invoice.paid_amount
            
            # Update invoice status
            if invoice.paid_amount <= 0:
                invoice.status = "approved"  # Revert to approved status
            elif invoice.paid_amount > 0:
                invoice.status = "partially_paid"
            
            db.add(invoice)
        
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def _generate_payment_number(self, db: AsyncSession) -> str:
        """Generate a unique payment number."""
        # Get current year and month
        now = datetime.now()
        year = now.year
        month = now.month
        
        # Get count of payments in current month
        query = select(func.count()).select_from(APPayment).where(
            and_(
                func.extract('year', APPayment.payment_date) == year,
                func.extract('month', APPayment.payment_date) == month
            )
        )
        result = await db.execute(query)
        count = result.scalar() or 0
        
        # Generate payment number: PAY-YYYYMM-XXXX
        return f"PAY-{year}{month:02d}-{count+1:04d}"
    
    async def _get_invoice(self, db: AsyncSession, invoice_id: UUID) -> Optional[APInvoice]:
        """Get an invoice by ID."""
        query = select(APInvoice).where(APInvoice.id == invoice_id)
        result = await db.execute(query)
        return result.scalars().first()

# Create an instance for dependency injection
payment_crud = PaymentCRUD()