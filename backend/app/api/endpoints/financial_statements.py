"""
Financial Statements API endpoints.
"""
from datetime import date
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import deps
from app.core.db.session import get_db
from app.services.accounting.financial_statement_generator import FinancialStatementGenerator
from app.services.accounting.financial_statement_service import FinancialStatementService
from app.services.gl.financial_statement_service import FinancialStatementService as GLFinancialStatementService

router = APIRouter()

# Helper functions
def get_financial_statement_service(db: Session = Depends(get_db)) -> FinancialStatementService:
    """Get an instance of the financial statement service."""
    return FinancialStatementService(db)

def get_financial_statement_generator(db: Session = Depends(get_db)) -> FinancialStatementGenerator:
    """Get an instance of the financial statement generator."""
    return FinancialStatementGenerator(db)

def get_gl_financial_statement_service(db: Session = Depends(get_db)) -> GLFinancialStatementService:
    """Get an instance of the GL financial statement service."""
    return GLFinancialStatementService(db)

@router.post(
    "/generate-all",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Generate all financial statements",
    description="Generate balance sheet, income statement, and cash flow statement for a specific date.",
    response_description="Generated financial statements",
    tags=["Financial Statements"]
)
async def generate_all_statements(
    company_id: UUID,
    as_of_date: date = Query(..., description="Date to generate statements for"),
    include_comparative: bool = Query(True, description="Include comparative figures"),
    include_ytd: bool = Query(True, description="Include year-to-date figures"),
    currency: str = Query("USD", description="Reporting currency"),
    format_currency: bool = Query(True, description="Format numbers as currency strings"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Generate all financial statements (balance sheet, income statement, cash flow)
    for a specific date.
    """
    generator = get_financial_statement_generator(db)
    try:
        return generator.generate_all_statements(
            company_id=company_id,
            as_of_date=as_of_date,
            include_comparative=include_comparative,
            include_ytd=include_ytd,
            currency=currency,
            format_currency=format_currency,
            created_by=current_user.id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get(
    "/balance-sheet",
    response_model=Dict[str, Any],
    summary="Generate a balance sheet",
    description="Generate a balance sheet as of a specific date.",
    response_description="Generated balance sheet",
    tags=["Financial Statements"]
)
async def generate_balance_sheet(
    company_id: UUID,
    as_of_date: date = Query(..., description="Date to generate balance sheet for"),
    include_comparative: bool = Query(True, description="Include comparative figures"),
    currency: str = Query("USD", description="Reporting currency"),
    format_currency: bool = Query(True, description="Format numbers as currency strings"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Generate a balance sheet as of a specific date.
    """
    service = get_financial_statement_service(db)
    try:
        return service.generate_balance_sheet(
            as_of_date=as_of_date,
            currency=currency,
            include_comparative=include_comparative,
            format_currency=format_currency
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get(
    "/income-statement",
    response_model=Dict[str, Any],
    summary="Generate an income statement",
    description="Generate an income statement for a specific date range.",
    response_description="Generated income statement",
    tags=["Financial Statements"]
)
async def generate_income_statement(
    company_id: UUID,
    start_date: date = Query(..., description="Start date of the period"),
    end_date: date = Query(..., description="End date of the period"),
    include_comparative: bool = Query(True, description="Include comparative figures"),
    include_ytd: bool = Query(True, description="Include year-to-date figures"),
    currency: str = Query("USD", description="Reporting currency"),
    format_currency: bool = Query(True, description="Format numbers as currency strings"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Generate an income statement for a specific date range.
    """
    service = get_financial_statement_service(db)
    try:
        return service.generate_income_statement(
            start_date=start_date,
            end_date=end_date,
            currency=currency,
            include_comparative=include_comparative,
            include_ytd=include_ytd,
            format_currency=format_currency
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get(
    "/cash-flow",
    response_model=Dict[str, Any],
    summary="Generate a cash flow statement",
    description="Generate a cash flow statement for a specific date range.",
    response_description="Generated cash flow statement",
    tags=["Financial Statements"]
)
async def generate_cash_flow_statement(
    company_id: UUID,
    start_date: date = Query(..., description="Start date of the period"),
    end_date: date = Query(..., description="End date of the period"),
    include_comparative: bool = Query(True, description="Include comparative figures"),
    currency: str = Query("USD", description="Reporting currency"),
    format_currency: bool = Query(True, description="Format numbers as currency strings"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Generate a cash flow statement for a specific date range.
    """
    service = get_financial_statement_service(db)
    try:
        return service.generate_cash_flow_statement(
            start_date=start_date,
            end_date=end_date,
            currency=currency,
            include_comparative=include_comparative,
            format_currency=format_currency
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get(
    "/{statement_id}",
    response_model=schemas.FinancialStatementResponse,
    summary="Get a financial statement by ID",
    description="Get a previously generated financial statement by its ID.",
    response_description="Financial statement",
    tags=["Financial Statements"]
)
async def get_financial_statement(
    statement_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get a previously generated financial statement by its ID.
    """
    service = get_gl_financial_statement_service(db)
    try:
        statement = service.get(statement_id)
        if not statement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Financial statement not found"
            )
        return service._format_statement_response(statement)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get(
    "/company/{company_id}",
    response_model=List[schemas.FinancialStatementResponse],
    summary="List financial statements for a company",
    description="List all financial statements for a specific company with optional filtering.",
    response_description="List of financial statements",
    tags=["Financial Statements"]
)
async def list_financial_statements(
    company_id: UUID,
    statement_type: Optional[schemas.FinancialStatementType] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    is_final: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    List all financial statements for a specific company with optional filtering.
    """
    service = get_gl_financial_statement_service(db)
    try:
        query = db.query(models.FinancialStatement).filter(
            models.FinancialStatement.company_id == company_id
        )
        
        if statement_type:
            query = query.filter(models.FinancialStatement.statement_type == statement_type)
        
        if start_date:
            query = query.filter(models.FinancialStatement.end_date >= start_date)
        
        if end_date:
            query = query.filter(models.FinancialStatement.start_date <= end_date)
        
        if is_final is not None:
            query = query.filter(models.FinancialStatement.is_final == is_final)
        
        statements = query.order_by(models.FinancialStatement.generated_at.desc())\
                         .offset(skip).limit(limit).all()
        
        return [service._format_statement_response(stmt) for stmt in statements]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )