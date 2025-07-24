"""
Benefits management schemas for the Payroll module.
"""
from datetime import date
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field
from decimal import Decimal
from enum import Enum


class BenefitTypeEnum(str, Enum):
    HEALTH_INSURANCE = "HEALTH_INSURANCE"
    DENTAL_INSURANCE = "DENTAL_INSURANCE"
    VISION_INSURANCE = "VISION_INSURANCE"
    LIFE_INSURANCE = "LIFE_INSURANCE"
    RETIREMENT_401K = "RETIREMENT_401K"
    HSA = "HSA"
    FSA = "FSA"
    PARKING = "PARKING"
    TRANSIT = "TRANSIT"
    OTHER = "OTHER"


class DeductionTypeEnum(str, Enum):
    PRE_TAX = "PRE_TAX"
    POST_TAX = "POST_TAX"
    EMPLOYER_PAID = "EMPLOYER_PAID"


class BenefitPlanCreate(BaseModel):
    """Schema for creating a benefit plan."""
    name: str = Field(..., min_length=1, max_length=100)
    benefit_type: BenefitTypeEnum
    description: Optional[str] = None
    provider: Optional[str] = Field(None, max_length=100)
    employee_cost: Decimal = Field(Decimal("0.00"), ge=0)
    employer_cost: Decimal = Field(Decimal("0.00"), ge=0)
    deduction_type: DeductionTypeEnum
    is_active: bool = True


class BenefitPlanUpdate(BaseModel):
    """Schema for updating a benefit plan."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    provider: Optional[str] = Field(None, max_length=100)
    employee_cost: Optional[Decimal] = Field(None, ge=0)
    employer_cost: Optional[Decimal] = Field(None, ge=0)
    deduction_type: Optional[DeductionTypeEnum] = None
    is_active: Optional[bool] = None


class BenefitPlanResponse(BaseModel):
    """Schema for benefit plan response."""
    id: UUID
    name: str
    benefit_type: BenefitTypeEnum
    description: Optional[str]
    provider: Optional[str]
    employee_cost: Decimal
    employer_cost: Decimal
    deduction_type: DeductionTypeEnum
    is_active: bool
    enrolled_count: int
    created_at: date
    updated_at: date

    class Config:
        orm_mode = True


class EmployeeBenefitEnrollment(BaseModel):
    """Schema for employee benefit enrollment."""
    employee_id: UUID
    benefit_plan_id: UUID
    enrollment_date: date
    effective_date: date
    end_date: Optional[date] = None
    employee_contribution: Decimal = Field(Decimal("0.00"), ge=0)
    employer_contribution: Decimal = Field(Decimal("0.00"), ge=0)
    is_active: bool = True


class EmployeeBenefitResponse(BaseModel):
    """Schema for employee benefit response."""
    id: UUID
    employee_id: UUID
    employee_name: str
    benefit_plan_id: UUID
    benefit_plan_name: str
    benefit_type: BenefitTypeEnum
    enrollment_date: date
    effective_date: date
    end_date: Optional[date]
    employee_contribution: Decimal
    employer_contribution: Decimal
    deduction_type: DeductionTypeEnum
    is_active: bool

    class Config:
        orm_mode = True


class BenefitsSummary(BaseModel):
    """Schema for benefits summary."""
    total_plans: int
    active_plans: int
    total_enrollments: int
    total_employee_cost: Decimal
    total_employer_cost: Decimal
    by_type: dict