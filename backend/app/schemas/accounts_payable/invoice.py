"""
Schemas for invoice API endpoints.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field, validator, root_validator

from app.models.enums import InvoiceStatus, PaymentTerms

class InvoiceLineItemBase(BaseModel):
    """Base schema for invoice line item."""
    description: str
    quantity: Decimal = Field(default=1, ge=0)
    unit_price: Decimal = Field(ge=0)
    amount: Optional[Decimal] = None
    account_id: UUID
    tax_code_id: Optional[UUID] = None

    @root_validator
    def calculate_amount(cls, values):
        """Calculate amount if not provided."""
        if values.get('amount') is None and values.get('quantity') is not None and values.get('unit_price') is not None:
            values['amount'] = values['quantity'] * values['unit_price']
        return values

class InvoiceLineItemCreate(InvoiceLineItemBase):
    """Schema for creating an invoice line item."""
    pass

class InvoiceLineItemUpdate(BaseModel):
    """Schema for updating an invoice line item."""
    description: Optional[str] = None
    quantity: Optional[Decimal] = None
    unit_price: Optional[Decimal] = None
    amount: Optional[Decimal] = None
    account_id: Optional[UUID] = None
    tax_code_id: Optional[UUID] = None

class InvoiceLineItemResponse(InvoiceLineItemBase):
    """Schema for invoice line item response."""
    id: UUID
    invoice_id: UUID

    class Config:
        orm_mode = True

class InvoiceBase(BaseModel):
    """Base schema for invoice."""
    vendor_id: UUID
    invoice_number: str
    invoice_date: date
    due_date: date
    description: Optional[str] = None
    reference: Optional[str] = None
    payment_terms: PaymentTerms = PaymentTerms.NET_30
    currency_id: Optional[UUID] = None
    requires_approval: bool = False

class InvoiceCreate(InvoiceBase):
    """Schema for creating an invoice."""
    line_items: List[InvoiceLineItemCreate]
    
    @validator('line_items')
    def validate_line_items(cls, v):
        """Validate that there is at least one line item."""
        if not v:
            raise ValueError("At least one line item is required")
        return v

class InvoiceUpdate(BaseModel):
    """Schema for updating an invoice."""
    invoice_number: Optional[str] = None
    invoice_date: Optional[date] = None
    due_date: Optional[date] = None
    description: Optional[str] = None
    reference: Optional[str] = None
    payment_terms: Optional[PaymentTerms] = None
    currency_id: Optional[UUID] = None
    requires_approval: Optional[bool] = None
    line_items: Optional[List[InvoiceLineItemCreate]] = None

class InvoiceResponse(InvoiceBase):
    """Schema for invoice response."""
    id: UUID
    status: InvoiceStatus
    subtotal: Decimal
    tax_amount: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    paid_amount: Decimal
    balance_due: Decimal
    posting_date: Optional[date] = None
    approved_by_id: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    line_items: List[InvoiceLineItemResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class InvoiceListResponse(BaseModel):
    """Schema for invoice list response."""
    items: List[InvoiceResponse]
    total: int
    page: int
    page_size: int
    pages: int

class InvoiceApprovalRequest(BaseModel):
    """Schema for invoice approval/rejection request."""
    approved_by_id: UUID
    notes: Optional[str] = None