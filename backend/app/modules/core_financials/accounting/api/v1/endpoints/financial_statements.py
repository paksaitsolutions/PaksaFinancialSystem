from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.modules.core_financials.accounting.models.account import Account, AccountType
from app.modules.core_financials.accounting.models.journal_entry import JournalEntry, JournalEntryStatus, JournalEntryLine
from app.modules.core_financials.accounting.schemas.financial_statement import (
    FinancialStatementType,
    FinancialStatementResponse,
    FinancialStatementSection,
    FinancialStatementLineItem,
    BalanceSheetResponse,
    IncomeStatementResponse,
    CashFlowStatementResponse,
    FinancialStatementPeriod
)
from app.modules.core_financials.accounting.services.financial_statement_service import FinancialStatementService
from app.modules.core_financials.accounting.services.period_service import PeriodService

router = APIRouter()

@router.get("/balance-sheet", response_model=BalanceSheetResponse)
async def get_balance_sheet(
    as_of_date: date = Query(..., description="The date to generate the balance sheet for"),
    include_comparative: bool = Query(False, description="Include comparative figures from the previous period"),
    format_currency: bool = Query(True, description="Format amounts as currency strings"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Generate a balance sheet as of a specific date.
    
    The balance sheet provides a snapshot of the company's financial position at a specific point in time,
    showing assets, liabilities, and equity.
    """
    try:
        period_service = PeriodService(db)
        service = FinancialStatementService(db, period_service)
        
        # Get the balance sheet data
        balance_sheet = service.generate_balance_sheet(
            as_of_date=as_of_date,
            include_comparative=include_comparative,
            format_currency=format_currency
        )
        
        return balance_sheet
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/income-statement", response_model=IncomeStatementResponse)
async def get_income_statement(
    start_date: date = Query(..., description="Start date of the period"),
    end_date: date = Query(..., description="End date of the period"),
    include_comparative: bool = Query(False, description="Include comparative figures from the previous period"),
    format_currency: bool = Query(True, description="Format amounts as currency strings"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Generate an income statement for a specified date range.
    
    The income statement shows the company's revenues, expenses, and profits over a period of time.
    """
    try:
        period_service = PeriodService(db)
        service = FinancialStatementService(db, period_service)
        
        # Get the income statement data
        income_statement = service.generate_income_statement(
            start_date=start_date,
            end_date=end_date,
            include_comparative=include_comparative,
            format_currency=format_currency
        )
        
        return income_statement
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cash-flow-statement", response_model=CashFlowStatementResponse)
async def get_cash_flow_statement(
    start_date: date = Query(..., description="Start date of the period"),
    end_date: date = Query(..., description="End date of the period"),
    include_comparative: bool = Query(False, description="Include comparative figures from the previous period"),
    format_currency: bool = Query(True, description="Format amounts as currency strings"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Generate a cash flow statement for a specified date range.
    
    The cash flow statement shows how changes in balance sheet accounts and income affect cash and cash equivalents,
    breaking the analysis down to operating, investing, and financing activities.
    """
    try:
        period_service = PeriodService(db)
        service = FinancialStatementService(db, period_service)
        
        # Get the cash flow statement data
        cash_flow_statement = service.generate_cash_flow_statement(
            start_date=start_date,
            end_date=end_date,
            include_comparative=include_comparative,
            format_currency=format_currency
        )
        
        return cash_flow_statement
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
