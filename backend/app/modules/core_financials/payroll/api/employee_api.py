"""
Employee API endpoints for the Payroll module.
"""
from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.db.session import get_db
from app.modules.core_financials.payroll.schemas.employee import (
    Employee, EmployeeList, EmployeeCreate, EmployeeUpdate
)
from app.modules.core_financials.payroll.services.employee_service import EmployeeService

router = APIRouter(prefix="/employees", tags=["employees"])


@router.get("/", response_model=EmployeeList)
def get_employees(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    department: Optional[str] = None,
    is_active: Optional[bool] = None,
    sort_by: str = Query("last_name", regex="^[a-zA-Z_]+$"),
    sort_order: str = Query("asc", regex="^(asc|desc)$"),
    db: Session = Depends(get_db)
):
    """
    Get a list of employees with optional filtering and sorting.
    """
    return EmployeeService.get_employees(
        db=db,
        skip=skip,
        limit=limit,
        search=search,
        department=department,
        is_active=is_active,
        sort_by=sort_by,
        sort_order=sort_order
    )


@router.get("/{employee_id}", response_model=Employee)
def get_employee(employee_id: UUID, db: Session = Depends(get_db)):
    """
    Get an employee by ID.
    """
    return EmployeeService.get_employee_by_id(db=db, employee_id=employee_id)


@router.get("/employee-id/{employee_code}", response_model=Employee)
def get_employee_by_code(employee_code: str, db: Session = Depends(get_db)):
    """
    Get an employee by employee ID (not UUID).
    """
    return EmployeeService.get_employee_by_employee_id(db=db, employee_id=employee_code)


@router.post("/", response_model=Employee, status_code=status.HTTP_201_CREATED)
def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    """
    Create a new employee.
    """
    return EmployeeService.create_employee(db=db, employee_data=employee)


@router.put("/{employee_id}", response_model=Employee)
def update_employee(
    employee_id: UUID,
    employee: EmployeeUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing employee.
    """
    return EmployeeService.update_employee(
        db=db,
        employee_id=employee_id,
        employee_data=employee
    )


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(employee_id: UUID, db: Session = Depends(get_db)):
    """
    Delete an employee.
    """
    EmployeeService.delete_employee(db=db, employee_id=employee_id)
    return None


@router.get("/departments/list", response_model=List[str])
def get_departments(db: Session = Depends(get_db)):
    """
    Get a list of all departments.
    """
    return EmployeeService.get_departments(db=db)


@router.get("/job-titles/list", response_model=List[str])
def get_job_titles(department: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Get a list of all job titles, optionally filtered by department.
    """
    return EmployeeService.get_job_titles(db=db, department=department)


@router.get("/stats/department-counts")
def get_employee_count_by_department(db: Session = Depends(get_db)):
    """
    Get employee count grouped by department.
    """
    return EmployeeService.get_employee_count_by_department(db=db)


@router.get("/managers/list", response_model=List[Employee])
def get_managers(db: Session = Depends(get_db)):
    """
    Get all employees who are managers (have subordinates).
    """
    return EmployeeService.get_managers(db=db)


@router.get("/subordinates/{manager_id}", response_model=List[Employee])
def get_subordinates(manager_id: UUID, db: Session = Depends(get_db)):
    """
    Get all employees reporting to a specific manager.
    """
    return EmployeeService.get_subordinates(db=db, manager_id=manager_id)