"""
Enhanced reports API endpoints with multi-tenant support.
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app import models
from app.api import deps
from app.core.db.session import get_db
from app.schemas.enhanced_reports_schemas import (
    CompanyReportResponse,
    ReportTemplateRequest,
    ReportTemplateResponse,
    ReportScheduleRequest,
    ReportScheduleResponse,
    IncomeStatementRequest,
    BalanceSheetRequest,
    AgingReportRequest,
    AuditReportRequest
)
from app.services.reports.enhanced_reports_service import EnhancedReportsService

router = APIRouter()


def get_reports_service(db: Session = Depends(get_db)) -> EnhancedReportsService:
    """Get an instance of the enhanced reports service."""
    return EnhancedReportsService(db)


@router.post(
    "/{company_id}/income-statement",
    response_model=CompanyReportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate income statement",
    description="Generate Income Statement (Profit & Loss) for company.",
    tags=["Financial Reports"]
)
async def generate_income_statement(
    company_id: UUID,
    request: IncomeStatementRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> CompanyReportResponse:
    """Generate Income Statement for company."""
    service = get_reports_service(db)
    
    try:
        report = service.generate_income_statement(
            company_id=company_id,
            period_start=request.period_start,
            period_end=request.period_end,
            generated_by=current_user.id
        )
        return report
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/{company_id}/balance-sheet",
    response_model=CompanyReportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate balance sheet",
    description="Generate Balance Sheet for company.",
    tags=["Financial Reports"]
)
async def generate_balance_sheet(
    company_id: UUID,
    request: BalanceSheetRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> CompanyReportResponse:
    """Generate Balance Sheet for company."""
    service = get_reports_service(db)
    
    try:
        report = service.generate_balance_sheet(
            company_id=company_id,
            period_end=request.as_of_date,
            generated_by=current_user.id
        )
        return report
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/{company_id}/aging-report",
    response_model=CompanyReportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate aging report",
    description="Generate Payables/Receivables Aging Report for company.",
    tags=["Operational Reports"]
)
async def generate_aging_report(
    company_id: UUID,
    request: AgingReportRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> CompanyReportResponse:
    """Generate Aging Report for company."""
    service = get_reports_service(db)
    
    try:
        report = service.generate_aging_report(
            company_id=company_id,
            report_type=request.aging_type,
            as_of_date=request.as_of_date,
            generated_by=current_user.id
        )
        return report
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/{company_id}/reports",
    response_model=List[CompanyReportResponse],
    summary="List company reports",
    description="List all reports for a company.",
    tags=["Report Management"]
)
async def list_company_reports(
    company_id: UUID,
    limit: int = Query(100, description="Maximum number of records"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> List[CompanyReportResponse]:
    """List reports for a company."""
    service = get_reports_service(db)
    
    reports = service.list_company_reports(company_id, limit=limit)
    return reports


@router.get(
    "/report/{report_id}",
    response_model=CompanyReportResponse,
    summary="Get report",
    description="Get a specific report by ID.",
    tags=["Report Management"]
)
async def get_report(
    report_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> CompanyReportResponse:
    """Get a specific report."""
    service = get_reports_service(db)
    
    report = service.get_report(report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    return report


@router.post(
    "/{company_id}/templates",
    response_model=ReportTemplateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create report template",
    description="Create a company-specific report template.",
    tags=["Report Templates"]
)
async def create_report_template(
    company_id: UUID,
    template_request: ReportTemplateRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> ReportTemplateResponse:
    """Create report template for company."""
    service = get_reports_service(db)
    
    try:
        template = service.create_report_template(
            company_id=company_id,
            template_data=template_request.dict(),
            created_by=current_user.id
        )
        return template
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )