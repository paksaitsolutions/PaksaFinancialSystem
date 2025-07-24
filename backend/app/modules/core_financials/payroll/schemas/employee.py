"""
Employee schemas for the Payroll module.
"""
from datetime import date
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, validator
from enum import Enum


class GenderEnum(str, Enum):
    MALE = "M"
    FEMALE = "F"
    OTHER = "O"


class MaritalStatusEnum(str, Enum):
    SINGLE = "SINGLE"
    MARRIED = "MARRIED"
    DIVORCED = "DIVORCED"
    WIDOWED = "WIDOWED"


class EmploymentTypeEnum(str, Enum):
    FULL_TIME = "FULL_TIME"
    PART_TIME = "PART_TIME"
    CONTRACT = "CONTRACT"
    TEMPORARY = "TEMPORARY"
    INTERN = "INTERN"


class PaymentMethodEnum(str, Enum):
    BANK_TRANSFER = "BANK_TRANSFER"
    CHECK = "CHECK"
    CASH = "CASH"
    OTHER = "OTHER"


class PaymentFrequencyEnum(str, Enum):
    WEEKLY = "WEEKLY"
    BI_WEEKLY = "BI_WEEKLY"
    SEMI_MONTHLY = "SEMI_MONTHLY"
    MONTHLY = "MONTHLY"


class EmployeeBase(BaseModel):
    """Base schema for Employee data."""
    employee_id: str = Field(..., min_length=1, max_length=50)
    first_name: str = Field(..., min_length=1, max_length=100)
    middle_name: Optional[str] = Field(None, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    date_of_birth: date
    gender: GenderEnum
    marital_status: MaritalStatusEnum
    national_id: Optional[str] = Field(None, max_length=50)
    social_security_number: Optional[str] = Field(None, max_length=50)
    tax_identification_number: Optional[str] = Field(None, max_length=50)
    
    # Contact Information
    email: EmailStr
    phone_number: str = Field(..., min_length=5, max_length=50)
    address_line1: str = Field(..., min_length=1, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=1, max_length=100)
    postal_code: str = Field(..., min_length=1, max_length=20)
    country: str = Field(..., min_length=1, max_length=100)
    
    # Employment Details
    hire_date: date
    termination_date: Optional[date] = None
    employment_type: EmploymentTypeEnum
    job_title: str = Field(..., min_length=1, max_length=100)
    department: str = Field(..., min_length=1, max_length=100)
    manager_id: Optional[UUID] = None
    is_active: bool = True
    
    # Bank Details
    bank_name: Optional[str] = Field(None, max_length=100)
    bank_branch: Optional[str] = Field(None, max_length=100)
    account_number: Optional[str] = Field(None, max_length=50)
    account_type: Optional[str] = Field(None, max_length=50)
    
    # Compensation
    base_salary: float = Field(..., gt=0)
    currency: str = Field("USD", min_length=3, max_length=3)
    payment_method: PaymentMethodEnum
    payment_frequency: PaymentFrequencyEnum
    
    @validator('hire_date')
    def validate_hire_date(cls, v):
        if v > date.today():
            raise ValueError('Hire date cannot be in the future')
        return v
    
    @validator('termination_date')
    def validate_termination_date(cls, v, values):
        if v and 'hire_date' in values and v < values['hire_date']:
            raise ValueError('Termination date cannot be before hire date')
        return v


class EmployeeCreate(EmployeeBase):
    """Schema for creating a new employee."""
    pass


class EmployeeUpdate(BaseModel):
    """Schema for updating an employee."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    middle_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    date_of_birth: Optional[date] = None
    gender: Optional[GenderEnum] = None
    marital_status: Optional[MaritalStatusEnum] = None
    national_id: Optional[str] = Field(None, max_length=50)
    social_security_number: Optional[str] = Field(None, max_length=50)
    tax_identification_number: Optional[str] = Field(None, max_length=50)
    
    # Contact Information
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, min_length=5, max_length=50)
    address_line1: Optional[str] = Field(None, min_length=1, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, min_length=1, max_length=100)
    state: Optional[str] = Field(None, min_length=1, max_length=100)
    postal_code: Optional[str] = Field(None, min_length=1, max_length=20)
    country: Optional[str] = Field(None, min_length=1, max_length=100)
    
    # Employment Details
    hire_date: Optional[date] = None
    termination_date: Optional[date] = None
    employment_type: Optional[EmploymentTypeEnum] = None
    job_title: Optional[str] = Field(None, min_length=1, max_length=100)
    department: Optional[str] = Field(None, min_length=1, max_length=100)
    manager_id: Optional[UUID] = None
    is_active: Optional[bool] = None
    
    # Bank Details
    bank_name: Optional[str] = Field(None, max_length=100)
    bank_branch: Optional[str] = Field(None, max_length=100)
    account_number: Optional[str] = Field(None, max_length=50)
    account_type: Optional[str] = Field(None, max_length=50)
    
    # Compensation
    base_salary: Optional[float] = Field(None, gt=0)
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    payment_method: Optional[PaymentMethodEnum] = None
    payment_frequency: Optional[PaymentFrequencyEnum] = None


class EmployeeInDB(EmployeeBase):
    """Schema for employee data from the database."""
    id: UUID
    created_at: date
    updated_at: date

    class Config:
        orm_mode = True


class Employee(EmployeeInDB):
    """Schema for employee response."""
    full_name: str
    is_currently_employed: bool


class EmployeeList(BaseModel):
    """Schema for a list of employees."""
    items: List[Employee]
    total: int