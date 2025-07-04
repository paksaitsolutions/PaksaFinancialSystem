"""
Pydantic schemas for Payslip-related models in the Payroll module.
"""
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, validator, root_validator

from app.modules.payroll.models import PayslipStatus, PayComponentType

class PayslipEarningBase(BaseModel):
    """Base schema for payslip earnings."""
    component_id: UUID
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    amount: Decimal = Field(..., gt=0, max_digits=12, decimal_places=2)
    quantity: Decimal = Field(1, gt=0, max_digits=10, decimal_places=2)
    rate: Optional[Decimal] = Field(None, gt=0, max_digits=12, decimal_places=4)
    is_taxable: bool = True
    metadata: Dict[str, Any] = {}

class PayslipEarningCreate(PayslipEarningBase):
    """Schema for creating a new payslip earning."""
    pass

class PayslipEarningUpdate(BaseModel):
    """Schema for updating a payslip earning."""
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    amount: Optional[Decimal] = Field(None, gt=0, max_digits=12, decimal_places=2)
    quantity: Optional[Decimal] = Field(None, gt=0, max_digits=10, decimal_places=2)
    rate: Optional[Decimal] = Field(None, gt=0, max_digits=12, decimal_places=4)
    is_taxable: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None

class PayslipEarningInDB(PayslipEarningBase):
    """Schema for payslip earning in the database."""
    id: UUID
    payslip_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class PayslipDeductionBase(BaseModel):
    """Base schema for payslip deductions."""
    component_id: UUID
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    amount: Decimal = Field(..., gt=0, max_digits=12, decimal_places=2)
    is_pretax: bool = False
    metadata: Dict[str, Any] = {}

class PayslipDeductionCreate(PayslipDeductionBase):
    """Schema for creating a new payslip deduction."""
    pass

class PayslipDeductionUpdate(BaseModel):
    """Schema for updating a payslip deduction."""
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    amount: Optional[Decimal] = Field(None, gt=0, max_digits=12, decimal_places=2)
    is_pretax: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None

class PayslipDeductionInDB(PayslipDeductionBase):
    """Schema for payslip deduction in the database."""
    id: UUID
    payslip_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class PayslipTaxBase(BaseModel):
    """Base schema for payslip taxes."""
    tax_name: str = Field(..., max_length=100)
    tax_code: str = Field(..., max_length=20)
    taxable_amount: Decimal = Field(..., ge=0, max_digits=12, decimal_places=2)
    tax_amount: Decimal = Field(..., ge=0, max_digits=12, decimal_places=2)
    tax_rate: Decimal = Field(..., ge=0, max_digits=5, decimal_places=4)
    is_employer_share: bool = False
    metadata: Dict[str, Any] = {}

class PayslipTaxCreate(PayslipTaxBase):
    """Schema for creating a new payslip tax."""
    pass

class PayslipTaxUpdate(BaseModel):
    """Schema for updating a payslip tax."""
    tax_name: Optional[str] = Field(None, max_length=100)
    tax_code: Optional[str] = Field(None, max_length=20)
    taxable_amount: Optional[Decimal] = Field(None, ge=0, max_digits=12, decimal_places=2)
    tax_amount: Optional[Decimal] = Field(None, ge=0, max_digits=12, decimal_places=2)
    tax_rate: Optional[Decimal] = Field(None, ge=0, max_digits=5, decimal_places=4)
    is_employer_share: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None

class PayslipTaxInDB(PayslipTaxBase):
    """Schema for payslip tax in the database."""
    id: UUID
    payslip_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class PayslipBase(BaseModel):
    """Base schema for payslips."""
    employee_payroll_id: UUID
    pay_period_id: UUID
    payslip_number: str = Field(..., max_length=50)
    status: PayslipStatus = PayslipStatus.DRAFT
    
    # Dates
    pay_date: date
    period_start_date: date
    period_end_date: date
    
    # Totals
    gross_pay: Decimal = Field(0, ge=0, max_digits=12, decimal_places=2)
    total_deductions: Decimal = Field(0, ge=0, max_digits=12, decimal_places=2)
    total_taxes: Decimal = Field(0, ge=0, max_digits=12, decimal_places=2)
    total_benefits: Decimal = Field(0, ge=0, max_digits=12, decimal_places=2)
    net_pay: Decimal = Field(0, ge=0, max_digits=12, decimal_places=2)
    
    # Payment details
    payment_method: Optional[str] = Field(None, max_length=50)
    payment_reference: Optional[str] = Field(None, max_length=100)
    payment_date: Optional[date] = None
    
    # Additional data
    notes: Optional[str] = None
    metadata: Dict[str, Any] = {}

    @root_validator
    def validate_dates(cls, values):
        if values.get('period_end_date') <= values.get('period_start_date'):
            raise ValueError("Period end date must be after start date")
        if values.get('payment_date') and values['payment_date'] < values.get('period_end_date'):
            raise ValueError("Payment date must be on or after period end date")
        return values

class PayslipCreate(PayslipBase):
    """Schema for creating a new payslip."""
    earnings: List[PayslipEarningCreate] = []
    deductions: List[PayslipDeductionCreate] = []
    taxes: List[PayslipTaxCreate] = []

class PayslipUpdate(BaseModel):
    """Schema for updating a payslip."""
    status: Optional[PayslipStatus] = None
    payment_method: Optional[str] = Field(None, max_length=50)
    payment_reference: Optional[str] = Field(None, max_length=100)
    payment_date: Optional[date] = None
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class PayslipInDB(PayslipBase):
    """Schema for payslip in the database."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    # Relationships
    earnings: List[PayslipEarningInDB] = []
    deductions: List[PayslipDeductionInDB] = []
    taxes: List[PayslipTaxInDB] = []

    class Config:
        orm_mode = True

class PayslipResponse(PayslipInDB):
    """Response schema for payslips with related data."""
    employee_name: Optional[str] = None
    employee_number: Optional[str] = None
    department: Optional[str] = None
    job_title: Optional[str] = None
    
    class Config:
        json_encoders = {
            Decimal: lambda v: str(v),
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
        }

class PayslipSummary(BaseModel):
    """Summary of payslip for listing."""
    id: UUID
    payslip_number: str
    employee_name: str
    employee_number: str
    department: str
    job_title: str
    period_start_date: date
    period_end_date: date
    pay_date: date
    gross_pay: Decimal
    total_deductions: Decimal
    total_taxes: Decimal
    net_pay: Decimal
    status: PayslipStatus
    
    class Config:
        orm_mode = True
        json_encoders = {
            Decimal: lambda v: str(v),
            date: lambda v: v.isoformat(),
        }

class PayrollSummary(BaseModel):
    """Summary of payroll for a period."""
    pay_period_id: UUID
    period_name: str
    period_start_date: date
    period_end_date: date
    employee_count: int
    total_gross_pay: Decimal
    total_deductions: Decimal
    total_taxes: Decimal
    total_net_pay: Decimal
    
    class Config:
        orm_mode = True
        json_encoders = {
            Decimal: lambda v: str(v),
            date: lambda v: v.isoformat(),
        }
