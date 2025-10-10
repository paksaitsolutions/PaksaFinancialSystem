"""
CRUD operations for Employee model.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from app.crud.base import CRUDBase
from app.models.hrm.employee import Employee
from app.schemas.hrm.employee import EmployeeCreate, EmployeeUpdate


class CRUDEmployee(CRUDBase[Employee, EmployeeCreate, EmployeeUpdate]):
    """CRUD operations for Employee"""
    
    def get_by_employee_id(self, db: Session, *, employee_id: str) -> Optional[Employee]:
        """Get employee by employee ID"""
        return db.query(Employee).filter(Employee.employee_id == employee_id).first()
    
    def get_by_email(self, db: Session, *, email: str) -> Optional[Employee]:
        """Get employee by email"""
        return db.query(Employee).filter(Employee.email == email).first()
    
    def get_by_department(self, db: Session, *, department_id: UUID) -> List[Employee]:
        """Get employees by department"""
        return db.query(Employee).filter(Employee.department_id == department_id).all()
    
    def get_active_employees(self, db: Session) -> List[Employee]:
        """Get all active employees"""
        return db.query(Employee).filter(Employee.is_active == True).all()
    
    def search_employees(
        self, 
        db: Session, 
        *, 
        search_term: str = None,
        department_id: UUID = None,
        is_active: bool = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Employee]:
        """Search employees with filters"""
        query = db.query(Employee)
        
        if search_term:
            query = query.filter(
                or_(
                    Employee.first_name.ilike(f"%{search_term}%"),
                    Employee.last_name.ilike(f"%{search_term}%"),
                    Employee.email.ilike(f"%{search_term}%"),
                    Employee.employee_id.ilike(f"%{search_term}%")
                )
            )
        
        if department_id:
            query = query.filter(Employee.department_id == department_id)
        
        if is_active is not None:
            query = query.filter(Employee.is_active == is_active)
        
        return query.offset(skip).limit(limit).all()
    
    def get_employee_stats(self, db: Session) -> Dict[str, Any]:
        """Get employee statistics"""
        total_employees = db.query(Employee).count()
        active_employees = db.query(Employee).filter(Employee.is_active == True).count()
        inactive_employees = total_employees - active_employees
        
        return {
            "total_employees": total_employees,
            "active_employees": active_employees,
            "inactive_employees": inactive_employees
        }


employee = CRUDEmployee(Employee)

# Convenience functions for backward compatibility
def get_employees(db: Session, skip: int = 0, limit: int = 100) -> List[Employee]:
    """Get all employees"""
    return employee.get_multi(db, skip=skip, limit=limit)

def get_employee(db: Session, employee_id: UUID) -> Optional[Employee]:
    """Get employee by ID"""
    return employee.get(db, id=employee_id)