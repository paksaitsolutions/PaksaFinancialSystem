"""
Payroll API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.payroll_models import Employee, PayRun, Payslip, PayrollItem
from app.services.payroll_service import PayrollService

router = APIRouter(prefix="/api/payroll", tags=["payroll"])

# Pydantic models
class EmployeeCreate(BaseModel):
    employee_id: str
    first_name: str
    last_name: str
    email: str
    phone_number: Optional[str] = None
    department: str
    job_title: str
    employment_type: str = "full_time"
    hire_date: Optional[date] = None
    base_salary: Decimal
    pay_frequency: str = "monthly"
    tax_id: Optional[str] = None
    tax_exemptions: int = 0

class EmployeeResponse(BaseModel):
    id: str
    employee_id: str
    first_name: str
    last_name: str
    full_name: str
    email: str
    phone_number: Optional[str] = None
    department: str
    job_title: str
    employment_type: str
    hire_date: date
    base_salary: Decimal
    pay_frequency: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PayRunCreate(BaseModel):
    pay_period_start: date
    pay_period_end: date
    pay_date: date
    employee_ids: Optional[List[str]] = None

class PayRunResponse(BaseModel):
    id: str
    run_number: str
    pay_period_start: date
    pay_period_end: date
    pay_date: date
    status: str
    total_gross_pay: Decimal
    total_deductions: Decimal
    total_taxes: Decimal
    total_net_pay: Decimal
    processed_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class PayslipResponse(BaseModel):
    id: str
    payslip_number: str
    employee_id: str
    pay_period_start: date
    pay_period_end: date
    pay_date: date
    gross_pay: Decimal
    total_deductions: Decimal
    net_pay: Decimal
    federal_tax: Decimal
    state_tax: Decimal
    health_insurance: Decimal
    regular_hours: Decimal
    overtime_hours: Decimal
    is_paid: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Employee endpoints
@router.get("/employees", response_model=List[EmployeeResponse])
async def get_employees(
    active_only: bool = True,
    department: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all employees."""
    payroll_service = PayrollService(db)
    employees = payroll_service.get_employees(active_only, department)
    return employees

@router.post("/employees", response_model=EmployeeResponse)
async def create_employee(
    employee_data: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new employee."""
    payroll_service = PayrollService(db)
    
    # Check if employee ID already exists
    existing = db.query(Employee).filter(Employee.employee_id == employee_data.employee_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Employee ID already exists")
    
    employee = payroll_service.create_employee(**employee_data.dict())
    return employee

@router.get("/employees/{employee_id}", response_model=EmployeeResponse)
async def get_employee(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get employee by ID."""
    payroll_service = PayrollService(db)
    employee = payroll_service.get_employee(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

@router.put("/employees/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: str,
    employee_data: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update employee."""
    payroll_service = PayrollService(db)
    employee = payroll_service.update_employee(employee_id, **employee_data.dict())
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

@router.delete("/employees/{employee_id}")
async def delete_employee(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Deactivate employee."""
    payroll_service = PayrollService(db)
    employee = payroll_service.update_employee(employee_id, is_active=False)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"message": "Employee deactivated successfully"}

# Pay run endpoints
@router.get("/pay-runs", response_model=List[PayRunResponse])
async def get_pay_runs(
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get pay runs."""
    payroll_service = PayrollService(db)
    pay_runs = payroll_service.get_pay_runs(limit)
    return pay_runs

@router.post("/pay-runs", response_model=PayRunResponse)
async def create_pay_run(
    pay_run_data: PayRunCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new pay run."""
    payroll_service = PayrollService(db)
    pay_run = payroll_service.create_pay_run(**pay_run_data.dict())
    return pay_run

@router.get("/pay-runs/{pay_run_id}", response_model=PayRunResponse)
async def get_pay_run(
    pay_run_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get pay run by ID."""
    payroll_service = PayrollService(db)
    pay_run = payroll_service.get_pay_run(pay_run_id)
    if not pay_run:
        raise HTTPException(status_code=404, detail="Pay run not found")
    return pay_run

@router.post("/pay-runs/{pay_run_id}/process", response_model=PayRunResponse)
async def process_pay_run(
    pay_run_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Process pay run calculations."""
    payroll_service = PayrollService(db)
    try:
        pay_run = payroll_service.process_pay_run(pay_run_id)
        return pay_run
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/pay-runs/{pay_run_id}/approve", response_model=PayRunResponse)
async def approve_pay_run(
    pay_run_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Approve a pay run."""
    payroll_service = PayrollService(db)
    try:
        pay_run = payroll_service.approve_pay_run(pay_run_id, str(current_user.id))
        return pay_run
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Payslip endpoints
@router.get("/payslips", response_model=List[PayslipResponse])
async def get_payslips(
    employee_id: Optional[str] = None,
    pay_run_id: Optional[str] = None,
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get payslips."""
    payroll_service = PayrollService(db)
    payslips = payroll_service.get_payslips(employee_id, pay_run_id, limit)
    return payslips

@router.get("/payslips/{payslip_id}", response_model=PayslipResponse)
async def get_payslip(
    payslip_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get payslip by ID."""
    payroll_service = PayrollService(db)
    payslip = payroll_service.get_payslip(payslip_id)
    if not payslip:
        raise HTTPException(status_code=404, detail="Payslip not found")
    return payslip

# Analytics endpoints
@router.get("/summary")
async def get_payroll_summary(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get payroll summary for a period."""
    payroll_service = PayrollService(db)
    summary = payroll_service.get_payroll_summary(start_date, end_date)
    return summary

@router.get("/departments/list")
async def get_departments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get list of departments."""
    departments = db.query(Employee.department).distinct().all()
    return [dept[0] for dept in departments if dept[0]]

@router.get("/employees/stats/department-counts")
async def get_department_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get employee count by department."""
    from sqlalchemy import func
    
    stats = db.query(
        Employee.department,
        func.count(Employee.id).label('count')
    ).filter(
        Employee.is_active == True
    ).group_by(Employee.department).all()
    
    return {dept: count for dept, count in stats}