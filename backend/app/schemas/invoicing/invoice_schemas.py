"""
Invoicing schemas.
"""
from typing import List, Optional
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel

class InvoiceItemBase(BaseModel):
    """Base invoice item schema."""
    description: str
    quantity: Decimal
    unit_price: Decimal
    total_price: Decimal

class InvoiceItemCreate(InvoiceItemBase):
    """Create invoice item schema."""
    pass

class InvoiceItemResponse(InvoiceItemBase):
    """Invoice item response schema."""
    id: UUID
    invoice_id: UUID

    class Config:
        orm_mode = True

class InvoiceTemplateBase(BaseModel):
    """Base invoice template schema."""
    name: str
    template_html: str
    is_default: bool = False
    is_active: bool = True

class InvoiceTemplateCreate(InvoiceTemplateBase):
    """Create invoice template schema."""
    pass

class InvoiceTemplateResponse(InvoiceTemplateBase):
    """Invoice template response schema."""
    id: UUID
    tenant_id: UUID
    created_at: datetime

    class Config:
        orm_mode = True

class InvoiceBase(BaseModel):
    """Base invoice schema."""
    customer_id: UUID
    template_id: Optional[UUID] = None
    issue_date: date
    due_date: date
    subtotal: Decimal
    tax_amount: Decimal = 0
    total_amount: Decimal
    notes: Optional[str] = None
    terms: Optional[str] = None
    is_recurring: bool = False
    recurring_frequency: Optional[str] = None
    next_invoice_date: Optional[date] = None

class InvoiceCreate(InvoiceBase):
    """Create invoice schema."""
    items: List[InvoiceItemCreate]

class InvoiceUpdate(BaseModel):
    """Update invoice schema."""
    customer_id: Optional[UUID] = None
    template_id: Optional[UUID] = None
    due_date: Optional[date] = None
    subtotal: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    total_amount: Optional[Decimal] = None
    status: Optional[str] = None
    payment_status: Optional[str] = None
    notes: Optional[str] = None
    terms: Optional[str] = None

class InvoiceResponse(InvoiceBase):
    """Invoice response schema."""
    id: UUID
    tenant_id: UUID
    invoice_number: str
    status: str
    payment_status: str
    items: List[InvoiceItemResponse]
    sent_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class InvoicePaymentBase(BaseModel):
    """Base invoice payment schema."""
    payment_date: date
    amount: Decimal
    payment_method: str
    reference: Optional[str] = None
    notes: Optional[str] = None

class InvoicePaymentCreate(InvoicePaymentBase):
    """Create invoice payment schema."""
    pass

class InvoicePaymentResponse(InvoicePaymentBase):
    """Invoice payment response schema."""
    id: UUID
    invoice_id: UUID
    created_at: datetime

    class Config:
        orm_mode = True

class InvoiceApprovalBase(BaseModel):
    """Base invoice approval schema."""
    status: str  # pending, approved, rejected
    comments: Optional[str] = None

class InvoiceApprovalCreate(InvoiceApprovalBase):
    """Create invoice approval schema."""
    pass

class InvoiceApprovalResponse(InvoiceApprovalBase):
    """Invoice approval response schema."""
    id: UUID
    invoice_id: UUID
    approver_id: UUID
    approved_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        orm_mode = True