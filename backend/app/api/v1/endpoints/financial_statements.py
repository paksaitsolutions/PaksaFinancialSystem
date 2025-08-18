"""
Financial Statements API Endpoints
"""
from datetime import date
from typing import Optional, List, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.modules.core_financials.accounting.services.financial_statement_service import FinancialStatementService
from app.modules.core_financials.accounting.models.gl_period import GLPeriod
from app.core.security import get_current_active_user
from app.models.user import User

router = APIRouter()


class FinancialStatementRequest(BaseModel):
    """Request model for generating financial statements"""
    start_date: date = Field(..., description="Start date of the reporting period")
    end_date: date = Field(..., description="End date of the reporting period")
    currency: str = Field("USD", description="Reporting currency code")
    include_comparative: bool = Field(False, description="Include prior period comparison")
    include_notes: bool = Field(True, description="Include notes and disclosures")
    format_currency: bool = Field(True, description="Format numbers as currency strings")
    template_id: Optional[UUID] = Field(None, description="ID of a custom template to use")


@router.get("/balance-sheet")
async def get_balance_sheet(
    as_of_date: date,
    currency: str = "USD",
    include_comparative: bool = False,
    include_notes: bool = True,
    format_currency: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Generate a balance sheet as of a specific date
    """
    try:
        service = FinancialStatementService(db)
        return service.generate_balance_sheet(
            as_of_date=as_of_date,
            currency=currency,
            include_comparative=include_comparative,
            include_notes=include_notes,
            format_currency=format_currency
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/income-statement")
async def get_income_statement(
    start_date: date,
    end_date: date,
    currency: str = "USD",
    include_comparative: bool = False,
    include_notes: bool = True,
    format_currency: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Generate an income statement for a date range
    """
    try:
        service = FinancialStatementService(db)
        return service.generate_income_statement(
            start_date=start_date,
            end_date=end_date,
            currency=currency,
            include_comparative=include_comparative,
            include_notes=include_notes,
            format_currency=format_currency
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/cash-flow-statement")
async def get_cash_flow_statement(
    start_date: date,
    end_date: date,
    currency: str = "USD",
    include_comparative: bool = False,
    include_notes: bool = True,
    format_currency: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Generate a cash flow statement for a date range
    """
    try:
        service = FinancialStatementService(db)
        return service.generate_cash_flow_statement(
            start_date=start_date,
            end_date=end_date,
            currency=currency,
            include_comparative=include_comparative,
            include_notes=include_notes,
            format_currency=format_currency
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/trial-balance")
async def get_trial_balance(
    as_of_date: date,
    currency: str = "USD",
    include_zero_balances: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Generate a trial balance as of a specific date
    """
    try:
        service = FinancialStatementService(db)
        return service.generate_trial_balance(
            as_of_date=as_of_date,
            currency=currency,
            include_zero_balances=include_zero_balances
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
