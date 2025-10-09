"""
Initialize payroll data with sample employees and payroll items.
"""
from datetime import date
from decimal import Decimal
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.payroll_models import Employee, PayrollItem
from app.services.payroll_service import PayrollService

def init_payroll_data():
    """Initialize payroll data with sample employees and items."""
    db = SessionLocal()
    try:
        # Check if data already exists
        existing_employees = db.query(Employee).count()
        if existing_employees > 0:
            print("Payroll data already exists, skipping initialization")
            return

        payroll_service = PayrollService(db)

        # Create sample employees
        sample_employees = [
            {
                "employee_id": "EMP001",
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@company.com",
                "phone_number": "+1-555-0101",
                "department": "Engineering",
                "job_title": "Software Engineer",
                "employment_type": "full_time",
                "hire_date": date(2023, 1, 15),
                "base_salary": Decimal("75000.00"),
                "pay_frequency": "monthly"
            },
            {
                "employee_id": "EMP002",
                "first_name": "Jane",
                "last_name": "Smith",
                "email": "jane.smith@company.com",
                "phone_number": "+1-555-0102",
                "department": "Marketing",
                "job_title": "Marketing Manager",
                "employment_type": "full_time",
                "hire_date": date(2023, 2, 1),
                "base_salary": Decimal("65000.00"),
                "pay_frequency": "monthly"
            },
            {
                "employee_id": "EMP003",
                "first_name": "Mike",
                "last_name": "Johnson",
                "email": "mike.johnson@company.com",
                "phone_number": "+1-555-0103",
                "department": "Finance",
                "job_title": "Financial Analyst",
                "employment_type": "full_time",
                "hire_date": date(2023, 3, 10),
                "base_salary": Decimal("60000.00"),
                "pay_frequency": "monthly"
            },
            {
                "employee_id": "EMP004",
                "first_name": "Sarah",
                "last_name": "Wilson",
                "email": "sarah.wilson@company.com",
                "phone_number": "+1-555-0104",
                "department": "HR",
                "job_title": "HR Specialist",
                "employment_type": "full_time",
                "hire_date": date(2023, 4, 5),
                "base_salary": Decimal("55000.00"),
                "pay_frequency": "monthly"
            },
            {
                "employee_id": "EMP005",
                "first_name": "David",
                "last_name": "Brown",
                "email": "david.brown@company.com",
                "phone_number": "+1-555-0105",
                "department": "Operations",
                "job_title": "Operations Manager",
                "employment_type": "full_time",
                "hire_date": date(2023, 5, 20),
                "base_salary": Decimal("70000.00"),
                "pay_frequency": "monthly"
            }
        ]

        for emp_data in sample_employees:
            employee = payroll_service.create_employee(**emp_data)
            print(f"Created employee: {employee.full_name} ({employee.employee_id})")

        # Create sample payroll items
        sample_payroll_items = [
            {
                "name": "Health Insurance",
                "code": "HEALTH_INS",
                "item_type": "deduction",
                "category": "Benefits",
                "is_taxable": False,
                "is_pre_tax": True,
                "calculation_method": "fixed",
                "default_amount": Decimal("200.00"),
                "expense_account": "5100",
                "liability_account": "2100"
            },
            {
                "name": "Dental Insurance",
                "code": "DENTAL_INS",
                "item_type": "deduction",
                "category": "Benefits",
                "is_taxable": False,
                "is_pre_tax": True,
                "calculation_method": "fixed",
                "default_amount": Decimal("50.00"),
                "expense_account": "5101",
                "liability_account": "2101"
            },
            {
                "name": "401(k) Contribution",
                "code": "401K_CONTRIB",
                "item_type": "deduction",
                "category": "Retirement",
                "is_taxable": False,
                "is_pre_tax": True,
                "calculation_method": "percentage",
                "percentage": Decimal("0.05"),  # 5%
                "expense_account": "5200",
                "liability_account": "2200"
            },
            {
                "name": "Federal Income Tax",
                "code": "FED_TAX",
                "item_type": "tax",
                "category": "Taxes",
                "is_taxable": False,
                "calculation_method": "percentage",
                "percentage": Decimal("0.15"),  # 15%
                "liability_account": "2300"
            },
            {
                "name": "State Income Tax",
                "code": "STATE_TAX",
                "item_type": "tax",
                "category": "Taxes",
                "is_taxable": False,
                "calculation_method": "percentage",
                "percentage": Decimal("0.05"),  # 5%
                "liability_account": "2301"
            },
            {
                "name": "Social Security",
                "code": "SOCIAL_SEC",
                "item_type": "tax",
                "category": "Taxes",
                "is_taxable": False,
                "calculation_method": "percentage",
                "percentage": Decimal("0.062"),  # 6.2%
                "liability_account": "2302"
            },
            {
                "name": "Medicare",
                "code": "MEDICARE",
                "item_type": "tax",
                "category": "Taxes",
                "is_taxable": False,
                "calculation_method": "percentage",
                "percentage": Decimal("0.0145"),  # 1.45%
                "liability_account": "2303"
            },
            {
                "name": "Performance Bonus",
                "code": "PERF_BONUS",
                "item_type": "earning",
                "category": "Bonus",
                "is_taxable": True,
                "calculation_method": "fixed",
                "default_amount": Decimal("0.00"),
                "expense_account": "5300"
            },
            {
                "name": "Overtime Pay",
                "code": "OVERTIME",
                "item_type": "earning",
                "category": "Overtime",
                "is_taxable": True,
                "calculation_method": "formula",
                "expense_account": "5301"
            }
        ]

        for item_data in sample_payroll_items:
            item = payroll_service.create_payroll_item(**item_data)
            print(f"Created payroll item: {item.name} ({item.code})")

        print("Payroll data initialization completed successfully!")

    except Exception as e:
        print(f"Error initializing payroll data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_payroll_data()