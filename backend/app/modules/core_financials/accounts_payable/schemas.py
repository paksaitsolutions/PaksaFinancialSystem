from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
from enum import Enum

class VendorCategory(str, Enum):
    SUPPLIER = "supplier"
    CONTRACTOR = "contractor"
    SERVICE = "service"

class VendorStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class PaymentTerms(str, Enum):
    NET_15 = "net15"
    NET_30 = "net30"
    NET_60 = "net60"
    DUE_ON_RECEIPT = "due_on_receipt"

class InvoiceStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"

class PaymentMethod(str, Enum):
    CHECK = "check"
    ACH = "ach"
    WIRE = "wire"
    CARD = "card"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    PROCESSED = "processed"
    FAILED = "failed"
    CANCELLED = "cancelled"

# Vendor Schemas
class VendorBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    category: VendorCategory
    contact_person: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    tax_id: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = Field(None, max_length=500)
    payment_terms: PaymentTerms = PaymentTerms.NET_30
    status: VendorStatus = VendorStatus.ACTIVE

class VendorCreate(VendorBase):
    pass

class VendorUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    category: Optional[VendorCategory] = None
    contact_person: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    tax_id: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = Field(None, max_length=500)
    payment_terms: Optional[PaymentTerms] = None
    status: Optional[VendorStatus] = None

class VendorResponse(VendorBase):
    id: int
    vendor_id: str
    outstanding_balance: Decimal = Field(default=Decimal('0.00'))
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Invoice Line Schemas
class InvoiceLineBase(BaseModel):
    description: str = Field(..., min_length=1, max_length=500)
    quantity: Decimal = Field(..., gt=0)
    unit_price: Decimal = Field(..., ge=0)
    account_id: Optional[int] = None

class InvoiceLineCreate(InvoiceLineBase):
    pass

class InvoiceLineUpdate(BaseModel):
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    quantity: Optional[Decimal] = Field(None, gt=0)
    unit_price: Optional[Decimal] = Field(None, ge=0)
    account_id: Optional[int] = None

class InvoiceLineResponse(InvoiceLineBase):
    id: int
    line_total: Decimal
    created_at: datetime

    class Config:
        from_attributes = True

# Invoice Schemas
class InvoiceBase(BaseModel):
    vendor_id: int
    invoice_number: str = Field(..., min_length=1, max_length=100)
    invoice_date: date
    due_date: date
    description: Optional[str] = Field(None, max_length=1000)
    tax_amount: Decimal = Field(default=Decimal('0.00'), ge=0)
    status: InvoiceStatus = InvoiceStatus.DRAFT

class InvoiceCreate(InvoiceBase):
    lines: List[InvoiceLineCreate] = Field(..., min_items=1)

class InvoiceUpdate(BaseModel):
    vendor_id: Optional[int] = None
    invoice_number: Optional[str] = Field(None, min_length=1, max_length=100)
    invoice_date: Optional[date] = None
    due_date: Optional[date] = None
    description: Optional[str] = Field(None, max_length=1000)
    tax_amount: Optional[Decimal] = Field(None, ge=0)
    status: Optional[InvoiceStatus] = None
    lines: Optional[List[InvoiceLineCreate]] = None

class InvoiceResponse(InvoiceBase):
    id: int
    subtotal: Decimal
    total_amount: Decimal
    paid_amount: Decimal = Field(default=Decimal('0.00'))
    balance_due: Decimal
    vendor_name: str
    lines: List[InvoiceLineResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Payment Schemas
class PaymentBase(BaseModel):
    vendor_id: int
    payment_method: PaymentMethod
    payment_date: date
    reference_number: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=1000)

class PaymentCreate(PaymentBase):
    invoice_ids: List[int] = Field(..., min_items=1)
    amount: Decimal = Field(..., gt=0)

class PaymentUpdate(BaseModel):
    payment_method: Optional[PaymentMethod] = None
    payment_date: Optional[date] = None
    reference_number: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=1000)
    status: Optional[PaymentStatus] = None

class PaymentResponse(PaymentBase):
    id: int
    payment_number: str
    amount: Decimal
    status: PaymentStatus
    vendor_name: str
    invoice_numbers: List[str] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Dashboard/Analytics Schemas
class APSummaryResponse(BaseModel):
    total_outstanding: Decimal
    overdue_amount: Decimal
    this_month_invoices: Decimal
    pending_approval: Decimal
    total_vendors: int
    active_vendors: int

class VendorSummaryResponse(BaseModel):
    vendor_id: int
    vendor_name: str
    total_invoices: int
    outstanding_balance: Decimal
    last_payment_date: Optional[date]
    payment_terms: PaymentTerms

class AgingReportItem(BaseModel):
    vendor_id: int
    vendor_name: str
    current: Decimal = Field(default=Decimal('0.00'))
    days_1_30: Decimal = Field(default=Decimal('0.00'))
    days_31_60: Decimal = Field(default=Decimal('0.00'))
    days_61_90: Decimal = Field(default=Decimal('0.00'))
    over_90_days: Decimal = Field(default=Decimal('0.00'))
    total_outstanding: Decimal

class AgingReportResponse(BaseModel):
    report_date: date
    items: List[AgingReportItem]
    totals: AgingReportItem

# Bulk Operations
class BulkApprovalRequest(BaseModel):
    invoice_ids: List[int] = Field(..., min_items=1)
    approved_by: str
    approval_notes: Optional[str] = None

class BulkPaymentRequest(BaseModel):
    payment_requests: List[PaymentCreate] = Field(..., min_items=1)
    batch_reference: Optional[str] = None