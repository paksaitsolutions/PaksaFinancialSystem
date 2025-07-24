"""
Payroll reporting API endpoints for the Payroll module.
"""
from typing import Optional, List
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.db.session import get_db
from app.modules.core_financials.payroll.schemas.payroll_reporting import (
    PayrollReportRequest, PayrollSummaryReport, EmployeeEarningsReport,
    TaxLiabilityReport, BenefitsReport, DepartmentCostsReport, YearEndSummary
)
from app.modules.core_financials.payroll.services.payroll_reporting_service import PayrollReportingService

router = APIRouter(prefix="/payroll-reports", tags=["payroll-reports"])


@router.get("/payroll-summary", response_model=PayrollSummaryReport)
def get_payroll_summary_report(
    start_date: date = Query(..., description="Report start date"),
    end_date: date = Query(..., description="Report end date"),
    department: Optional[str] = Query(None, description="Filter by department"),
    db: Session = Depends(get_db)
):
    """Generate payroll summary report."""
    return PayrollReportingService.generate_payroll_summary_report(
        db=db,
        start_date=start_date,
        end_date=end_date,
        department=department
    )


@router.get("/employee-earnings", response_model=List[EmployeeEarningsReport])
def get_employee_earnings_report(
    start_date: date = Query(..., description="Report start date"),
    end_date: date = Query(..., description="Report end date"),
    employee_ids: Optional[str] = Query(None, description="Comma-separated employee IDs"),
    db: Session = Depends(get_db)
):
    """Generate employee earnings report."""
    employee_id_list = None
    if employee_ids:
        employee_id_list = employee_ids.split(',')
    
    return PayrollReportingService.generate_employee_earnings_report(
        db=db,
        start_date=start_date,
        end_date=end_date,
        employee_ids=employee_id_list
    )


@router.get("/tax-liability", response_model=TaxLiabilityReport)
def get_tax_liability_report(
    start_date: date = Query(..., description="Report start date"),
    end_date: date = Query(..., description="Report end date"),
    db: Session = Depends(get_db)
):
    """Generate tax liability report."""
    return PayrollReportingService.generate_tax_liability_report(
        db=db,
        start_date=start_date,
        end_date=end_date
    )


@router.get("/benefits", response_model=BenefitsReport)
def get_benefits_report(
    start_date: date = Query(..., description="Report start date"),
    end_date: date = Query(..., description="Report end date"),
    db: Session = Depends(get_db)
):
    """Generate benefits report."""
    return PayrollReportingService.generate_benefits_report(
        db=db,
        start_date=start_date,
        end_date=end_date
    )


@router.get("/department-costs", response_model=DepartmentCostsReport)
def get_department_costs_report(
    start_date: date = Query(..., description="Report start date"),
    end_date: date = Query(..., description="Report end date"),
    db: Session = Depends(get_db)
):
    """Generate department costs report."""
    return PayrollReportingService.generate_department_costs_report(
        db=db,
        start_date=start_date,
        end_date=end_date
    )


@router.get("/year-end-summary", response_model=YearEndSummary)
def get_year_end_summary(
    year: int = Query(..., description="Year for the summary"),
    db: Session = Depends(get_db)
):
    """Generate year-end summary report."""
    return PayrollReportingService.generate_year_end_summary(
        db=db,
        year=year
    )


@router.get("/available-reports")
def get_available_reports():
    """Get list of available report types."""
    from app.modules.core_financials.payroll.schemas.payroll_reporting import ReportTypeEnum
    
    return [
        {
            "type": "PAYROLL_SUMMARY",
            "name": "Payroll Summary",
            "description": "Overall payroll summary with department breakdown"
        },
        {
            "type": "EMPLOYEE_EARNINGS",
            "name": "Employee Earnings",
            "description": "Detailed earnings report by employee"
        },
        {
            "type": "TAX_LIABILITY",
            "name": "Tax Liability",
            "description": "Tax liability breakdown by type"
        },
        {
            "type": "BENEFITS_REPORT",
            "name": "Benefits Report",
            "description": "Employee benefits contributions and costs"
        },
        {
            "type": "DEPARTMENT_COSTS",
            "name": "Department Costs",
            "description": "Payroll costs breakdown by department"
        },
        {
            "type": "YEAR_END_SUMMARY",
            "name": "Year-End Summary",
            "description": "Annual payroll summary with quarterly breakdown"
        }
    ]