"""
Payroll processing schemas for the Payroll module.
"""
from datetime import date
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field
from decimal import Decimal
from enum import Enum


class PayrollStatusEnum(str, Enum):
    DRAFT = "DRAFT"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    APPROVED = "APPROVED"
    PAID = "PAID"
    CANCELLED = "CANCELLED"


class PayrollRunCreate(BaseModel):
    """Schema for creating a payroll run."""
    pay_period_start: date
    pay_period_end: date
    pay_date: date
    description: Optional[str] = None
    department: Optional[str] = None


class PayrollRunUpdate(BaseModel):
    """Schema for updating a payroll run."""
    pay_date: Optional[date] = None
    description: Optional[str] = None
    status: Optional[PayrollStatusEnum] = None


class PayrollRunResponse(BaseModel):
    """Schema for payroll run response."""
    id: UUID
    pay_period_start: date
    pay_period_end: date
    pay_date: date
    description: Optional[str]
    department: Optional[str]
    status: PayrollStatusEnum
    total_gross_pay: Decimal
    total_net_pay: Decimal
    total_deductions: Decimal
    employee_count: int
    created_at: date
    updated_at: date

    class Config:
        orm_mode = True


class PayslipCreate(BaseModel):
    """Schema for creating a payslip."""
    employee_id: UUID
    payroll_run_id: UUID
    gross_pay: Decimal = Field(..., gt=0)
    basic_salary: Decimal = Field(..., ge=0)
    overtime_pay: Decimal = Field(0, ge=0)
    bonus: Decimal = Field(0, ge=0)
    allowances: Decimal = Field(0, ge=0)
    deductions: Decimal = Field(0, ge=0)
    tax_deductions: Decimal = Field(0, ge=0)
    net_pay: Decimal = Field(..., gt=0)


class PayslipResponse(BaseModel):
    """Schema for payslip response."""
    id: UUID
    employee_id: UUID
    employee_name: str
    employee_code: str
    payroll_run_id: UUID
    gross_pay: Decimal
    basic_salary: Decimal
    overtime_pay: Decimal
    bonus: Decimal
    allowances: Decimal
    deductions: Decimal
    tax_deductions: Decimal
    net_pay: Decimal
    pay_period_start: date
    pay_period_end: date
    pay_date: date
    created_at: date

    class Config:
        orm_mode = True


class PayrollCalculationRequest(BaseModel):
    """Schema for payroll calculation request."""
    employee_ids: List[UUID]
    pay_period_start: date
    pay_period_end: date
    include_overtime: bool = True
    include_bonus: bool = True


class PayrollSummary(BaseModel):
    """Schema for payroll summary."""
    total_employees: int
    total_gross_pay: Decimal
    total_net_pay: Decimal
    total_deductions: Decimal
    total_tax_deductions: Decimal
    average_gross_pay: Decimal
    average_net_pay: Decimal