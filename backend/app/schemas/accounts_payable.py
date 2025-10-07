"""
Accounts Payable Schemas
"""
from datetime import date, datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator

# from app.schemas.base import BaseSchema


class BillStatus(str, Enum):
    DRAFT = "draft"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    CANCELLED = "cancelled"
    VOID = "void"


class PaymentMethod(str, Enum):
    CHECK = "check"
    BANK_TRANSFER = "bank_transfer"
    CASH = "cash"
    CREDIT_CARD = "credit_card"
    OTHER = "other"


class BillItemBase(BaseModel):
    """Base schema for bill line items"""
    account_id: UUID = Field(..., description="GL Account ID for this line item")
    item_description: str = Field(..., max_length=500)
    quantity: float = Field(1.0, gt=0, description="Quantity of items")
    unit_price: float = Field(..., gt=0, description="Price per unit")
    tax_rate: float = Field(0.0, ge=0, le=1, description="Tax rate as decimal (e.g., 0.1 for 10%)")
    discount_percent: float = Field(0.0, ge=0, le=100, description="Discount percentage (0-100)")
    amount: float = Field(..., gt=0, description="Total amount for this line (quantity * unit_price * (1 - discount_percent/100) * (1 + tax_rate))")

    @validator('amount')
    def validate_amount(cls, v, values):
        if 'quantity' in values and 'unit_price' in values and 'discount_percent' in values and 'tax_rate' in values:
            calculated = (
                values['quantity'] * 
                values['unit_price'] * 
                (1 - values['discount_percent'] / 100) * 
                (1 + values['tax_rate'])
            )
            if abs(v - calculated) > 0.01:  # Allow for floating point precision
                raise ValueError("Amount does not match calculated value based on quantity, price, discount, and tax")
        return v


class BillItemCreate(BillItemBase):
    """Schema for creating a new bill line item"""
    pass


class BillItemUpdate(BillItemBase):
    """Schema for updating a bill line item"""
    pass


class BillItemInDB(BillItemBase):
    """Schema for bill line item in database"""
    id: UUID
    bill_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class BillBase(BaseModel):
    """Base schema for bills"""
    vendor_id: UUID = Field(..., description="Vendor ID")
    bill_date: date = Field(default_factory=date.today)
    due_date: date
    reference: Optional[str] = Field(None, max_length=100)
    terms: Optional[str] = Field(None, max_length=100, description="Payment terms")
    notes: Optional[str] = Field(None, description="Additional notes")
    items: List[BillItemCreate] = Field(..., min_items=1, description="Bill line items")

    @validator('due_date')
    def due_date_after_bill_date(cls, v, values):
        if 'bill_date' in values and v < values['bill_date']:
            raise ValueError("Due date cannot be before bill date")
        return v


class BillCreate(BillBase):
    """Schema for creating a new bill"""
    pass


class BillUpdate(BaseModel):
    """Schema for updating a bill"""
    bill_date: Optional[date] = None
    due_date: Optional[date] = None
    reference: Optional[str] = None
    terms: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[BillStatus] = None

    @validator('due_date')
    def due_date_after_bill_date(cls, v, values, **kwargs):
        if 'bill_date' in values and v and values['bill_date'] and v < values['bill_date']:
            raise ValueError("Due date cannot be before bill date")
        return v


class BillInDB(BaseModel):
    """Schema for bill in database"""
    id: UUID
    bill_number: str
    vendor_id: UUID
    bill_date: date
    due_date: date
    reference: Optional[str]
    terms: Optional[str]
    status: BillStatus
    subtotal: float
    tax_amount: float
    discount_amount: float
    total_amount: float
    amount_paid: float
    balance_due: float
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    created_by_id: UUID
    updated_by_id: UUID
    approved_by_id: Optional[UUID]
    approved_at: Optional[datetime]
    
    # Relationships
    items: List[BillItemInDB] = []
    
    class Config:
        orm_mode = True


class PaymentBase(BaseModel):
    """Base schema for payments"""
    bill_id: UUID = Field(..., description="Bill ID being paid")
    payment_date: date = Field(default_factory=date.today)
    payment_method: PaymentMethod
    reference: Optional[str] = Field(None, max_length=100)
    amount: float = Field(..., gt=0, description="Payment amount")
    notes: Optional[str] = Field(None, description="Additional notes")


class PaymentCreate(PaymentBase):
    """Schema for creating a new payment"""
    pass


class PaymentUpdate(BaseModel):
    """Schema for updating a payment"""
    payment_date: Optional[date] = None
    payment_method: Optional[PaymentMethod] = None
    reference: Optional[str] = None
    amount: Optional[float] = Field(None, gt=0)
    notes: Optional[str] = None
    is_posted: Optional[bool] = None


class PaymentInDB(BaseModel):
    """Schema for payment in database"""
    id: UUID
    payment_number: str
    bill_id: UUID
    payment_date: date
    payment_method: PaymentMethod
    reference: Optional[str]
    amount: float
    notes: Optional[str]
    is_posted: bool
    posted_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    created_by_id: UUID
    updated_by_id: UUID
    
    class Config:
        orm_mode = True


class BillWithPayments(BillInDB):
    """Schema for bill with its payments"""
    payments: List[PaymentInDB] = []


class PaymentWithBill(PaymentInDB):
    """Schema for payment with its bill"""
    bill: Optional[BillInDB] = None
