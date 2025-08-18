"""
Pydantic schemas for Accounts Receivable module.
"""
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field, validator, root_validator

from schemas.base import BaseSchema


class InvoiceStatus(str, Enum):
    """Status of an invoice."""
    DRAFT = "draft"
    SENT = "sent"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    WRITTEN_OFF = "written_off"


class PaymentMethod(str, Enum):
    """Payment methods for customer payments."""
    CASH = "cash"
    CHECK = "check"
    CREDIT_CARD = "credit_card"
    BANK_TRANSFER = "bank_transfer"
    DIGITAL_WALLET = "digital_wallet"
    OTHER = "other"


class InvoiceItemBase(BaseModel):
    """Base schema for invoice line items."""
    product_id: Optional[UUID] = Field(None, description="Product ID (if applicable)")
    account_id: UUID = Field(..., description="GL Account ID for this line item")
    description: str = Field(..., max_length=500, description="Item description")
    quantity: Decimal = Field(..., gt=0, description="Quantity of items")
    unit_price: Decimal = Field(..., ge=0, description="Price per unit")
    tax_rate: Decimal = Field(0, ge=0, le=1, description="Tax rate as decimal (e.g., 0.1 for 10%)")
    discount_percent: Decimal = Field(0, ge=0, le=100, description="Discount percentage (0-100)")
    amount: Decimal = Field(..., gt=0, description="Total amount for this line")

    @validator('amount')
    def validate_amount(cls, v, values):
        if 'quantity' in values and 'unit_price' in values and 'discount_percent' in values and 'tax_rate' in values:
            calculated = (
                values['quantity'] * 
                values['unit_price'] * 
                (1 - values['discount_percent'] / 100) * 
                (1 + values['tax_rate'])
            )
            if abs(float(v) - float(calculated)) > 0.01:  # Allow for floating point precision
                raise ValueError("Amount does not match calculated value based on quantity, price, discount, and tax")
        return v


class InvoiceItemCreate(InvoiceItemBase):
    """Schema for creating a new invoice line item."""
    pass


class InvoiceItemUpdate(InvoiceItemBase):
    """Schema for updating an existing invoice line item."""
    pass


class InvoiceItemInDB(InvoiceItemBase):
    """Schema for invoice line item in database."""
    id: UUID
    invoice_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class InvoiceBase(BaseModel):
    """Base schema for invoices."""
    customer_id: UUID = Field(..., description="Customer ID")
    issue_date: date = Field(default_factory=date.today, description="Date the invoice was issued")
    due_date: date = Field(..., description="Payment due date")
    reference: Optional[str] = Field(None, max_length=100, description="Reference number or code")
    terms: Optional[str] = Field(None, max_length=200, description="Payment terms")
    notes: Optional[str] = Field(None, description="Additional notes")
    items: List[InvoiceItemCreate] = Field(..., min_items=1, description="Invoice line items")

    @validator('due_date')
    def due_date_after_issue_date(cls, v, values):
        if 'issue_date' in values and v < values['issue_date']:
            raise ValueError("Due date must be on or after the issue date")
        return v


class InvoiceCreate(InvoiceBase):
    """Schema for creating a new invoice."""
    pass


class InvoiceUpdate(BaseModel):
    """Schema for updating an existing invoice."""
    customer_id: Optional[UUID] = None
    issue_date: Optional[date] = None
    due_date: Optional[date] = None
    reference: Optional[str] = None
    terms: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[InvoiceStatus] = None
    items: Optional[List[Union[InvoiceItemCreate, InvoiceItemUpdate]]] = None

    @root_validator
    def validate_dates(cls, values):
        issue_date = values.get('issue_date')
        due_date = values.get('due_date')
        
        if issue_date and due_date and due_date < issue_date:
            raise ValueError("Due date must be on or after the issue date")
            
        return values


class InvoiceInDB(BaseSchema):
    """Schema for invoice in database."""
    id: UUID
    invoice_number: str
    customer_id: UUID
    issue_date: date
    due_date: date
    paid_date: Optional[date]
    status: InvoiceStatus
    reference: Optional[str]
    terms: Optional[str]
    notes: Optional[str]
    subtotal: Decimal
    tax_amount: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    amount_paid: Decimal
    balance_due: Decimal
    is_recurring: bool
    recurring_invoice_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    created_by_id: UUID
    updated_by_id: UUID
    
    # Relationships
    items: List[InvoiceItemInDB] = []
    
    class Config:
        orm_mode = True


class PaymentReceiptBase(BaseModel):
    """Base schema for payment receipts."""
    invoice_id: UUID = Field(..., description="Invoice ID being paid")
    customer_id: UUID = Field(..., description="Customer ID making the payment")
    payment_date: date = Field(default_factory=date.today, description="Date payment was received")
    payment_method: PaymentMethod = Field(..., description="Payment method used")
    reference: Optional[str] = Field(None, max_length=100, description="Payment reference number")
    amount: Decimal = Field(..., gt=0, description="Payment amount")
    notes: Optional[str] = Field(None, description="Additional notes about the payment")


class PaymentReceiptCreate(PaymentReceiptBase):
    """Schema for creating a new payment receipt."""
    pass


class PaymentReceiptUpdate(BaseModel):
    """Schema for updating an existing payment receipt."""
    payment_date: Optional[date] = None
    payment_method: Optional[PaymentMethod] = None
    reference: Optional[str] = None
    amount: Optional[Decimal] = Field(None, gt=0)
    notes: Optional[str] = None
    is_posted: Optional[bool] = None


class PaymentReceiptInDB(BaseSchema):
    """Schema for payment receipt in database."""
    id: UUID
    receipt_number: str
    invoice_id: UUID
    customer_id: UUID
    payment_date: date
    payment_method: PaymentMethod
    reference: Optional[str]
    amount: Decimal
    notes: Optional[str]
    is_posted: bool
    posted_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    created_by_id: UUID
    updated_by_id: UUID
    
    class Config:
        orm_mode = True


class InvoiceWithPayments(InvoiceInDB):
    """Schema for invoice with its payments."""
    payments: List[PaymentReceiptInDB] = []


class PaymentWithInvoice(PaymentReceiptInDB):
    """Schema for payment with its invoice."""
    invoice: Optional[InvoiceInDB] = None


class InvoiceStatusUpdate(BaseModel):
    """Schema for updating invoice status."""
    status: InvoiceStatus
    notes: Optional[str] = None


class PaymentPosting(BaseModel):
    """Schema for posting a payment to the general ledger."""
    post_date: date = Field(default_factory=date.today, description="Date to post the payment")
    account_id: UUID = Field(..., description="GL Account ID to post the payment to")
    reference: Optional[str] = Field(None, description="Reference for the GL entry")
    notes: Optional[str] = Field(None, description="Additional notes for the GL entry")
