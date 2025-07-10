from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.db.session import get_db
from app.core.security import get_current_active_user
from app.modules.core_financials.payroll import schemas, services
from app.modules.core_financials.payroll.services.exceptions import (
    PayrollRunNotFoundError,
    PayrollProcessingError,
    EmployeeNotFoundError,
    PayPeriodError
)

router = APIRouter()

# Pay Period endpoints
@router.post("/pay-periods/", response_model=schemas.PayPeriod)
def create_pay_period(
    pay_period: schemas.PayPeriodCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Create a new pay period"""
    try:
        return services.create_pay_period(db=db, pay_period=pay_period, user_id=current_user.id)
    except PayPeriodError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/pay-periods/", response_model=List[schemas.PayPeriod])
def list_pay_periods(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """List all pay periods with pagination"""
    return services.get_pay_periods(db, skip=skip, limit=limit)

# Pay Run endpoints
@router.post("/pay-runs/", response_model=schemas.PayRun)
def create_pay_run(
    pay_run: schemas.PayRunCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Create a new pay run"""
    try:
        return services.create_pay_run(
            db=db, 
            pay_run=pay_run,
            user_id=current_user.id
        )
    except PayPeriodError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PayrollProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/pay-runs/", response_model=List[schemas.PayRun])
def list_pay_runs(
    skip: int = 0, 
    limit: int = 100,
    status: Optional[str] = None,
    pay_period_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """List pay runs with optional filtering by status and pay period"""
    return services.get_pay_runs(
        db, 
        skip=skip, 
        limit=limit,
        status=status,
        pay_period_id=pay_period_id
    )

@router.get("/pay-runs/{pay_run_id}", response_model=schemas.PayRunWithDetails)
def get_pay_run(
    pay_run_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get pay run details including all payslips"""
    try:
        return services.get_pay_run_with_details(db, pay_run_id=pay_run_id)
    except PayrollRunNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/pay-runs/{pay_run_id}/process", response_model=schemas.PayRun)
def process_pay_run(
    pay_run_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Process a pay run (calculate all payslips)"""
    try:
        return services.process_pay_run(db, pay_run_id=pay_run_id, user_id=current_user.id)
    except PayrollRunNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PayrollProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/pay-runs/{pay_run_id}/approve", response_model=schemas.PayRun)
def approve_pay_run(
    pay_run_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Approve a processed pay run"""
    try:
        return services.approve_pay_run(db, pay_run_id=pay_run_id, user_id=current_user.id)
    except PayrollRunNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PayrollProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/pay-runs/{pay_run_id}/post-to-ledger", response_model=schemas.PayRun)
def post_pay_run_to_ledger(
    pay_run_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Post pay run to general ledger"""
    try:
        return services.post_pay_run_to_ledger(db, pay_run_id=pay_run_id, user_id=current_user.id)
    except PayrollRunNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PayrollProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Payslip endpoints
@router.get("/payslips/{payslip_id}", response_model=schemas.PayslipWithDetails)
def get_payslip(
    payslip_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get payslip details with all line items"""
    try:
        return services.get_payslip_with_details(db, payslip_id=payslip_id)
    except services.PayslipNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/payslips/{payslip_id}/email")
def email_payslip(
    payslip_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Email a payslip to the employee"""
    try:
        services.email_payslip(db, payslip_id=payslip_id, user_id=current_user.id)
        return {"status": "success", "message": "Payslip email sent successfully"}
    except services.PayslipNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except services.EmailError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Employee payroll endpoints
@router.get("/employees/{employee_id}/payslips", response_model=List[schemas.Payslip])
def get_employee_payslips(
    employee_id: int,
    year: Optional[int] = None,
    skip: int = 0,
    limit: int = 12,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get payslips for an employee with optional year filter"""
    try:
        return services.get_employee_payslips(
            db, 
            employee_id=employee_id,
            year=year,
            skip=skip,
            limit=limit
        )
    except EmployeeNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/employees/{employee_id}/ytd-summary", response_model=schemas.YearToDateSummary)
def get_employee_ytd_summary(
    employee_id: int,
    year: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get year-to-date summary for an employee"""
    try:
        year = year or date.today().year
        return services.get_employee_ytd_summary(
            db, 
            employee_id=employee_id,
            year=year
        )
    except EmployeeNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PayrollProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))
