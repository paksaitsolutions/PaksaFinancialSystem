"""
Employee schemas for HRM module
"""
from datetime import date, datetime
from typing import Optional
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, EmailStr, validator

class EmployeeBase(BaseModel):
    employee_id: str
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    job_title: str
    department: Optional[str] = None
    hire_date: date
    base_salary: Decimal
    is_active: bool = True

class EmployeeCreate(EmployeeBase):
    middle_name: Optional[str] = None
    date_of_birth: date
    gender: str
    marital_status: str
    national_id: Optional[str] = None
    address_line1: str
    city: str
    state: str
    postal_code: str
    country: str
    employment_type: str
    payment_method: str
    payment_frequency: str
    
    @validator('gender')
    def validate_gender(cls, v):
        if v not in ['M', 'F', 'O']:
            raise ValueError('Gender must be M, F, or O')
        return v
    
    @validator('employment_type')
    def validate_employment_type(cls, v):
        valid_types = ['FULL_TIME', 'PART_TIME', 'CONTRACT', 'TEMPORARY', 'INTERN']
        if v not in valid_types:
            raise ValueError(f'Employment type must be one of {valid_types}')
        return v

class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    job_title: Optional[str] = None
    department: Optional[str] = None
    base_salary: Optional[Decimal] = None
    is_active: Optional[bool] = None

class EmployeeInDB(EmployeeBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class Employee(EmployeeInDB):
    pass