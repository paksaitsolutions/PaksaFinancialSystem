"""
Accounts Receivable schemas.
"""
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from .models import InvoiceStatus, PaymentStatus


class InvoiceItemBase(BaseModel):
    description: str
    quantity: Decimal = Field(default=1, gt=0)
    unit_price: Decimal = Field(ge=0)
    discount_percent: Decimal = Field(default=0, ge=0, le=100)
    tax_rate: Decimal = Field(default=0, ge=0, le=100)


class InvoiceItemCreate(InvoiceItemBase):
    pass


class InvoiceItemResponse(InvoiceItemBase):
    id: UUID
    invoice_id: UUID
    subtotal: Decimal
    discount_amount: Decimal
    taxable_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal

    class Config:
        from_attributes = True


class InvoiceBase(BaseModel):
    customer_id: UUID
    issue_date: date = Field(default_factory=date.today)
    due_date: date
    po_number: Optional[str] = None
    terms: Optional[str] = None
    notes: Optional[str] = None


class InvoiceCreate(InvoiceBase):
    items: List[InvoiceItemCreate] = Field(min_items=1)


class InvoiceUpdate(BaseModel):
    due_date: Optional[date] = None
    po_number: Optional[str] = None
    terms: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[InvoiceStatus] = None


class InvoiceResponse(InvoiceBase):
    id: UUID
    invoice_number: str
    status: InvoiceStatus
    subtotal: Decimal
    tax_amount: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    amount_paid: Decimal
    balance_due: Decimal
    date_sent: Optional[datetime] = None
    date_viewed: Optional[datetime] = None
    date_paid: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    items: List[InvoiceItemResponse] = []

    class Config:
        from_attributes = True


class PaymentBase(BaseModel):
    customer_id: UUID
    payment_date: date = Field(default_factory=date.today)
    amount: Decimal = Field(gt=0)
    payment_method: str
    transaction_id: Optional[str] = None
    reference_number: Optional[str] = None
    notes: Optional[str] = None


class PaymentCreate(PaymentBase):
    invoice_id: Optional[UUID] = None


class PaymentResponse(PaymentBase):
    id: UUID
    payment_number: str
    status: PaymentStatus
    invoice_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CreditNoteBase(BaseModel):
    customer_id: UUID
    issue_date: date = Field(default_factory=date.today)
    total_amount: Decimal = Field(gt=0)
    reference_invoice_id: Optional[UUID] = None
    reason: Optional[str] = None


class CreditNoteCreate(CreditNoteBase):
    pass


class CreditNoteResponse(CreditNoteBase):
    id: UUID
    credit_note_number: str
    status: str
    remaining_amount: Decimal
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True