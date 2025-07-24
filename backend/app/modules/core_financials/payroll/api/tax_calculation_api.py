"""
Tax calculation API endpoints for the Payroll module.
"""
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.db.session import get_db
from app.modules.core_financials.payroll.schemas.tax_calculation import (
    TaxCalculationRequest, TaxCalculationResult, TaxSummary
)
from app.modules.core_financials.payroll.services.tax_calculation_service import TaxCalculationService

router = APIRouter(prefix="/tax-calculation", tags=["tax-calculation"])


@router.post("/calculate", response_model=TaxCalculationResult)
def calculate_employee_taxes(
    request: TaxCalculationRequest,
    db: Session = Depends(get_db)
):
    """Calculate taxes for a single employee."""
    return TaxCalculationService.calculate_taxes(request)


@router.post("/calculate-batch", response_model=List[TaxCalculationResult])
def calculate_batch_taxes(
    requests: List[TaxCalculationRequest],
    db: Session = Depends(get_db)
):
    """Calculate taxes for multiple employees."""
    return TaxCalculationService.calculate_batch_taxes(requests)


@router.get("/tax-brackets")
def get_tax_brackets(
    filing_status: str = "SINGLE",
    year: int = 2024
):
    """Get current tax brackets for reference."""
    if filing_status == "MARRIED_JOINT":
        brackets = TaxCalculationService.FEDERAL_TAX_BRACKETS_MARRIED
    else:
        brackets = TaxCalculationService.FEDERAL_TAX_BRACKETS_SINGLE
    
    return {
        "filing_status": filing_status,
        "year": year,
        "brackets": [
            {
                "min_income": str(bracket.min_income),
                "max_income": str(bracket.max_income) if bracket.max_income else None,
                "rate": str(bracket.rate),
                "base_tax": str(bracket.base_tax)
            }
            for bracket in brackets
        ],
        "standard_deduction": str(TaxCalculationService.STANDARD_DEDUCTIONS.get(filing_status, "0")),
        "social_security_rate": str(TaxCalculationService.SOCIAL_SECURITY_RATE),
        "medicare_rate": str(TaxCalculationService.MEDICARE_RATE)
    }


@router.get("/tax-rates")
def get_current_tax_rates():
    """Get current tax rates for reference."""
    return {
        "social_security": {
            "rate": str(TaxCalculationService.SOCIAL_SECURITY_RATE),
            "wage_base": str(TaxCalculationService.SOCIAL_SECURITY_WAGE_BASE)
        },
        "medicare": {
            "rate": str(TaxCalculationService.MEDICARE_RATE),
            "additional_rate": str(TaxCalculationService.MEDICARE_ADDITIONAL_RATE),
            "additional_threshold": str(TaxCalculationService.MEDICARE_ADDITIONAL_THRESHOLD)
        },
        "unemployment": {
            "futa_rate": str(TaxCalculationService.FUTA_RATE),
            "futa_wage_base": str(TaxCalculationService.FUTA_WAGE_BASE)
        }
    }


@router.post("/estimate-annual")
def estimate_annual_taxes(
    gross_pay: float,
    pay_period: str = "bi_weekly",
    filing_status: str = "SINGLE",
    allowances: int = 0,
    state: str = "CA"
):
    """Estimate annual tax liability."""
    from uuid import uuid4
    from decimal import Decimal
    
    request = TaxCalculationRequest(
        employee_id=uuid4(),
        gross_pay=Decimal(str(gross_pay)),
        pay_period=pay_period,
        filing_status=filing_status,
        allowances=allowances,
        state=state,
        year=2024
    )
    
    result = TaxCalculationService.calculate_taxes(request)
    
    # Annualize the results
    period_multiplier = TaxCalculationService._get_period_multiplier(pay_period)
    
    return {
        "annual_gross_pay": str(result.gross_pay * period_multiplier),
        "annual_federal_tax": str(result.federal_income_tax * period_multiplier),
        "annual_state_tax": str(result.state_income_tax * period_multiplier),
        "annual_social_security": str(result.social_security_tax * period_multiplier),
        "annual_medicare": str(result.medicare_tax * period_multiplier),
        "annual_total_tax": str(result.total_tax * period_multiplier),
        "annual_net_pay": str(result.net_pay * period_multiplier),
        "effective_tax_rate": str(result.effective_tax_rate),
        "marginal_tax_rate": str(result.marginal_tax_rate)
    }