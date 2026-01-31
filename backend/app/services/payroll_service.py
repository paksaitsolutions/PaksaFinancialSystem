"""
Payroll service for calculations and management.
"""
from datetime import date, datetime, timedelta
from typing import List, Optional, Dict, Any

from decimal import Decimal
from sqlalchemy import and_, or_, desc
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.payroll_models import Employee, PayRun, PayRunEmployee, Payslip, PayrollItem, EmployeePayrollItem



class PayrollService:
    """Service for payroll calculations and management."""
    
    def __init__(self, db: Session):
        """  Init  ."""
        self.db = db
    
    # Employee Management
    def create_employee(
        """Create Employee."""
        self,
        employee_id: str,
        first_name: str,
        last_name: str,
        email: str,
        department: str,
        job_title: str,
        base_salary: Decimal,
        **kwargs
    ) -> Employee:
        """Create Employee."""
        """Create a new employee."""
        
        employee = Employee(
            employee_id=employee_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            department=department,
            job_title=job_title,
            base_salary=base_salary,
            **kwargs
        )
        
        self.db.add(employee)
        self.db.commit()
        self.db.refresh(employee)
        
        return employee
    
    def get_employees(
        """Get Employees."""
        self,
        active_only: bool = True,
        department: Optional[str] = None
    ) -> List[Employee]:
        """Get Employees."""
        """Get employees with optional filtering."""
        
        query = self.db.query(Employee)
        
        if active_only:
            query = query.filter(Employee.is_active == True)
        if department:
            query = query.filter(Employee.department == department)
        
        return query.order_by(Employee.last_name, Employee.first_name).all()
    
    def get_employee(self, employee_id: str) -> Optional[Employee]:
        """Get Employee."""
        """Get employee by ID."""
        return self.db.query(Employee).filter(Employee.id == employee_id).first()
    
    def update_employee(self, employee_id: str, **kwargs) -> Optional[Employee]:
        """Update Employee."""
        """Update employee information."""
        
        employee = self.get_employee(employee_id)
        if not employee:
            return None
        
        for key, value in kwargs.items():
            if hasattr(employee, key):
                setattr(employee, key, value)
        
        employee.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(employee)
        
        return employee
    
    # Pay Run Management
    def create_pay_run(
        """Create Pay Run."""
        self,
        pay_period_start: date,
        pay_period_end: date,
        pay_date: date,
        employee_ids: Optional[List[str]] = None
    ) -> PayRun:
        """Create Pay Run."""
        """Create a new pay run."""
        
        # Generate run number
        run_number = f"PR-{pay_period_start.strftime('%Y%m%d')}-{pay_period_end.strftime('%Y%m%d')}"
        
        pay_run = PayRun(
            run_number=run_number,
            pay_period_start=pay_period_start,
            pay_period_end=pay_period_end,
            pay_date=pay_date
        )
        
        self.db.add(pay_run)
        self.db.flush()  # Get the ID
        
        # Add employees to pay run
        if employee_ids:
            employees = self.db.query(Employee).filter(Employee.id.in_(employee_ids)).all()
        else:
            employees = self.get_employees(active_only=True)
        
        for employee in employees:
            pay_run_employee = PayRunEmployee(
                pay_run_id=pay_run.id,
                employee_id=employee.id,
                gross_pay=employee.base_salary,
                net_pay=employee.base_salary  # Will be calculated later
            )
            self.db.add(pay_run_employee)
        
        self.db.commit()
        self.db.refresh(pay_run)
        
        return pay_run
    
    def get_pay_runs(self, limit: int = 50) -> List[PayRun]:
        """Get Pay Runs."""
        """Get pay runs ordered by creation date."""
        return self.db.query(PayRun).order_by(desc(PayRun.created_at)).limit(limit).all()
    
    def get_pay_run(self, pay_run_id: str) -> Optional[PayRun]:
        """Get Pay Run."""
        """Get pay run by ID."""
        return self.db.query(PayRun).filter(PayRun.id == pay_run_id).first()
    
    def process_pay_run(self, pay_run_id: str) -> PayRun:
        """Process Pay Run."""
        """Process pay run calculations."""
        
        pay_run = self.get_pay_run(pay_run_id)
        if not pay_run:
            raise ValueError("Pay run not found")
        
        if pay_run.status != "draft":
            raise ValueError("Pay run is not in draft status")
        
        total_gross = Decimal("0.00")
        total_deductions = Decimal("0.00")
        total_taxes = Decimal("0.00")
        total_net = Decimal("0.00")
        
        # Process each employee
        for pay_run_employee in pay_run.employees:
            employee = pay_run_employee.employee
            
            # Calculate gross pay (simplified)
            gross_pay = employee.base_salary
            
            # Calculate taxes (simplified - 20% total)
            taxes = gross_pay * Decimal("0.20")
            
            # Calculate deductions (simplified - health insurance)
            deductions = Decimal("200.00")  # Fixed health insurance
            
            # Calculate net pay
            net_pay = gross_pay - taxes - deductions
            
            # Update pay run employee
            pay_run_employee.gross_pay = gross_pay
            pay_run_employee.total_taxes = taxes
            pay_run_employee.total_deductions = deductions
            pay_run_employee.net_pay = net_pay
            pay_run_employee.is_processed = True
            
            # Create payslip
            payslip = self.create_payslip(pay_run, employee, pay_run_employee)
            
            # Update totals
            total_gross += gross_pay
            total_deductions += deductions
            total_taxes += taxes
            total_net += net_pay
        
        # Update pay run totals
        pay_run.total_gross_pay = total_gross
        pay_run.total_deductions = total_deductions
        pay_run.total_taxes = total_taxes
        pay_run.total_net_pay = total_net
        pay_run.status = "processing"
        pay_run.processed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(pay_run)
        
        return pay_run
    
    def approve_pay_run(self, pay_run_id: str, approved_by: str) -> PayRun:
        """Approve Pay Run."""
        """Approve a pay run."""
        
        pay_run = self.get_pay_run(pay_run_id)
        if not pay_run:
            raise ValueError("Pay run not found")
        
        if pay_run.status != "processing":
            raise ValueError("Pay run is not ready for approval")
        
        pay_run.status = "approved"
        pay_run.approved_at = datetime.utcnow()
        pay_run.approved_by = approved_by
        
        self.db.commit()
        self.db.refresh(pay_run)
        
        return pay_run
    
    def create_payslip(self, pay_run: PayRun, employee: Employee, pay_run_employee: PayRunEmployee) -> Payslip:
        """Create Payslip."""
        """Create a payslip for an employee."""
        
        payslip_number = f"PS-{employee.employee_id}-{pay_run.pay_period_start.strftime('%Y%m')}"
        
        payslip = Payslip(
            payslip_number=payslip_number,
            pay_run_id=pay_run.id,
            employee_id=employee.id,
            pay_period_start=pay_run.pay_period_start,
            pay_period_end=pay_run.pay_period_end,
            pay_date=pay_run.pay_date,
            base_salary=pay_run_employee.gross_pay,
            gross_pay=pay_run_employee.gross_pay,
            federal_tax=pay_run_employee.total_taxes * Decimal("0.7"),  # 70% federal
            state_tax=pay_run_employee.total_taxes * Decimal("0.3"),   # 30% state
            health_insurance=pay_run_employee.total_deductions,
            total_deductions=pay_run_employee.total_deductions + pay_run_employee.total_taxes,
            net_pay=pay_run_employee.net_pay,
            regular_hours=pay_run_employee.regular_hours,
            overtime_hours=pay_run_employee.overtime_hours
        )
        
        self.db.add(payslip)
        return payslip
    
    # Payslip Management
    def get_payslips(
        """Get Payslips."""
        self,
        employee_id: Optional[str] = None,
        pay_run_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Payslip]:
        """Get Payslips."""
        """Get payslips with optional filtering."""
        
        query = self.db.query(Payslip)
        
        if employee_id:
            query = query.filter(Payslip.employee_id == employee_id)
        if pay_run_id:
            query = query.filter(Payslip.pay_run_id == pay_run_id)
        
        return query.order_by(desc(Payslip.created_at)).limit(limit).all()
    
    def get_payslip(self, payslip_id: str) -> Optional[Payslip]:
        """Get Payslip."""
        """Get payslip by ID."""
        return self.db.query(Payslip).filter(Payslip.id == payslip_id).first()
    
    # Payroll Items Management
    def create_payroll_item(
        """Create Payroll Item."""
        self,
        name: str,
        code: str,
        item_type: str,
        **kwargs
    ) -> PayrollItem:
        """Create Payroll Item."""
        """Create a payroll item."""
        
        item = PayrollItem(
            name=name,
            code=code,
            item_type=item_type,
            **kwargs
        )
        
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        
        return item
    
    def get_payroll_items(self, item_type: Optional[str] = None) -> List[PayrollItem]:
        """Get Payroll Items."""
        """Get payroll items with optional filtering."""
        
        query = self.db.query(PayrollItem).filter(PayrollItem.is_active == True)
        
        if item_type:
            query = query.filter(PayrollItem.item_type == item_type)
        
        return query.order_by(PayrollItem.name).all()
    
    # Analytics and Reporting
    def get_payroll_summary(
        """Get Payroll Summary."""
        self,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """Get Payroll Summary."""
        """Get payroll summary for a period."""
        
        pay_runs = self.db.query(PayRun).filter(
            PayRun.pay_period_start >= start_date,
            PayRun.pay_period_end <= end_date,
            PayRun.status.in_(["approved", "paid"])
        ).all()
        
        total_gross = sum(pr.total_gross_pay for pr in pay_runs)
        total_net = sum(pr.total_net_pay for pr in pay_runs)
        total_taxes = sum(pr.total_taxes for pr in pay_runs)
        total_deductions = sum(pr.total_deductions for pr in pay_runs)
        
        # Department breakdown
        dept_summary = {}
        for pay_run in pay_runs:
            for emp in pay_run.employees:
                dept = emp.employee.department
                if dept not in dept_summary:
                    dept_summary[dept] = {
                        "employee_count": 0,
                        "total_gross": Decimal("0.00"),
                        "total_net": Decimal("0.00")
                    }
                dept_summary[dept]["employee_count"] += 1
                dept_summary[dept]["total_gross"] += emp.gross_pay
                dept_summary[dept]["total_net"] += emp.net_pay
        
        return {
            "period": {
                "start_date": start_date,
                "end_date": end_date
            },
            "summary": {
                "pay_runs_count": len(pay_runs),
                "total_gross_pay": total_gross,
                "total_net_pay": total_net,
                "total_taxes": total_taxes,
                "total_deductions": total_deductions
            },
            "by_department": dept_summary
        }