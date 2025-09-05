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
from app.services.gl.financial_statement_service import FinancialStatementService
from app.schemas.gl_schemas import FinancialStatementType as FSType
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
    company_id: UUID,
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
        return service.generate_financial_statement(
            statement_type=FSType.BALANCE_SHEET,
            company_id=company_id,
            end_date=as_of_date,
            created_by=current_user.id
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/income-statement")
async def get_income_statement(
    company_id: UUID,
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
        return service.generate_financial_statement(
            statement_type=FSType.INCOME_STATEMENT,
            company_id=company_id,
            start_date=start_date,
            end_date=end_date,
            created_by=current_user.id
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/cash-flow-statement")
async def get_cash_flow_statement(
    company_id: UUID,
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
        return service.generate_financial_statement(
            statement_type=FSType.CASH_FLOW,
            company_id=company_id,
            start_date=start_date,
            end_date=end_date,
            created_by=current_user.id
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/generate-all")
async def generate_all_statements(
    company_id: UUID,
    as_of_date: date,
    include_comparative: bool = False,
    include_ytd: bool = False,
    currency: str = "USD",
    format_currency: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Generate all financial statements (balance sheet, income statement, cash flow)
    """
    try:
        service = FinancialStatementService(db)
        
        # Calculate start date for income statement and cash flow (beginning of fiscal year)
        from datetime import datetime
        current_year = as_of_date.year
        start_date = datetime(current_year, 1, 1).date()
        
        # Generate all statements
        balance_sheet = service.generate_financial_statement(
            statement_type=FSType.BALANCE_SHEET,
            company_id=company_id,
            end_date=as_of_date,
            created_by=current_user.id
        )
        
        income_statement = service.generate_financial_statement(
            statement_type=FSType.INCOME_STATEMENT,
            company_id=company_id,
            start_date=start_date,
            end_date=as_of_date,
            created_by=current_user.id
        )
        
        cash_flow = service.generate_financial_statement(
            statement_type=FSType.CASH_FLOW,
            company_id=company_id,
            start_date=start_date,
            end_date=as_of_date,
            created_by=current_user.id
        )
        
        return {
            "balance_sheet": balance_sheet.statement_data,
            "income_statement": income_statement.statement_data,
            "cash_flow": cash_flow.statement_data,
            "metadata": {
                "company_id": str(company_id),
                "as_of_date": as_of_date.isoformat(),
                "start_date": start_date.isoformat(),
                "currency": currency,
                "include_comparative": include_comparative,
                "include_ytd": include_ytd,
                "generated_at": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/trial-balance")
async def get_trial_balance(
    company_id: UUID,
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
        trial_balance = service._get_trial_balance(company_id, as_of_date)
        return {
            "trial_balance": trial_balance,
            "metadata": {
                "company_id": str(company_id),
                "as_of_date": as_of_date.isoformat(),
                "currency": currency,
                "include_zero_balances": include_zero_balances
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
