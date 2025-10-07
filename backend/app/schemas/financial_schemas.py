"""
Pydantic schemas for financial models with validation
"""
from pydantic import BaseModel, validator, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class ChartOfAccountsBase(BaseModel):
    account_code: str = Field(..., min_length=1, max_length=20)
    account_name: str = Field(..., min_length=1, max_length=255)
    account_type: str = Field(..., pattern="^(Asset|Liability|Equity|Revenue|Expense)$")
    parent_id: Optional[str] = None
    normal_balance: str = Field(..., pattern="^(Debit|Credit)$")
    is_active: bool = True

class ChartOfAccountsCreate(ChartOfAccountsBase):
    pass

class ChartOfAccountsUpdate(BaseModel):
    account_name: Optional[str] = Field(None, min_length=1, max_length=255)
    is_active: Optional[bool] = None

class ChartOfAccountsResponse(ChartOfAccountsBase):
    id: str
    current_balance: Decimal
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class JournalEntryLineCreate(BaseModel):
    account_id: str
    description: Optional[str] = Field(None, max_length=255)
    debit_amount: Decimal = Field(0, ge=0)
    credit_amount: Decimal = Field(0, ge=0)
    
    @validator('debit_amount', 'credit_amount')
    def validate_amounts(cls, v, values):
        if 'debit_amount' in values and 'credit_amount' in values:
            if values['debit_amount'] > 0 and values['credit_amount'] > 0:
                raise ValueError('Cannot have both debit and credit amounts')
            if values['debit_amount'] == 0 and values['credit_amount'] == 0:
                raise ValueError('Must have either debit or credit amount')
        return v

class JournalEntryCreate(BaseModel):
    description: str = Field(..., min_length=1)
    reference: Optional[str] = Field(None, max_length=100)
    entry_date: datetime
    lines: List[JournalEntryLineCreate] = Field(..., min_items=2)
    
    @validator('lines')
    def validate_balanced_entry(cls, v):
        total_debit = sum(line.debit_amount for line in v)
        total_credit = sum(line.credit_amount for line in v)
        if abs(total_debit - total_credit) > Decimal('0.01'):
            raise ValueError('Journal entry must be balanced (debits = credits)')
        return v

class JournalEntryResponse(BaseModel):
    id: str
    entry_number: str
    description: str
    reference: Optional[str]
    entry_date: datetime
    status: str
    total_debit: Decimal
    total_credit: Decimal
    created_at: datetime
    
    class Config:
        from_attributes = True

class VendorBase(BaseModel):
    vendor_code: str = Field(..., min_length=1, max_length=20)
    vendor_name: str = Field(..., min_length=1, max_length=255)
    contact_person: Optional[str] = Field(None, max_length=255)
    email: Optional[str] = Field(None, pattern=r'^[^@]+@[^@]+\.[^@]+$')
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    tax_id: Optional[str] = Field(None, max_length=50)
    payment_terms: Optional[str] = Field(None, max_length=50)
    credit_limit: Decimal = Field(0, ge=0)

class VendorCreate(VendorBase):
    pass

class VendorUpdate(BaseModel):
    vendor_name: Optional[str] = Field(None, min_length=1, max_length=255)
    contact_person: Optional[str] = Field(None, max_length=255)
    email: Optional[str] = Field(None, pattern=r'^[^@]+@[^@]+\.[^@]+$')
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    payment_terms: Optional[str] = Field(None, max_length=50)
    credit_limit: Optional[Decimal] = Field(None, ge=0)
    is_active: Optional[bool] = None

class VendorResponse(VendorBase):
    id: str
    current_balance: Decimal
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class CustomerBase(BaseModel):
    customer_code: str = Field(..., min_length=1, max_length=20)
    customer_name: str = Field(..., min_length=1, max_length=255)
    contact_person: Optional[str] = Field(None, max_length=255)
    email: Optional[str] = Field(None, pattern=r'^[^@]+@[^@]+\.[^@]+$')
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    tax_id: Optional[str] = Field(None, max_length=50)
    payment_terms: Optional[str] = Field(None, max_length=50)
    credit_limit: Decimal = Field(0, ge=0)

class CustomerCreate(CustomerBase):
    pass

class CustomerResponse(CustomerBase):
    id: str
    current_balance: Decimal
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class BillCreate(BaseModel):
    vendor_id: str
    bill_date: datetime
    due_date: datetime
    total_amount: Decimal = Field(..., gt=0)
    description: Optional[str] = None
    
    @validator('due_date')
    def validate_due_date(cls, v, values):
        if 'bill_date' in values and v < values['bill_date']:
            raise ValueError('Due date cannot be before bill date')
        return v

class BillResponse(BaseModel):
    id: str
    bill_number: str
    vendor_id: str
    bill_date: datetime
    due_date: datetime
    total_amount: Decimal
    paid_amount: Decimal
    remaining_amount: Decimal
    status: str
    description: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class InvoiceCreate(BaseModel):
    customer_id: str
    invoice_date: datetime
    due_date: datetime
    total_amount: Decimal = Field(..., gt=0)
    description: Optional[str] = None
    
    @validator('due_date')
    def validate_due_date(cls, v, values):
        if 'invoice_date' in values and v < values['invoice_date']:
            raise ValueError('Due date cannot be before invoice date')
        return v

class InvoiceResponse(BaseModel):
    id: str
    invoice_number: str
    customer_id: str
    invoice_date: datetime
    due_date: datetime
    total_amount: Decimal
    paid_amount: Decimal
    remaining_amount: Decimal
    status: str
    description: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class PaymentCreate(BaseModel):
    amount: Decimal = Field(..., gt=0)
    payment_date: datetime
    payment_method: str = Field(..., pattern="^(check|wire|ach|credit_card|cash)$")
    reference: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None

class VendorPaymentCreate(PaymentCreate):
    vendor_id: str
    bill_id: Optional[str] = None

class CustomerPaymentCreate(PaymentCreate):
    customer_id: str
    invoice_id: Optional[str] = None

class PaymentResponse(BaseModel):
    id: str
    payment_number: str
    payment_date: datetime
    amount: Decimal
    payment_method: str
    reference: Optional[str]
    description: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
