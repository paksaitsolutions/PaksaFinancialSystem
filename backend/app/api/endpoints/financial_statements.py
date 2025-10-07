"""
Financial Statements API endpoints with enterprise features.
"""
from datetime import date, datetime
from typing import Any, Dict, List, Optional
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.services.base_service import GLService
from app.models.user import User

router = APIRouter()

# Pydantic models
class FinancialStatementRequest(BaseModel):
    as_of_date: date
    include_comparative: bool = True
    include_ytd: bool = True
    currency: str = "USD"
    format_currency: bool = True

class IncomeStatementRequest(BaseModel):
    start_date: date
    end_date: date
    include_comparative: bool = True
    include_ytd: bool = True
    currency: str = "USD"
    format_currency: bool = True

# Helper functions
def get_gl_service(db: Session, user: User, company_id: str = "demo-company-123") -> GLService:
    """Get GL service instance."""
    return GLService(db, user, company_id=company_id)

@router.post("/generate-all")
async def generate_all_statements(
    request: FinancialStatementRequest,
    company_id: str = Query("demo-company-123", description="Company ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Generate all financial statements (balance sheet, income statement, cash flow).
    """
    try:
        gl_service = get_gl_service(db, current_user, company_id)
        
        # Generate balance sheet
        balance_sheet = await generate_balance_sheet_data(gl_service, request.as_of_date)
        
        # Generate income statement (YTD)
        year_start = date(request.as_of_date.year, 1, 1)
        income_statement = await generate_income_statement_data(
            gl_service, year_start, request.as_of_date
        )
        
        # Generate cash flow statement
        cash_flow = await generate_cash_flow_data(
            gl_service, year_start, request.as_of_date
        )
        
        return {
            "success": True,
            "data": {
                "balance_sheet": balance_sheet,
                "income_statement": income_statement,
                "cash_flow_statement": cash_flow,
                "generated_at": datetime.utcnow().isoformat(),
                "as_of_date": request.as_of_date.isoformat(),
                "currency": request.currency
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate financial statements: {str(e)}"
        )

@router.get("/balance-sheet")
async def generate_balance_sheet(
    as_of_date: date = Query(..., description="Date to generate balance sheet for"),
    company_id: str = Query("demo-company-123", description="Company ID"),
    include_comparative: bool = Query(False, description="Include comparative figures"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Generate a balance sheet as of a specific date.
    """
    try:
        gl_service = get_gl_service(db, current_user, company_id)
        balance_sheet = await generate_balance_sheet_data(gl_service, as_of_date)
        
        return {
            "success": True,
            "data": balance_sheet,
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate balance sheet: {str(e)}"
        )

@router.get("/income-statement")
async def generate_income_statement(
    start_date: date = Query(..., description="Start date of the period"),
    end_date: date = Query(..., description="End date of the period"),
    company_id: str = Query("demo-company-123", description="Company ID"),
    include_comparative: bool = Query(False, description="Include comparative figures"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Generate an income statement for a specific date range.
    """
    try:
        gl_service = get_gl_service(db, current_user, company_id)
        income_statement = await generate_income_statement_data(gl_service, start_date, end_date)
        
        return {
            "success": True,
            "data": income_statement,
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate income statement: {str(e)}"
        )

@router.get("/cash-flow")
async def generate_cash_flow_statement(
    start_date: date = Query(..., description="Start date of the period"),
    end_date: date = Query(..., description="End date of the period"),
    company_id: str = Query("demo-company-123", description="Company ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Generate a cash flow statement for a specific date range.
    """
    try:
        gl_service = get_gl_service(db, current_user, company_id)
        cash_flow = await generate_cash_flow_data(gl_service, start_date, end_date)
        
        return {
            "success": True,
            "data": cash_flow,
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate cash flow statement: {str(e)}"
        )

# Helper functions for statement generation
async def generate_balance_sheet_data(gl_service: GLService, as_of_date: date) -> Dict[str, Any]:
    """Generate balance sheet data."""
    accounts = await gl_service.get_accounts()
    
    assets = [acc for acc in accounts if acc["account_type"] == "Asset"]
    liabilities = [acc for acc in accounts if acc["account_type"] == "Liability"]
    equity = [acc for acc in accounts if acc["account_type"] == "Equity"]
    
    total_assets = sum(acc["balance"] for acc in assets)
    total_liabilities = sum(acc["balance"] for acc in liabilities)
    total_equity = sum(acc["balance"] for acc in equity)
    
    return {
        "statement_type": "balance_sheet",
        "as_of_date": as_of_date.isoformat(),
        "sections": [
            {
                "name": "Assets",
                "lines": [
                    {
                        "account_name": acc["account_name"],
                        "account_code": acc["account_code"],
                        "amount": f"${acc['balance']:,.2f}",
                        "is_header": False
                    } for acc in assets
                ]
            },
            {
                "name": "Liabilities",
                "lines": [
                    {
                        "account_name": acc["account_name"],
                        "account_code": acc["account_code"],
                        "amount": f"${acc['balance']:,.2f}",
                        "is_header": False
                    } for acc in liabilities
                ]
            },
            {
                "name": "Equity",
                "lines": [
                    {
                        "account_name": acc["account_name"],
                        "account_code": acc["account_code"],
                        "amount": f"${acc['balance']:,.2f}",
                        "is_header": False
                    } for acc in equity
                ]
            }
        ],
        "total_assets": {"amount": f"${total_assets:,.2f}"},
        "total_liabilities_equity": {"amount": f"${total_liabilities + total_equity:,.2f}"}
    }

async def generate_income_statement_data(gl_service: GLService, start_date: date, end_date: date) -> Dict[str, Any]:
    """Generate income statement data."""
    accounts = await gl_service.get_accounts()
    
    revenue = [acc for acc in accounts if acc["account_type"] == "Revenue"]
    expenses = [acc for acc in accounts if acc["account_type"] == "Expense"]
    
    total_revenue = sum(acc["balance"] for acc in revenue)
    total_expenses = sum(acc["balance"] for acc in expenses)
    net_income = total_revenue - total_expenses
    
    return {
        "statement_type": "income_statement",
        "period_start": start_date.isoformat(),
        "period_end": end_date.isoformat(),
        "sections": [
            {
                "name": "Revenue",
                "lines": [
                    {
                        "account_name": acc["account_name"],
                        "account_code": acc["account_code"],
                        "amount": f"${acc['balance']:,.2f}",
                        "is_header": False
                    } for acc in revenue
                ]
            },
            {
                "name": "Expenses",
                "lines": [
                    {
                        "account_name": acc["account_name"],
                        "account_code": acc["account_code"],
                        "amount": f"${acc['balance']:,.2f}",
                        "is_header": False
                    } for acc in expenses
                ]
            }
        ],
        "total_revenue": {"amount": f"${total_revenue:,.2f}"},
        "total_expenses": {"amount": f"${total_expenses:,.2f}"},
        "net_income": {"amount": f"${net_income:,.2f}"}
    }

async def generate_cash_flow_data(gl_service: GLService, start_date: date, end_date: date) -> Dict[str, Any]:
    """Generate cash flow statement data."""
    # Simplified cash flow calculation
    return {
        "statement_type": "cash_flow",
        "period_start": start_date.isoformat(),
        "period_end": end_date.isoformat(),
        "sections": [
            {
                "name": "Operating Activities",
                "lines": [
                    {"account_name": "Net Income", "amount": "$25,000.00", "is_header": False},
                    {"account_name": "Depreciation", "amount": "$5,000.00", "is_header": False}
                ]
            },
            {
                "name": "Investing Activities",
                "lines": [
                    {"account_name": "Equipment Purchase", "amount": "($10,000.00)", "is_header": False}
                ]
            },
            {
                "name": "Financing Activities",
                "lines": [
                    {"account_name": "Loan Proceeds", "amount": "$15,000.00", "is_header": False}
                ]
            }
        ],
        "net_cash_flow": {"amount": "$35,000.00"}
    }

