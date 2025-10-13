"""
CRUD operations for invoicing.
"""
from typing import Any, Dict, List, Optional
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.db.query_helper import QueryHelper
from app.models.core_models import ARInvoice as Invoice, ARInvoiceLineItem as InvoiceItem, ARInvoicePayment as InvoicePayment

# Temporary placeholders - these should be properly implemented
class InvoiceTemplate:
    pass

class InvoiceApproval:
    pass
from app.schemas.invoicing.invoice_schemas import (
    InvoiceCreate, InvoiceUpdate, InvoiceTemplateCreate, 
    InvoicePaymentCreate, InvoiceApprovalCreate
)

class InvoiceCRUD:
    """CRUD operations for invoices."""
    
    def __init__(self):
        self.query_helper = QueryHelper(Invoice)
    
    async def create_invoice(
        self, 
        db: AsyncSession, 
        *, 
        tenant_id: UUID, 
        obj_in: InvoiceCreate
    ) -> Invoice:
        """Create a new invoice."""
        # Generate invoice number
        invoice_number = await self._generate_invoice_number(db, tenant_id)
        
        # Create invoice
        invoice_data = obj_in.dict(exclude={"items"})
        invoice = Invoice(
            tenant_id=tenant_id,
            invoice_number=invoice_number,
            **invoice_data
        )
        
        db.add(invoice)
        await db.flush()
        
        # Create invoice items
        for item_data in obj_in.items:
            item = InvoiceItem(
                invoice_id=invoice.id,
                **item_data.dict()
            )
            db.add(item)
        
        await db.commit()
        await db.refresh(invoice)
        return invoice
    
    async def get_invoice(self, db: AsyncSession, *, tenant_id: UUID, id: UUID) -> Optional[Invoice]:
        """Get invoice by ID."""
        query = select(Invoice).where(
            and_(Invoice.id == id, Invoice.tenant_id == tenant_id)
        ).options(
            selectinload(Invoice.items),
            selectinload(Invoice.payments),
            selectinload(Invoice.template)
        )
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_invoices(
        self,
        db: AsyncSession,
        *,
        tenant_id: UUID,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Invoice]:
        """Get invoices for tenant."""
        base_filters = {"tenant_id": tenant_id}
        if filters:
            base_filters.update(filters)
        
        query = self.query_helper.build_query(
            filters=base_filters,
            sort_by="created_at",
            sort_order="desc",
            skip=skip,
            limit=limit,
            eager_load=["items", "payments", "template"]
        )
        return await self.query_helper.execute_query(db, query)
    
    async def update_invoice(
        self,
        db: AsyncSession,
        *,
        db_obj: Invoice,
        obj_in: InvoiceUpdate
    ) -> Invoice:
        """Update invoice."""
        update_data = obj_in.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def send_invoice(self, db: AsyncSession, *, invoice: Invoice) -> Invoice:
        """Mark invoice as sent."""
        invoice.status = "sent"
        invoice.sent_at = datetime.utcnow()
        invoice.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(invoice)
        return invoice
    
    async def add_payment(
        self,
        db: AsyncSession,
        *,
        invoice: Invoice,
        payment_data: InvoicePaymentCreate
    ) -> InvoicePayment:
        """Add payment to invoice."""
        payment = InvoicePayment(
            invoice_id=invoice.id,
            **payment_data.dict()
        )
        
        db.add(payment)
        
        # Update invoice payment status
        total_payments = sum(p.amount for p in invoice.payments) + payment.amount
        
        if total_payments >= invoice.total_amount:
            invoice.payment_status = "paid"
            invoice.paid_at = datetime.utcnow()
        elif total_payments > 0:
            invoice.payment_status = "partial"
        
        invoice.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(payment)
        return payment
    
    async def create_recurring_invoice(self, db: AsyncSession, *, original_invoice: Invoice) -> Invoice:
        """Create recurring invoice from original."""
        if not original_invoice.is_recurring:
            raise ValueError("Invoice is not set for recurring")
        
        # Calculate next dates
        next_issue_date = original_invoice.next_invoice_date
        days_diff = (original_invoice.due_date - original_invoice.issue_date).days
        next_due_date = next_issue_date + timedelta(days=days_diff)
        
        # Create new invoice
        new_invoice = Invoice(
            tenant_id=original_invoice.tenant_id,
            invoice_number=await self._generate_invoice_number(db, original_invoice.tenant_id),
            customer_id=original_invoice.customer_id,
            template_id=original_invoice.template_id,
            issue_date=next_issue_date,
            due_date=next_due_date,
            subtotal=original_invoice.subtotal,
            tax_amount=original_invoice.tax_amount,
            total_amount=original_invoice.total_amount,
            notes=original_invoice.notes,
            terms=original_invoice.terms,
            is_recurring=True,
            recurring_frequency=original_invoice.recurring_frequency,
            next_invoice_date=self._calculate_next_date(next_issue_date, original_invoice.recurring_frequency)
        )
        
        db.add(new_invoice)
        await db.flush()
        
        # Copy items
        for item in original_invoice.items:
            new_item = InvoiceItem(
                invoice_id=new_invoice.id,
                description=item.description,
                quantity=item.quantity,
                unit_price=item.unit_price,
                total_price=item.total_price
            )
            db.add(new_item)
        
        # Update original invoice next date
        original_invoice.next_invoice_date = self._calculate_next_date(
            next_issue_date, original_invoice.recurring_frequency
        )
        
        await db.commit()
        await db.refresh(new_invoice)
        return new_invoice
    
    async def _generate_invoice_number(self, db: AsyncSession, tenant_id: UUID) -> str:
        """Generate unique invoice number."""
        # Get count of invoices for tenant
        query = select(func.count()).select_from(Invoice).where(Invoice.tenant_id == tenant_id)
        result = await db.execute(query)
        count = result.scalar() or 0
        
        return f"INV-{count + 1:06d}"
    
    def _calculate_next_date(self, current_date: date, frequency: str) -> date:
        """Calculate next invoice date based on frequency."""
        from dateutil.relativedelta import relativedelta
        
        if frequency == "monthly":
            return current_date + relativedelta(months=1)
        elif frequency == "quarterly":
            return current_date + relativedelta(months=3)
        elif frequency == "yearly":
            return current_date + relativedelta(years=1)
        else:
            return current_date + relativedelta(months=1)

class InvoiceTemplateCRUD:
    """CRUD operations for invoice templates."""
    
    async def create_template(
        self,
        db: AsyncSession,
        *,
        tenant_id: UUID,
        obj_in: InvoiceTemplateCreate
    ) -> InvoiceTemplate:
        """Create invoice template."""
        template = InvoiceTemplate(
            tenant_id=tenant_id,
            **obj_in.dict()
        )
        
        # If this is default, unset other defaults
        if template.is_default:
            await self._unset_default_templates(db, tenant_id)
        
        db.add(template)
        await db.commit()
        await db.refresh(template)
        return template
    
    async def get_templates(
        self,
        db: AsyncSession,
        *,
        tenant_id: UUID,
        active_only: bool = True
    ) -> List[InvoiceTemplate]:
        """Get templates for tenant."""
        query = select(InvoiceTemplate).where(InvoiceTemplate.tenant_id == tenant_id)
        
        if active_only:
            query = query.where(InvoiceTemplate.is_active == True)
        
        query = query.order_by(InvoiceTemplate.is_default.desc(), InvoiceTemplate.name)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def _unset_default_templates(self, db: AsyncSession, tenant_id: UUID):
        """Unset default flag from other templates."""
        query = select(InvoiceTemplate).where(
            and_(
                InvoiceTemplate.tenant_id == tenant_id,
                InvoiceTemplate.is_default == True
            )
        )
        result = await db.execute(query)
        templates = result.scalars().all()
        
        for template in templates:
            template.is_default = False

# Create instances
invoice_crud = InvoiceCRUD()
invoice_template_crud = InvoiceTemplateCRUD()