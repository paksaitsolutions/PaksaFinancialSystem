"""
Payroll processing API endpoints for the Payroll module.
"""
from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.db.session import get_db
from app.modules.core_financials.payroll.schemas.payroll_processing import (
    PayrollRunCreate, PayrollRunUpdate, PayrollRunResponse,
    PayrollCalculationRequest, PayslipCreate, PayslipResponse,
    PayrollSummary
)
from app.modules.core_financials.payroll.services.payroll_processing_service import PayrollProcessingService

router = APIRouter(prefix="/payroll-processing", tags=["payroll-processing"])


@router.post("/runs", response_model=PayrollRunResponse, status_code=status.HTTP_201_CREATED)
def create_payroll_run(
    payroll_run: PayrollRunCreate,
    db: Session = Depends(get_db)
):
    """Create a new payroll run."""
    return PayrollProcessingService.create_payroll_run(db=db, payroll_data=payroll_run)


@router.get("/runs")
def get_payroll_runs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get payroll runs with optional filtering."""
    return PayrollProcessingService.get_payroll_runs(
        db=db,
        skip=skip,
        limit=limit,
        status=status
    )


@router.get("/runs/{payroll_run_id}", response_model=PayrollRunResponse)
def get_payroll_run(payroll_run_id: UUID, db: Session = Depends(get_db)):
    """Get a specific payroll run."""
    runs = PayrollProcessingService.get_payroll_runs(db=db, skip=0, limit=1)
    for run in runs["items"]:
        if run["id"] == payroll_run_id:
            return run
    
    from fastapi import HTTPException
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Payroll run not found"
    )


@router.put("/runs/{payroll_run_id}", response_model=PayrollRunResponse)
def update_payroll_run(
    payroll_run_id: UUID,
    payroll_run: PayrollRunUpdate,
    db: Session = Depends(get_db)
):
    """Update a payroll run."""
    # Implementation would go here
    pass


@router.post("/runs/{payroll_run_id}/calculate")
def calculate_payroll(
    payroll_run_id: UUID,
    calculation_request: PayrollCalculationRequest,
    db: Session = Depends(get_db)
):
    """Calculate payroll for specified employees."""
    return PayrollProcessingService.calculate_payroll(
        db=db,
        payroll_run_id=payroll_run_id,
        calculation_request=calculation_request
    )


@router.post("/runs/{payroll_run_id}/process")
def process_payroll(
    payroll_run_id: UUID,
    payslips: List[PayslipCreate],
    db: Session = Depends(get_db)
):
    """Process payroll and create payslips."""
    return PayrollProcessingService.process_payroll(
        db=db,
        payroll_run_id=payroll_run_id,
        payslips_data=payslips
    )


@router.post("/runs/{payroll_run_id}/approve")
def approve_payroll(payroll_run_id: UUID, db: Session = Depends(get_db)):
    """Approve a payroll run."""
    return PayrollProcessingService.approve_payroll(
        db=db,
        payroll_run_id=payroll_run_id
    )


@router.get("/runs/{payroll_run_id}/summary", response_model=PayrollSummary)
def get_payroll_summary(payroll_run_id: UUID, db: Session = Depends(get_db)):
    """Get payroll summary for a specific run."""
    return PayrollProcessingService.get_payroll_summary(
        db=db,
        payroll_run_id=payroll_run_id
    )


@router.get("/runs/{payroll_run_id}/payslips")
def get_payroll_payslips(
    payroll_run_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get payslips for a specific payroll run."""
    from app.models.payslip import Payslip
    from app.models.employee import Employee
    
    query = db.query(Payslip, Employee).join(Employee).filter(
        Payslip.pay_period_id == payroll_run_id
    )
    
    total = query.count()
    payslips = query.offset(skip).limit(limit).all()
    
    result = []
    for payslip, employee in payslips:
        result.append({
            "id": payslip.id,
            "employee_id": employee.id,
            "employee_name": employee.full_name,
            "employee_code": employee.employee_id,
            "payroll_run_id": payroll_run_id,
            "gross_pay": payslip.gross_pay,
            "basic_salary": payslip.basic_salary,
            "overtime_pay": payslip.overtime_pay,
            "bonus": payslip.bonus,
            "allowances": payslip.allowances,
            "deductions": payslip.deductions,
            "tax_deductions": payslip.tax_deductions,
            "net_pay": payslip.net_pay,
            "created_at": payslip.created_at
        })
    
    return {
        "items": result,
        "total": total
    }