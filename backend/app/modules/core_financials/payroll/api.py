"""
Payroll API endpoints.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db.base import get_db

# Import the employee API router
from app.modules.core_financials.payroll.api.employee_api import router as employee_router
from app.modules.core_financials.payroll.api.payroll_processing_api import router as payroll_processing_router
from app.modules.core_financials.payroll.api.tax_calculation_api import router as tax_calculation_router
from app.modules.core_financials.payroll.api.benefits_api import router as benefits_router
from app.modules.core_financials.payroll.api.payroll_reporting_api import router as payroll_reporting_router

from app.modules.core_financials.payroll.services import EmployeeService, PayrollService
from app.modules.core_financials.payroll.schemas import (
    EmployeeCreate, EmployeeUpdate, EmployeeResponse,
    PayrollRecordCreate, PayrollRecordResponse
)

router = APIRouter()
employee_service = EmployeeService()
payroll_service = PayrollService()

# Include the employee router
router.include_router(employee_router)
router.include_router(payroll_processing_router)
router.include_router(tax_calculation_router)
router.include_router(benefits_router)
router.include_router(payroll_reporting_router)

# Legacy Employee endpoints - these will be deprecated in favor of the new employee API
@router.post("/legacy/employees/", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED, deprecated=True)
async def create_employee(
    employee: EmployeeCreate,
    db: AsyncSession = Depends(get_db)
):
    # Check if employee ID already exists
    existing = await employee_service.get_by_employee_id(db, employee.employee_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee ID already exists"
        )
    return await employee_service.create(db, obj_in=employee)

@router.get("/legacy/employees/", response_model=List[EmployeeResponse], deprecated=True)
async def get_employees(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    db: AsyncSession = Depends(get_db)
):
    if active_only:
        return await employee_service.get_active_employees(db)
    return await employee_service.get_multi(db, skip=skip, limit=limit)

@router.get("/legacy/employees/{employee_id}", response_model=EmployeeResponse, deprecated=True)
async def get_employee(
    employee_id: int,
    db: AsyncSession = Depends(get_db)
):
    employee = await employee_service.get(db, employee_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    return employee

@router.put("/legacy/employees/{employee_id}", response_model=EmployeeResponse, deprecated=True)
async def update_employee(
    employee_id: int,
    employee_update: EmployeeUpdate,
    db: AsyncSession = Depends(get_db)
):
    employee = await employee_service.get(db, employee_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    return await employee_service.update(db, db_obj=employee, obj_in=employee_update)

# Payroll endpoints
@router.post("/payroll-records/", response_model=PayrollRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_payroll_record(
    payroll_record: PayrollRecordCreate,
    db: AsyncSession = Depends(get_db)
):
    # Verify employee exists
    employee = await employee_service.get(db, payroll_record.employee_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    return await payroll_service.create_payroll_record(db, payroll_data=payroll_record)

@router.get("/payroll-records/", response_model=List[PayrollRecordResponse])
async def get_payroll_records(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    return await payroll_service.get_multi(db, skip=skip, limit=limit)

@router.get("/payroll-records/employee/{employee_id}", response_model=List[PayrollRecordResponse])
async def get_employee_payroll_records(
    employee_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await payroll_service.get_payroll_records_by_employee(db, employee_id)

@router.get("/payroll-records/{record_id}", response_model=PayrollRecordResponse)
async def get_payroll_record(
    record_id: int,
    db: AsyncSession = Depends(get_db)
):
    record = await payroll_service.get(db, record_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payroll record not found"
        )
    return record

@router.post("/calculate-taxes/")
async def calculate_payroll_taxes(
    gross_pay: float,
    employee_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Calculate payroll taxes for given gross pay and employee."""
    from decimal import Decimal
    taxes = await payroll_service.calculate_payroll_taxes(
        Decimal(str(gross_pay)), employee_id
    )
    return {"taxes": taxes}