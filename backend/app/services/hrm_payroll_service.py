"""
HRM Payroll Integration Service
"""
from uuid import UUID
from sqlalchemy.orm import Session
from app.models import Employee, Department, PayrollRun, PayrollEntry
from app.services.base import BaseService

class HRMPayrollService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db, Employee)
    
    def sync_employee_to_payroll(self, employee: Employee) -> None:
        """Sync employee changes to payroll system"""
        # Employee data is already unified, no sync needed
        # This method handles any payroll-specific updates
        
        # Update any active payroll entries if salary changed
        if employee.salary:
            active_payroll_entries = self.db.query(PayrollEntry).join(PayrollRun).filter(
                PayrollEntry.employee_id == employee.id,
                PayrollRun.status == 'draft'
            ).all()
            
            for entry in active_payroll_entries:
                entry.gross_pay = employee.salary
                entry.net_pay = employee.salary - entry.total_deductions
    
    def create_payroll_run_for_department(self, department_id: UUID, pay_period_start, pay_period_end, pay_date) -> PayrollRun:
        """Create payroll run for all employees in department"""
        
        department = self.db.query(Department).filter(Department.id == department_id).first()
        if not department:
            raise ValueError("Department not found")
        
        # Get all active employees in department
        employees = self.db.query(Employee).filter(
            Employee.department_id == department_id,
            Employee.status == 'active'
        ).all()
        
        # Create payroll run
        payroll_run = PayrollRun(
            company_id=department.company_id,
            run_number=f"PR-{department.department_code}-{pay_period_start.strftime('%Y%m%d')}",
            pay_period_start=pay_period_start,
            pay_period_end=pay_period_end,
            pay_date=pay_date,
            status='draft'
        )
        self.db.add(payroll_run)
        self.db.flush()
        
        # Create payroll entries for each employee
        total_gross = 0
        total_net = 0
        
        for employee in employees:
            entry = PayrollEntry(
                payroll_run_id=payroll_run.id,
                employee_id=employee.id,
                gross_pay=employee.salary or 0,
                total_deductions=0,  # Calculate based on employee deductions
                net_pay=employee.salary or 0
            )
            self.db.add(entry)
            
            total_gross += entry.gross_pay
            total_net += entry.net_pay
        
        payroll_run.total_gross = total_gross
        payroll_run.total_net = total_net
        
        return payroll_run
    
    def get_employee_payroll_summary(self, employee_id: UUID) -> dict:
        """Get unified employee and payroll summary"""
        
        employee = self.db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            return {}
        
        # Get recent payroll entries
        recent_entries = self.db.query(PayrollEntry).join(PayrollRun).filter(
            PayrollEntry.employee_id == employee_id
        ).order_by(PayrollRun.pay_date.desc()).limit(6).all()
        
        return {
            "employee": {
                "id": str(employee.id),
                "employee_code": employee.employee_code,
                "name": f"{employee.first_name} {employee.last_name}",
                "department": employee.department.department_name if employee.department else None,
                "position": employee.position,
                "salary": float(employee.salary or 0),
                "employment_type": employee.employment_type,
                "hire_date": employee.hire_date.isoformat() if employee.hire_date else None
            },
            "payroll_history": [
                {
                    "pay_date": entry.payroll_run.pay_date.isoformat(),
                    "gross_pay": float(entry.gross_pay),
                    "deductions": float(entry.total_deductions),
                    "net_pay": float(entry.net_pay)
                }
                for entry in recent_entries
            ]
        }