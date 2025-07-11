"""
Payroll Pydantic schemas for API validation.
"""
from datetime import date
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr
from app.schemas.base import BaseSchema, BaseCreateSchema, BaseUpdateSchema, AuditResponseSchema

class EmployeeCreate(BaseCreateSchema):
    employee_id: str = Field(..., max_length=20)
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    email: Optional[EmailStr] = None
    department: Optional[str] = Field(None, max_length=50)
    position: Optional[str] = Field(None, max_length=100)
    hire_date: date
    salary: Decimal = Field(..., gt=0)
    pay_frequency: str = Field(default="monthly", max_length=20)

class EmployeeUpdate(BaseUpdateSchema):
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = None
    department: Optional[str] = Field(None, max_length=50)
    position: Optional[str] = Field(None, max_length=100)
    salary: Optional[Decimal] = Field(None, gt=0)
    pay_frequency: Optional[str] = Field(None, max_length=20)

class EmployeeResponse(AuditResponseSchema):
    employee_id: str
    first_name: str
    last_name: str
    email: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    hire_date: date
    salary: Decimal
    pay_frequency: str

class PayrollDeductionCreate(BaseSchema):
    deduction_type: str = Field(..., max_length=50)
    amount: Decimal = Field(..., gt=0)
    description: Optional[str] = None

class PayrollRecordCreate(BaseCreateSchema):
    employee_id: int
    pay_period_start: date
    pay_period_end: date
    pay_date: date
    gross_pay: Decimal = Field(..., gt=0)
    deductions: List[PayrollDeductionCreate] = []

class PayrollDeductionResponse(BaseSchema):
    id: int
    deduction_type: str
    amount: Decimal
    description: Optional[str] = None

class PayrollRecordResponse(AuditResponseSchema):
    employee_id: int
    pay_period_start: date
    pay_period_end: date
    pay_date: date
    gross_pay: Decimal
    total_deductions: Decimal
    net_pay: Decimal
    status: str
    deductions: List[PayrollDeductionResponse]