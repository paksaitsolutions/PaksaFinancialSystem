"""
Pydantic schemas for Tax Filing and Payment request/response validation.
"""
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator, condecimal
from uuid import UUID

# Shared schemas
class TaxFilingStatus(str, Enum):
    DRAFT = "DRAFT"
    PENDING = "PENDING"
    FILED = "FILED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    AMENDED = "AMENDED"
    CANCELLED = "CANCELLED"

class TaxPaymentStatus(str, Enum):
    PENDING = "PENDING"
    SCHEDULED = "SCHEDULED"
    PROCESSING = "PROCESSING"
    PAID = "PAID"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"
    CANCELLED = "CANCELLED"

# Tax Filing schemas
class TaxFilingBase(BaseModel):
    tax_agency_id: UUID
    tax_year: int = Field(..., ge=1900, le=2100)
    tax_period: str  # MONTHLY, QUARTERLY, ANNUAL
    start_date: date
    end_date: date
    due_date: date
    filing_method: Optional[str] = None
    notes: Optional[str] = None

class TaxFilingCreate(TaxFilingBase):
    pass

class TaxFilingUpdate(BaseModel):
    status: Optional[TaxFilingStatus] = None
    filing_method: Optional[str] = None
    confirmation_number: Optional[str] = None
    notes: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None

class TaxFilingResponse(TaxFilingBase):
    id: UUID
    filing_reference: str
    status: TaxFilingStatus
    total_taxable_wages: Decimal = Field(0, ge=0, decimal_places=2)
    total_tax_withheld: Decimal = Field(0, ge=0, decimal_places=2)
    total_employer_tax: Decimal = Field(0, ge=0, decimal_places=2)
    total_interest_penalties: Decimal = Field(0, ge=0, decimal_places=2)
    total_amount_due: Decimal = Field(0, ge=0, decimal_places=2)
    payment_status: TaxPaymentStatus
    filed_at: Optional[datetime] = None
    accepted_at: Optional[datetime] = None
    rejected_at: Optional[datetime] = None
    rejected_reason: Optional[str] = None
    payment_date: Optional[date] = None
    payment_reference: Optional[str] = None
    payment_method: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime]
    custom_fields: Dict[str, Any]
    
    class Config:
        orm_mode = True

# Tax Filing Detail schemas
class TaxFilingDetailBase(BaseModel):
    tax_code_id: UUID
    employee_id: UUID
    taxable_wages: Decimal = Field(..., ge=0, decimal_places=2)
    tax_withheld: Decimal = Field(..., ge=0, decimal_places=2)
    employer_tax: Decimal = Field(0, ge=0, decimal_places=2)
    withholding_allowances: int = Field(0, ge=0)
    additional_withholding: Decimal = Field(0, ge=0, decimal_places=2)

class TaxFilingDetailCreate(TaxFilingDetailBase):
    tax_filing_id: UUID

class TaxFilingDetailUpdate(BaseModel):
    taxable_wages: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    tax_withheld: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    employer_tax: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    withholding_allowances: Optional[int] = Field(None, ge=0)
    additional_withholding: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    custom_fields: Optional[Dict[str, Any]] = None

class TaxFilingDetailResponse(TaxFilingDetailBase):
    id: UUID
    tax_filing_id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    custom_fields: Dict[str, Any]
    
    class Config:
        orm_mode = True

# Tax Payment schemas
class TaxPaymentBase(BaseModel):
    payment_date: date
    payment_method: str
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    fee_amount: Decimal = Field(0, ge=0, decimal_places=2)
    bank_account_id: Optional[UUID] = None
    notes: Optional[str] = None

class TaxPaymentCreate(TaxPaymentBase):
    tax_filing_id: UUID

class TaxPaymentUpdate(BaseModel):
    payment_date: Optional[date] = None
    payment_method: Optional[str] = None
    amount: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    fee_amount: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    status: Optional[TaxPaymentStatus] = None
    confirmation_number: Optional[str] = None
    failure_reason: Optional[str] = None
    notes: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None

class TaxPaymentResponse(TaxPaymentBase):
    id: UUID
    tax_filing_id: UUID
    payment_reference: str
    status: TaxPaymentStatus
    total_amount: Decimal = Field(..., ge=0, decimal_places=2)
    confirmation_number: Optional[str] = None
    failure_reason: Optional[str] = None
    processed_at: Optional[datetime] = None
    gl_journal_entry_id: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime]
    custom_fields: Dict[str, Any]
    
    class Config:
        orm_mode = True

# Tax Filing with Details Response
class TaxFilingDetailResponse(TaxFilingResponse):
    tax_filing_details: List[TaxFilingDetailResponse] = []
    tax_payments: List[TaxPaymentResponse] = []
    
    class Config:
        orm_mode = True

# Tax Agency schemas
class TaxAgencyBase(BaseModel):
    name: str
    tax_id: str
    tax_type: str  # FEDERAL, STATE, LOCAL, etc.
    jurisdiction: str
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    postal_code: str
    country: str
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    is_active: bool = True
    notes: Optional[str] = None

class TaxAgencyCreate(TaxAgencyBase):
    pass

class TaxAgencyUpdate(BaseModel):
    name: Optional[str] = None
    tax_id: Optional[str] = None
    tax_type: Optional[str] = None
    jurisdiction: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None

class TaxAgencyResponse(TaxAgencyBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    custom_fields: Dict[str, Any]
    
    class Config:
        orm_mode = True
