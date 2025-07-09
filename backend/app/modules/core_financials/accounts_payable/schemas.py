import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field

from .models import BillStatus, PaymentStatus

# ================================================
#                Vendor Schemas
# ================================================

class VendorBase(BaseModel):
    name: str = Field(..., max_length=255)
    contact_person: Optional[str] = Field(None, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    tax_id: Optional[str] = Field(None, max_length=100)
    default_currency: str = Field('USD', max_length=3)
    is_active: bool = True

class VendorCreate(VendorBase):
    pass

class VendorUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    contact_person: Optional[str] = Field(None, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    tax_id: Optional[str] = Field(None, max_length=100)
    default_currency: Optional[str] = Field(None, max_length=3)
    is_active: Optional[bool] = None

class Vendor(VendorBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# ================================================
#                  Bill Schemas
# ================================================

class BillLineItemBase(BaseModel):
    account_id: uuid.UUID
    description: str
    quantity: Decimal = Field(..., gt=0)
    unit_price: Decimal = Field(..., ge=0)

class BillLineItemCreate(BillLineItemBase):
    pass

class BillLineItem(BillLineItemBase):
    id: uuid.UUID
    total_price: Decimal

    class Config:
        orm_mode = True

class BillBase(BaseModel):
    vendor_id: uuid.UUID
    bill_number: str = Field(..., max_length=100)
    issue_date: date
    due_date: date
    currency: str = Field('USD', max_length=3)
    notes: Optional[str] = None

class BillCreate(BillBase):
    line_items: List[BillLineItemCreate]

class BillUpdate(BaseModel):
    bill_number: Optional[str] = Field(None, max_length=100)
    issue_date: Optional[date] = None
    due_date: Optional[date] = None
    notes: Optional[str] = None
    status: Optional[BillStatus] = None # Allow status changes, e.g., to VOID

class Bill(BillBase):
    id: uuid.UUID
    total_amount: Decimal
    amount_paid: Decimal
    status: BillStatus
    created_at: datetime
    updated_at: datetime
    line_items: List[BillLineItem]
    vendor: Vendor # Include vendor details

    class Config:
        orm_mode = True

# ================================================
#                Payment Schemas
# ================================================

class PaymentAllocationCreate(BaseModel):
    bill_id: uuid.UUID
    amount_allocated: Decimal = Field(..., gt=0)

class PaymentAllocation(PaymentAllocationCreate):
    id: uuid.UUID

    class Config:
        orm_mode = True

class PaymentBase(BaseModel):
    vendor_id: uuid.UUID
    payment_date: date
    amount: Decimal = Field(..., gt=0)
    currency: str = Field('USD', max_length=3)
    payment_method: Optional[str] = Field(None, max_length=100)
    reference_number: Optional[str] = Field(None, max_length=255)

class PaymentCreate(PaymentBase):
    allocations: List[PaymentAllocationCreate]

class PaymentUpdate(BaseModel):
    payment_date: Optional[date] = None
    payment_method: Optional[str] = Field(None, max_length=100)
    reference_number: Optional[str] = Field(None, max_length=255)
    status: Optional[PaymentStatus] = None

class Payment(PaymentBase):
    id: uuid.UUID
    status: PaymentStatus
    created_at: datetime
    updated_at: datetime
    allocations: List[PaymentAllocation]
    vendor: Vendor

    class Config:
        orm_mode = True
