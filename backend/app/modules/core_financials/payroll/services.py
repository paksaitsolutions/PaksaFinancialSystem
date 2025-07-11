"""
Payroll service layer for business logic.
"""
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.services.base import BaseService
from app.modules.core_financials.payroll.models import Employee, PayrollRecord, PayrollDeduction
from app.modules.core_financials.payroll.schemas import (
    EmployeeCreate, EmployeeUpdate, PayrollRecordCreate
)

class EmployeeService(BaseService[Employee, EmployeeCreate, EmployeeUpdate]):
    def __init__(self):
        super().__init__(Employee)

    async def get_by_employee_id(self, db: AsyncSession, employee_id: str) -> Optional[Employee]:
        result = await db.execute(
            select(Employee).where(Employee.employee_id == employee_id)
        )
        return result.scalar_one_or_none()

    async def get_active_employees(self, db: AsyncSession) -> List[Employee]:
        result = await db.execute(
            select(Employee)
            .where(Employee.is_active == True)
            .order_by(Employee.last_name, Employee.first_name)
        )
        return result.scalars().all()

class PayrollService(BaseService[PayrollRecord, PayrollRecordCreate, None]):
    def __init__(self):
        super().__init__(PayrollRecord)

    async def create_payroll_record(
        self, db: AsyncSession, *, payroll_data: PayrollRecordCreate
    ) -> PayrollRecord:
        # Calculate total deductions
        total_deductions = sum(deduction.amount for deduction in payroll_data.deductions)
        net_pay = payroll_data.gross_pay - total_deductions

        # Create payroll record
        payroll_record = PayrollRecord(
            employee_id=payroll_data.employee_id,
            pay_period_start=payroll_data.pay_period_start,
            pay_period_end=payroll_data.pay_period_end,
            pay_date=payroll_data.pay_date,
            gross_pay=payroll_data.gross_pay,
            total_deductions=total_deductions,
            net_pay=net_pay
        )
        
        db.add(payroll_record)
        await db.flush()

        # Create deduction records
        for deduction_data in payroll_data.deductions:
            deduction = PayrollDeduction(
                payroll_record_id=payroll_record.id,
                deduction_type=deduction_data.deduction_type,
                amount=deduction_data.amount,
                description=deduction_data.description
            )
            db.add(deduction)

        await db.commit()
        await db.refresh(payroll_record)
        return payroll_record

    async def get_payroll_records_by_employee(
        self, db: AsyncSession, employee_id: int
    ) -> List[PayrollRecord]:
        result = await db.execute(
            select(PayrollRecord)
            .options(selectinload(PayrollRecord.deductions))
            .where(PayrollRecord.employee_id == employee_id)
            .order_by(PayrollRecord.pay_date.desc())
        )
        return result.scalars().all()

    async def calculate_payroll_taxes(
        self, gross_pay: Decimal, employee_id: int
    ) -> List[dict]:
        """
        Simplified tax calculation - in production this would be much more complex
        and would integrate with tax tables and regulations.
        """
        taxes = []
        
        # Federal income tax (simplified)
        federal_tax = gross_pay * Decimal('0.12')
        taxes.append({
            'deduction_type': 'federal_income_tax',
            'amount': federal_tax,
            'description': 'Federal Income Tax'
        })
        
        # Social Security tax
        ss_tax = gross_pay * Decimal('0.062')
        taxes.append({
            'deduction_type': 'social_security',
            'amount': ss_tax,
            'description': 'Social Security Tax'
        })
        
        # Medicare tax
        medicare_tax = gross_pay * Decimal('0.0145')
        taxes.append({
            'deduction_type': 'medicare',
            'amount': medicare_tax,
            'description': 'Medicare Tax'
        })
        
        return taxes