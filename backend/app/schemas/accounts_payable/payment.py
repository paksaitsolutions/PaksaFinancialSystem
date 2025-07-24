"""
Schemas for payment API endpoints.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field, validator

from app.models.enums import PaymentStatus, PaymentMethod

class PaymentInvoiceBase(BaseModel):
    """Base schema for payment-invoice association."""
    invoice_id: UUID
    amount: Decimal = Field(gt=0)

class PaymentInvoiceCreate(PaymentInvoiceBase):
    """Schema for creating a payment-invoice association."""
    pass

class PaymentInvoiceResponse(PaymentInvoiceBase):
    """Schema for payment-invoice association response."""
    id: UUID
    payment_id: UUID
    invoice_number: str
    invoice_total: Decimal
    invoice_balance_before: Decimal
    invoice_balance_after: Decimal

    class Config:
        orm_mode = True

class PaymentBase(BaseModel):
    """Base schema for payment."""
    vendor_id: UUID
    payment_date: date
    amount: Decimal = Field(gt=0)
    payment_method: PaymentMethod
    reference: Optional[str] = None
    memo: Optional[str] = None

class PaymentCreate(PaymentBase):
    """Schema for creating a payment."""
    invoices: List[PaymentInvoiceCreate]
    
    @validator('invoices')
    def validate_invoices(cls, v):
        """Validate that there is at least one invoice."""
        if not v:
            raise ValueError("At least one invoice is required")
        return v

class PaymentUpdate(BaseModel):
    """Schema for updating a payment."""
    payment_date: Optional[date] = None
    payment_method: Optional[PaymentMethod] = None
    reference: Optional[str] = None
    memo: Optional[str] = None

class PaymentResponse(PaymentBase):
    """Schema for payment response."""
    id: UUID
    payment_number: str
    status: PaymentStatus
    created_at: datetime
    updated_at: datetime
    invoices: List[PaymentInvoiceResponse] = []

    class Config:
        orm_mode = True

class PaymentListResponse(BaseModel):
    """Schema for payment list response."""
    items: List[PaymentResponse]
    total: int
    page: int
    page_size: int
    pages: int

class PaymentVoidRequest(BaseModel):
    """Schema for voiding a payment."""
    reason: str