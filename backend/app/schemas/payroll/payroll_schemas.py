"""
Pydantic schemas for Payroll module request/response validation.
"""
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator, condecimal
from uuid import UUID

# Shared schemas
class StatusEnum(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    DRAFT = "DRAFT"
    PROCESSED = "PROCESSED"
    CANCELLED = "CANCELLED"

class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints."""
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(100, ge=1, le=1000, description="Number of records to return")

class PaginatedResponse(BaseModel):
    """Generic paginated response schema."""
    items: List[Any]
    total: int
    page: int
    pages: int
    size: int

# Timesheet schemas
class TimesheetStatus(str, Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PROCESSED = "PROCESSED"

class TimesheetBase(BaseModel):
    employee_id: UUID
    start_date: date
    end_date: date
    notes: Optional[str] = None

class TimesheetCreate(TimesheetBase):
    pass

class TimesheetUpdate(BaseModel):
    status: Optional[TimesheetStatus] = None
    notes: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None

class TimesheetEntryBase(BaseModel):
    entry_date: date
    project_id: Optional[UUID] = None
    task_id: Optional[UUID] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_minutes: int = Field(0, ge=0)
    regular_hours: Decimal = Field(0, ge=0, decimal_places=2)
    overtime_hours: Decimal = Field(0, ge=0, decimal_places=2)
    double_overtime_hours: Decimal = Field(0, ge=0, decimal_places=2)
    vacation_hours: Decimal = Field(0, ge=0, decimal_places=2)
    sick_hours: Decimal = Field(0, ge=0, decimal_places=2)
    holiday_hours: Decimal = Field(0, ge=0, decimal_places=2)
    other_hours: Decimal = Field(0, ge=0, decimal_places=2)
    is_billable: bool = True
    notes: Optional[str] = None

class TimesheetEntryCreate(TimesheetEntryBase):
    timesheet_id: UUID

class TimesheetEntryUpdate(BaseModel):
    duration_minutes: Optional[int] = Field(None, ge=0)
    regular_hours: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    overtime_hours: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    double_overtime_hours: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    vacation_hours: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    sick_hours: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    holiday_hours: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    other_hours: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    is_billable: Optional[bool] = None
    notes: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None

class TimesheetEntryResponse(TimesheetEntryBase):
    id: UUID
    timesheet_id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    custom_fields: Dict[str, Any]

    class Config:
        orm_mode = True

class TimesheetResponse(TimesheetBase):
    id: UUID
    timesheet_number: str
    status: TimesheetStatus
    regular_hours: Decimal
    overtime_hours: Decimal
    double_overtime_hours: Decimal
    vacation_hours: Decimal
    sick_hours: Decimal
    holiday_hours: Decimal
    other_hours: Decimal
    submitted_at: Optional[datetime]
    approved_at: Optional[datetime]
    approved_by_id: Optional[UUID]
    rejected_at: Optional[datetime]
    rejected_reason: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    custom_fields: Dict[str, Any]
    entries: List[TimesheetEntryResponse] = []
    
    class Config:
        orm_mode = True

# Payroll Entry schemas
class PayrollEntryBase(BaseModel):
    employee_id: UUID
    pay_period_start: date
    pay_period_end: date
    pay_date: date
    payment_method: str
    notes: Optional[str] = None

class PayrollEntryCreate(PayrollEntryBase):
    pass

class PayrollEntryUpdate(BaseModel):
    status: Optional[StatusEnum] = None
    notes: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None

class PayrollEntryResponse(PayrollEntryBase):
    id: UUID
    payroll_number: str
    status: StatusEnum
    gross_pay: Decimal
    total_deductions: Decimal
    net_pay: Decimal
    created_at: datetime
    updated_at: Optional[datetime]
    custom_fields: Dict[str, Any]
    
    class Config:
        orm_mode = True

# Earning schemas
class EarningBase(BaseModel):
    earning_code_id: UUID
    rate: Decimal = Field(..., gt=0, decimal_places=4)
    quantity: Decimal = Field(1, gt=0, decimal_places=4)
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    is_taxable: bool = True
    is_pretax: bool = False
    description: Optional[str] = None

class EarningCreate(EarningBase):
    payroll_entry_id: UUID

class EarningUpdate(BaseModel):
    rate: Optional[Decimal] = Field(None, gt=0, decimal_places=4)
    quantity: Optional[Decimal] = Field(None, gt=0, decimal_places=4)
    amount: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    is_taxable: Optional[bool] = None
    is_pretax: Optional[bool] = None
    description: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None

class EarningResponse(EarningBase):
    id: UUID
    payroll_entry_id: UUID
    gl_account_id: Optional[UUID]
    created_at: datetime
    updated_at: Optional[datetime]
    custom_fields: Dict[str, Any]
    
    class Config:
        orm_mode = True

# Deduction schemas
class DeductionBase(BaseModel):
    deduction_code_id: UUID
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    rate: Optional[Decimal] = Field(None, ge=0, le=100, decimal_places=4)
    is_pretax: bool = False
    affects_taxable_income: bool = True
    description: Optional[str] = None

class DeductionCreate(DeductionBase):
    payroll_entry_id: UUID

class DeductionUpdate(BaseModel):
    amount: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    rate: Optional[Decimal] = Field(None, ge=0, le=100, decimal_places=4)
    is_pretax: Optional[bool] = None
    affects_taxable_income: Optional[bool] = None
    description: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None

class DeductionResponse(DeductionBase):
    id: UUID
    payroll_entry_id: UUID
    gl_account_id: Optional[UUID]
    created_at: datetime
    updated_at: Optional[datetime]
    custom_fields: Dict[str, Any]
    
    class Config:
        orm_mode = True

# Tax schemas
class TaxBase(BaseModel):
    tax_code_id: UUID
    taxable_amount: Decimal = Field(..., ge=0, decimal_places=2)
    tax_amount: Decimal = Field(..., ge=0, decimal_places=2)
    employer_tax_amount: Decimal = Field(0, ge=0, decimal_places=2)
    description: Optional[str] = None

class TaxCreate(TaxBase):
    payroll_entry_id: UUID

class TaxUpdate(BaseModel):
    taxable_amount: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    tax_amount: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    employer_tax_amount: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    description: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None

class TaxResponse(TaxBase):
    id: UUID
    payroll_entry_id: UUID
    employee_liability_account_id: Optional[UUID]
    employer_liability_account_id: Optional[UUID]
    created_at: datetime
    updated_at: Optional[datetime]
    custom_fields: Dict[str, Any]
    
    class Config:
        orm_mode = True

# Benefit schemas
class BenefitBase(BaseModel):
    benefit_plan_id: UUID
    employee_contribution: Decimal = Field(..., ge=0, decimal_places=2)
    employer_contribution: Decimal = Field(..., ge=0, decimal_places=2)
    description: Optional[str] = None

class BenefitCreate(BenefitBase):
    payroll_entry_id: UUID

class BenefitUpdate(BaseModel):
    employee_contribution: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    employer_contribution: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    description: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None

class BenefitResponse(BenefitBase):
    id: UUID
    payroll_entry_id: UUID
    employee_contra_account_id: Optional[UUID]
    employer_contra_account_id: Optional[UUID]
    created_at: datetime
    updated_at: Optional[datetime]
    custom_fields: Dict[str, Any]
    
    class Config:
        orm_mode = True

# Bank Account schemas
class BankAccountType(str, Enum):
    CHECKING = "CHECKING"
    SAVINGS = "SAVINGS"
    CURRENT = "CURRENT"
    LOAN = "LOAN"
    CREDIT_CARD = "CREDIT_CARD"
    OTHER = "OTHER"

class BankAccountBase(BaseModel):
    account_holder_name: str
    bank_name: str
    branch_name: Optional[str] = None
    account_number: str
    account_type: BankAccountType
    routing_number: Optional[str] = None
    iban: Optional[str] = None
    swift_code: Optional[str] = None
    is_active: bool = True
    is_primary: bool = False
    is_verified: bool = False

class BankAccountCreate(BankAccountBase):
    employee_id: UUID

class BankAccountUpdate(BaseModel):
    account_holder_name: Optional[str] = None
    bank_name: Optional[str] = None
    branch_name: Optional[str] = None
    account_type: Optional[BankAccountType] = None
    routing_number: Optional[str] = None
    iban: Optional[str] = None
    swift_code: Optional[str] = None
    is_active: Optional[bool] = None
    is_primary: Optional[bool] = None
    custom_fields: Optional[Dict[str, Any]] = None

class BankAccountResponse(BankAccountBase):
    id: UUID
    employee_id: UUID
    verified_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    custom_fields: Dict[str, Any]
    
    class Config:
        orm_mode = True

# Payroll Entry Detail Response
class PayrollEntryDetailResponse(PayrollEntryResponse):
    earnings: List[EarningResponse] = []
    deductions: List[DeductionResponse] = []
    taxes: List[TaxResponse] = []
    benefits: List[BenefitResponse] = []
    
    class Config:
        orm_mode = True
