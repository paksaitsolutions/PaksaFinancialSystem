"""
Service layer for the Accounts Receivable module.
"""
from datetime import date
from decimal import Decimal
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from . import models, schemas
from .exceptions import (
    BusinessRuleError,
    NotFoundError,
    ValidationError,
)


class InvoiceService:
    """Service for managing invoices."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_invoice(
        self, invoice_in: schemas.InvoiceCreate, created_by_id: UUID
    ) -> models.Invoice:
        """
        Creates a new invoice.
        - Validates input data.
        - Calculates totals from line items.
        - Creates Invoice and InvoiceItem records.
        """
        if not invoice_in.invoice_items:
            raise ValidationError("Invoice must have at least one line item.")
        if invoice_in.due_date < invoice_in.issue_date:
            raise ValidationError("Due date cannot be before the issue date.")

        subtotal = sum(item.quantity * item.unit_price for item in invoice_in.invoice_items)
        
        total_tax = 0
        total_discount = 0
        
        invoice_items_to_create = []
        for item_in in invoice_in.invoice_items:
            item_subtotal = item_in.quantity * item_in.unit_price
            item_discount = (item_subtotal * item_in.discount_percent) / 100
            item_taxable_amount = item_subtotal - item_discount
            item_tax = (item_taxable_amount * item_in.tax_rate) / 100
            
            total_discount += item_discount
            total_tax += item_tax

            invoice_items_to_create.append(
                models.InvoiceItem(
                    description=item_in.description,
                    quantity=item_in.quantity,
                    unit_price=item_in.unit_price,
                    discount_percent=item_in.discount_percent,
                    tax_rate=item_in.tax_rate,
                    item_id=item_in.item_id,
                    gl_account_id=item_in.gl_account_id,
                )
            )

        total_amount = subtotal + total_tax - total_discount

        new_invoice = models.Invoice(
            customer_id=invoice_in.customer_id,
            issue_date=invoice_in.issue_date,
            due_date=invoice_in.due_date,
            po_number=invoice_in.po_number,
            terms=invoice_in.terms,
            notes=invoice_in.notes,
            subtotal=subtotal,
            tax_amount=total_tax,
            discount_amount=total_discount,
            total_amount=total_amount,
            balance_due=total_amount, 
            created_by_id=created_by_id,
            updated_by_id=created_by_id,
            invoice_items=invoice_items_to_create,
            invoice_number=f"INV-{date.today().year}-{await self._get_next_invoice_number()}"
        )

        self.db.add(new_invoice)
        await self.db.commit()
        await self.db.refresh(new_invoice, ["invoice_items"])

        return new_invoice

    async def _get_next_invoice_number(self) -> int:
        """Generates the next invoice number for the current year."""
        current_year = date.today().year
        result = await self.db.execute(
            select(func.count(models.Invoice.id)).where(
                func.extract('year', models.Invoice.issue_date) == current_year
            )
        )
        count = result.scalar_one_or_none() or 0
        return count + 1

    async def get_invoice(self, invoice_id: UUID) -> Optional[models.Invoice]:
        """Retrieves an invoice by its ID."""
        result = await self.db.execute(
            select(models.Invoice)
            .where(models.Invoice.id == invoice_id)
            .options(selectinload(models.Invoice.invoice_items))
        )
        return result.scalars().first()

    async def list_invoices(self, **kwargs):
        pass

    async def update_invoice(self, **kwargs):
        pass

    async def send_invoice(self, **kwargs):
        pass

    async def void_invoice(self, **kwargs):
        pass


class PaymentService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def record_payment(self, **kwargs):
        pass

    async def list_payments(self, **kwargs):
        pass

    async def get_payment(self, **kwargs):
        pass


class CreditNoteService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_credit_note(self, **kwargs):
        pass


class ReportingService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_accounts_aging_report(self, **kwargs):
        pass
