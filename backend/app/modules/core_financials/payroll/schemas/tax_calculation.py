"""
Tax calculation schemas for the Payroll module.
"""
from typing import Optional, List, Dict
from uuid import UUID
from pydantic import BaseModel, Field
from decimal import Decimal
from enum import Enum


class TaxTypeEnum(str, Enum):
    FEDERAL_INCOME = "FEDERAL_INCOME"
    STATE_INCOME = "STATE_INCOME"
    SOCIAL_SECURITY = "SOCIAL_SECURITY"
    MEDICARE = "MEDICARE"
    UNEMPLOYMENT = "UNEMPLOYMENT"
    DISABILITY = "DISABILITY"


class FilingStatusEnum(str, Enum):
    SINGLE = "SINGLE"
    MARRIED_JOINT = "MARRIED_JOINT"
    MARRIED_SEPARATE = "MARRIED_SEPARATE"
    HEAD_OF_HOUSEHOLD = "HEAD_OF_HOUSEHOLD"


class TaxBracket(BaseModel):
    """Tax bracket definition."""
    min_income: Decimal
    max_income: Optional[Decimal]
    rate: Decimal
    base_tax: Decimal = Decimal("0.00")


class TaxRule(BaseModel):
    """Tax rule configuration."""
    id: Optional[UUID] = None
    tax_type: TaxTypeEnum
    filing_status: Optional[FilingStatusEnum] = None
    state: Optional[str] = None
    year: int
    brackets: List[TaxBracket]
    standard_deduction: Decimal = Decimal("0.00")
    exemption_amount: Decimal = Decimal("0.00")
    is_active: bool = True


class TaxCalculationRequest(BaseModel):
    """Request for tax calculation."""
    employee_id: UUID
    gross_pay: Decimal = Field(..., gt=0)
    pay_period: str  # "weekly", "bi_weekly", "monthly", "annual"
    filing_status: FilingStatusEnum = FilingStatusEnum.SINGLE
    allowances: int = Field(0, ge=0)
    additional_withholding: Decimal = Field(Decimal("0.00"), ge=0)
    state: Optional[str] = None
    year: int = Field(2024, ge=2020, le=2030)


class TaxCalculationResult(BaseModel):
    """Result of tax calculation."""
    employee_id: UUID
    gross_pay: Decimal
    federal_income_tax: Decimal
    state_income_tax: Decimal
    social_security_tax: Decimal
    medicare_tax: Decimal
    unemployment_tax: Decimal
    disability_tax: Decimal
    total_tax: Decimal
    net_pay: Decimal
    effective_tax_rate: Decimal
    marginal_tax_rate: Decimal


class TaxSummary(BaseModel):
    """Tax summary for reporting."""
    total_gross_pay: Decimal
    total_federal_tax: Decimal
    total_state_tax: Decimal
    total_social_security: Decimal
    total_medicare: Decimal
    total_unemployment: Decimal
    total_disability: Decimal
    total_taxes: Decimal
    total_net_pay: Decimal
    employee_count: int