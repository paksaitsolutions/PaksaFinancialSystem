"""
Pydantic schemas for the Accounts Receivable module.
"""
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field, validator, condecimal

from .models import InvoiceStatus, PaymentStatus


# Base schemas
class BaseSchema(BaseModel):
    """Base schema with common fields."""
    class Config:
        orm_mode = True
        json_encoders = {
            Decimal: str,
        }


# Invoice schemas
class InvoiceItemBase(BaseSchema):
    """Base schema for invoice items."""
    description: str
    quantity: Decimal = Field(..., gt=0, decimal_places=4)
    unit_price: Decimal = Field(..., gt=0, decimal_places=4)
    discount_percent: Decimal = Field(0, ge=0, le=100, decimal_places=2)
    tax_rate: Decimal = Field(..., ge=0, decimal_places=2)
    item_id: Optional[UUID] = None
    gl_account_id: UUID


class InvoiceItemCreate(InvoiceItemBase):
    """Schema for creating an invoice item."""
    pass


class InvoiceItemUpdate(InvoiceItemBase):
    """Schema for updating an invoice item."""
    pass


class InvoiceItemResponse(InvoiceItemBase):
    """Schema for returning an invoice item."""
    id: UUID
    invoice_id: UUID
    subtotal: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal


class InvoiceBase(BaseSchema):
    """Base schema for invoices."""
    customer_id: UUID
    issue_date: date
    due_date: date
    po_number: Optional[str] = None
    terms: Optional[str] = None
    notes: Optional[str] = None
    dunning_schedule: Optional[dict] = None
    dispute_status: Optional[str] = None
    invoice_items: List[InvoiceItemCreate]


class InvoiceCreate(InvoiceBase):
    """Schema for creating an invoice."""
    pass


class InvoiceUpdate(BaseSchema):
    """Schema for updating an invoice."""
    status: Optional[InvoiceStatus] = None
    po_number: Optional[str] = None
    terms: Optional[str] = None
    notes: Optional[str] = None


class InvoiceResponse(InvoiceBase):
    """Schema for returning an invoice."""
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
    invoice_items: List[InvoiceItemResponse] = []


# Payment schemas
class PaymentBase(BaseSchema):
    """Base schema for payments."""
    customer_id: UUID
    payment_date: date
    amount: Decimal = Field(..., gt=0, decimal_places=4)
    payment_method: str
    reference_number: Optional[str] = None
    transaction_id: Optional[str] = None
    notes: Optional[str] = None


class PaymentCreate(PaymentBase):
    """Schema for creating a payment."""
    invoice_ids: List[UUID] = []
    credit_note_ids: List[UUID] = []


class PaymentUpdate(BaseSchema):
    """Schema for updating a payment."""
    status: Optional[PaymentStatus] = None
    reference_number: Optional[str] = None
    transaction_id: Optional[str] = None
    notes: Optional[str] = None


class PaymentResponse(PaymentBase):
    """Schema for returning a payment."""
    id: UUID
    payment_number: str
    status: PaymentStatus
    created_at: datetime
    updated_at: datetime


# Credit Note schemas
class CreditNoteItemBase(BaseSchema):
    """Base schema for credit note items."""
    description: str
    quantity: Decimal = Field(..., gt=0, decimal_places=4)
    unit_price: Decimal = Field(..., gt=0, decimal_places=4)
    tax_rate: Decimal = Field(..., ge=0, decimal_places=2)
    item_id: Optional[UUID] = None
    gl_account_id: UUID


class CreditNoteItemCreate(CreditNoteItemBase):
    """Schema for creating a credit note item."""
    pass


class CreditNoteItemResponse(CreditNoteItemBase):
    """Schema for returning a credit note item."""
    id: UUID
    credit_note_id: UUID
    total_amount: Decimal


class CreditNoteBase(BaseSchema):
    """Base schema for credit notes."""
    customer_id: UUID
    issue_date: date
    reference_invoice_id: Optional[UUID] = None
    reason: Optional[str] = None
    credit_note_items: List[CreditNoteItemCreate]


class CreditNoteCreate(CreditNoteBase):
    """Schema for creating a credit note."""
    pass


class CreditNoteUpdate(BaseSchema):
    """Schema for updating a credit note."""
    status: Optional[str] = None
    reason: Optional[str] = None


class CreditNoteResponse(CreditNoteBase):
    """Schema for returning a credit note."""
    id: UUID
    credit_note_number: str
    status: str
    total_amount: Decimal
    remaining_amount: Decimal
    created_at: datetime
    updated_at: datetime
    credit_note_items: List[CreditNoteItemResponse] = []


# Reporting schemas
class AccountsAgingSummary(BaseSchema):
    """Schema for accounts aging summary."""
    customer_id: UUID
    customer_name: str
    current: Decimal
    days_1_30: Decimal
    days_31_60: Decimal
    days_61_90: Decimal
    days_over_90: Decimal
    total: Decimal


class PaymentSummary(BaseSchema):
    """Schema for payment summary."""
    date: date
    total_payments: Decimal
    payment_count: int
    payment_methods: dict[str, Decimal]  # method -> amount


class ARReport(BaseModel):
    summary: dict


# Enums for filtering
class InvoiceStatusFilter(str, Enum):
    """Invoice status filter options."""
    ALL = 'all'
    DRAFT = 'draft'
    SENT = 'sent'
    VIEWED = 'viewed'
    PARTIALLY_PAID = 'partially_paid'
    PAID = 'paid'
    OVERDUE = 'overdue'
    VOID = 'void'


class DateRangeFilter(BaseModel):
    """Date range filter."""
    start_date: Optional[date] = None
    end_date: Optional[date] = None


# Query parameters
class InvoiceQueryParams(BaseModel):
    """Query parameters for filtering invoices."""
    status: Optional[InvoiceStatusFilter] = InvoiceStatusFilter.ALL
    customer_id: Optional[UUID] = None
    date_range: Optional[DateRangeFilter] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    is_overdue: Optional[bool] = None


class PaymentQueryParams(BaseModel):
    """Query parameters for filtering payments."""
    status: Optional[PaymentStatus] = None
    customer_id: Optional[UUID] = None
    payment_method: Optional[str] = None
    date_range: Optional[DateRangeFilter] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None


# Webhook schemas
class PaymentWebhookData(BaseModel):
    """Schema for payment webhook data."""
    payment_id: UUID
    status: PaymentStatus
    amount: Decimal
    transaction_id: Optional[str] = None
    processed_at: datetime
    metadata: Optional[dict] = None


class DunningSchedule(BaseModel):
    steps: List[dict] # Each step: {"date": date, "action": str, "status": str}


class DunningAction(BaseModel):
    invoice_id: UUID
    action: str
    date: date


class DisputeAction(BaseModel):
    invoice_id: UUID
    action: str
    reason: Optional[str] = None
    date: Optional[date] = None


class DisputeResult(BaseModel):
    invoice_id: UUID
    status: str
    resolution: Optional[str] = None
