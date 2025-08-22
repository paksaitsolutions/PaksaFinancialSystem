"""
Employee service for the Payroll module.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from fastapi import HTTPException, status

from app.models.employee import Employee
from app.modules.core_financials.payroll.schemas.employee import EmployeeCreate, EmployeeUpdate


class EmployeeService:
    """Service for employee management operations."""
    
    @staticmethod
    def get_employees(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        department: Optional[str] = None,
        is_active: Optional[bool] = None,
        sort_by: str = "last_name",
        sort_order: str = "asc"
    ) -> Dict[str, Any]:
        """
        Get a list of employees with optional filtering and sorting.
        """
        query = db.query(Employee)
        
        # Apply filters
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Employee.first_name.ilike(search_term),
                    Employee.last_name.ilike(search_term),
                    Employee.employee_id.ilike(search_term),
                    Employee.email.ilike(search_term)
                )
            )
        
        if department:
            query = query.filter(Employee.department == department)
        
        if is_active is not None:
            query = query.filter(Employee.is_active == is_active)
        
        # Get total count before pagination
        total = query.count()
        
        # Apply sorting
        if sort_order.lower() == "desc":
            query = query.order_by(getattr(Employee, sort_by).desc())
        else:
            query = query.order_by(getattr(Employee, sort_by).asc())
        
        # Apply pagination
        employees = query.offset(skip).limit(limit).all()
        
        return {
            "items": employees,
            "total": total
        }
    
    @staticmethod
    def get_employee_by_id(db: Session, employee_id: UUID) -> Employee:
        """
        Get an employee by ID.
        """
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee with ID {employee_id} not found"
            )
        return employee
    
    @staticmethod
    def get_employee_by_employee_id(db: Session, employee_id: str) -> Employee:
        """
        Get an employee by employee ID (not UUID).
        """
        employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee with employee ID {employee_id} not found"
            )
        return employee
    
    @staticmethod
    def create_employee(db: Session, employee_data: EmployeeCreate) -> Employee:
        """
        Create a new employee.
        """
        # Check if employee with same employee_id, email, or identification numbers already exists
        existing_employee = db.query(Employee).filter(
            or_(
                Employee.employee_id == employee_data.employee_id,
                Employee.email == employee_data.email,
                and_(
                    Employee.national_id == employee_data.national_id,
                    employee_data.national_id is not None
                ),
                and_(
                    Employee.social_security_number == employee_data.social_security_number,
                    employee_data.social_security_number is not None
                ),
                and_(
                    Employee.tax_identification_number == employee_data.tax_identification_number,
                    employee_data.tax_identification_number is not None
                )
            )
        ).first()
        
        if existing_employee:
            if existing_employee.employee_id == employee_data.employee_id:
                field = "employee_id"
            elif existing_employee.email == employee_data.email:
                field = "email"
            elif existing_employee.national_id == employee_data.national_id:
                field = "national_id"
            elif existing_employee.social_security_number == employee_data.social_security_number:
                field = "social_security_number"
            else:
                field = "tax_identification_number"
                
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Employee with this {field} already exists"
            )
        
        # Create new employee
        employee = Employee(**employee_data.dict())
        db.add(employee)
        db.commit()
        db.refresh(employee)
        return employee
    
    @staticmethod
    def update_employee(
        db: Session, 
        employee_id: UUID, 
        employee_data: EmployeeUpdate
    ) -> Employee:
        """
        Update an existing employee.
        """
        employee = EmployeeService.get_employee_by_id(db, employee_id)
        
        # Check for unique constraints if updating unique fields
        if employee_data.employee_id or employee_data.email or employee_data.national_id or \
           employee_data.social_security_number or employee_data.tax_identification_number:
            
            filters = []
            if employee_data.employee_id:
                filters.append(Employee.employee_id == employee_data.employee_id)
            if employee_data.email:
                filters.append(Employee.email == employee_data.email)
            if employee_data.national_id:
                filters.append(Employee.national_id == employee_data.national_id)
            if employee_data.social_security_number:
                filters.append(Employee.social_security_number == employee_data.social_security_number)
            if employee_data.tax_identification_number:
                filters.append(Employee.tax_identification_number == employee_data.tax_identification_number)
            
            if filters:
                existing_employee = db.query(Employee).filter(
                    and_(
                        or_(*filters),
                        Employee.id != employee_id
                    )
                ).first()
                
                if existing_employee:
                    if employee_data.employee_id and existing_employee.employee_id == employee_data.employee_id:
                        field = "employee_id"
                    elif employee_data.email and existing_employee.email == employee_data.email:
                        field = "email"
                    elif employee_data.national_id and existing_employee.national_id == employee_data.national_id:
                        field = "national_id"
                    elif employee_data.social_security_number and existing_employee.social_security_number == employee_data.social_security_number:
                        field = "social_security_number"
                    else:
                        field = "tax_identification_number"
                        
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"Employee with this {field} already exists"
                    )
        
        # Update employee data
        update_data = employee_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(employee, key, value)
        
        db.commit()
        db.refresh(employee)
        return employee
    
    @staticmethod
    def delete_employee(db: Session, employee_id: UUID) -> None:
        """
        Delete an employee.
        """
        employee = EmployeeService.get_employee_by_id(db, employee_id)
        db.delete(employee)
        db.commit()
    
    @staticmethod
    def get_departments(db: Session) -> List[str]:
        """
        Get a list of all departments.
        """
        departments = db.query(Employee.department).distinct().all()
        return [dept[0] for dept in departments]
    
    @staticmethod
    def get_job_titles(db: Session, department: Optional[str] = None) -> List[str]:
        """
        Get a list of all job titles, optionally filtered by department.
        """
        query = db.query(Employee.job_title).distinct()
        if department:
            query = query.filter(Employee.department == department)
        job_titles = query.all()
        return [title[0] for title in job_titles]
    
    @staticmethod
    def get_employee_count_by_department(db: Session) -> Dict[str, int]:
        """
        Get employee count grouped by department.
        """
        from sqlalchemy import func
        result = db.query(
            Employee.department,
            func.count(Employee.id).label('count')
        ).group_by(Employee.department).all()
        
        return {dept: count for dept, count in result}
    
    @staticmethod
    def get_managers(db: Session) -> List[Employee]:
        """
        Get all employees who are managers (have subordinates).
        """
        # Get distinct manager IDs
        manager_ids = db.query(Employee.manager_id).filter(
            Employee.manager_id.isnot(None)
        ).distinct().all()
        
        # Get the actual manager records
        manager_ids = [m[0] for m in manager_ids]
        if not manager_ids:
            return []
            
        managers = db.query(Employee).filter(Employee.id.in_(manager_ids)).all()
        return managers
    
    @staticmethod
    def get_subordinates(db: Session, manager_id: UUID) -> List[Employee]:
        """
        Get all employees reporting to a specific manager.
        """
        subordinates = db.query(Employee).filter(Employee.manager_id == manager_id).all()
        return subordinates