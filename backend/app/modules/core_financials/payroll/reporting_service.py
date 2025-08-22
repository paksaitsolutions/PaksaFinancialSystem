from typing import Dict, List, Optional
from decimal import Decimal
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, extract
from .models import PayrollRun, Employee, TaxCalculation, PayrollItem
from .schemas import PayrollReport, QuarterlyReport, YearEndReport

class PayrollReportingService:
    """Service for comprehensive payroll reporting"""
    
    async def generate_payroll_register(
        self,
        db: AsyncSession,
        payroll_run_id: int
    ) -> PayrollReport:
        """Generate detailed payroll register report"""
        
        # Get payroll run details
        run_result = await db.execute(
            select(PayrollRun).where(PayrollRun.id == payroll_run_id)
        )
        payroll_run = run_result.scalar_one_or_none()
        
        if not payroll_run:
            raise ValueError("Payroll run not found")
        
        # Get all payroll items for this run
        items_result = await db.execute(
            select(PayrollItem, Employee)
            .join(Employee)
            .where(PayrollItem.payroll_run_id == payroll_run_id)
            .order_by(Employee.last_name, Employee.first_name)
        )
        
        payroll_items = items_result.all()
        
        # Calculate totals
        total_gross = Decimal('0')
        total_deductions = Decimal('0')
        total_net = Decimal('0')
        
        employee_details = []
        
        for item, employee in payroll_items:
            # Get tax calculations
            tax_result = await db.execute(
                select(TaxCalculation).where(
                    and_(
                        TaxCalculation.payroll_run_id == payroll_run_id,
                        TaxCalculation.employee_id == employee.id
                    )
                )
            )
            tax_calc = tax_result.scalar_one_or_none()
            
            gross_pay = item.gross_pay
            total_taxes = tax_calc.total_taxes if tax_calc else Decimal('0')
            net_pay = gross_pay - total_taxes
            
            total_gross += gross_pay
            total_deductions += total_taxes
            total_net += net_pay
            
            employee_details.append({
                'employee_id': employee.id,
                'employee_name': f"{employee.first_name} {employee.last_name}",
                'employee_number': employee.employee_number,
                'department': employee.department,
                'regular_hours': float(item.regular_hours or 0),
                'overtime_hours': float(item.overtime_hours or 0),
                'regular_pay': float(item.regular_pay or 0),
                'overtime_pay': float(item.overtime_pay or 0),
                'gross_pay': float(gross_pay),
                'federal_tax': float(tax_calc.federal_income_tax if tax_calc else 0),
                'state_tax': float(tax_calc.work_state_income_tax if tax_calc else 0),
                'social_security': float(tax_calc.federal_social_security if tax_calc else 0),
                'medicare': float(tax_calc.federal_medicare if tax_calc else 0),
                'total_deductions': float(total_taxes),
                'net_pay': float(net_pay)
            })
        
        return PayrollReport(
            payroll_run_id=payroll_run_id,
            pay_period_start=payroll_run.pay_period_start,
            pay_period_end=payroll_run.pay_period_end,
            pay_date=payroll_run.pay_date,
            employee_count=len(employee_details),
            total_gross_pay=total_gross,
            total_deductions=total_deductions,
            total_net_pay=total_net,
            employee_details=employee_details
        )
    
    async def generate_quarterly_report(
        self,
        db: AsyncSession,
        company_id: int,
        year: int,
        quarter: int
    ) -> QuarterlyReport:
        """Generate quarterly tax report (941/940)"""
        
        # Determine quarter date range
        quarter_start_month = (quarter - 1) * 3 + 1
        quarter_start = date(year, quarter_start_month, 1)
        
        if quarter == 4:
            quarter_end = date(year, 12, 31)
        else:
            next_quarter_month = quarter * 3 + 1
            quarter_end = date(year, next_quarter_month, 1)
        
        # Get all payroll runs in quarter
        runs_result = await db.execute(
            select(PayrollRun).where(
                and_(
                    PayrollRun.company_id == company_id,
                    PayrollRun.pay_date >= quarter_start,
                    PayrollRun.pay_date <= quarter_end,
                    PayrollRun.status == 'completed'
                )
            )
        )
        payroll_runs = runs_result.scalars().all()
        
        run_ids = [run.id for run in payroll_runs]
        
        if not run_ids:
            return QuarterlyReport(
                company_id=company_id,
                year=year,
                quarter=quarter,
                total_wages=Decimal('0'),
                total_federal_tax=Decimal('0'),
                total_social_security_tax=Decimal('0'),
                total_medicare_tax=Decimal('0'),
                employee_count=0
            )
        
        # Get tax calculations for all runs in quarter
        tax_result = await db.execute(
            select(
                func.sum(TaxCalculation.gross_pay).label('total_wages'),
                func.sum(TaxCalculation.federal_income_tax).label('total_federal_tax'),
                func.sum(TaxCalculation.federal_social_security).label('total_social_security'),
                func.sum(TaxCalculation.federal_medicare).label('total_medicare'),
                func.count(func.distinct(TaxCalculation.employee_id)).label('employee_count')
            ).where(TaxCalculation.payroll_run_id.in_(run_ids))
        )
        
        totals = tax_result.first()
        
        # Get monthly breakdown
        monthly_breakdown = []
        for month in range(quarter_start_month, quarter_start_month + 3):
            month_start = date(year, month, 1)
            if month == 12:
                month_end = date(year, 12, 31)
            else:
                month_end = date(year, month + 1, 1)
            
            month_runs = [run for run in payroll_runs 
                         if month_start <= run.pay_date < month_end]
            month_run_ids = [run.id for run in month_runs]
            
            if month_run_ids:
                month_tax_result = await db.execute(
                    select(
                        func.sum(TaxCalculation.gross_pay).label('wages'),
                        func.sum(TaxCalculation.federal_income_tax).label('federal_tax'),
                        func.sum(TaxCalculation.federal_social_security).label('social_security'),
                        func.sum(TaxCalculation.federal_medicare).label('medicare')
                    ).where(TaxCalculation.payroll_run_id.in_(month_run_ids))
                )
                month_totals = month_tax_result.first()
                
                monthly_breakdown.append({
                    'month': month,
                    'wages': float(month_totals.wages or 0),
                    'federal_tax': float(month_totals.federal_tax or 0),
                    'social_security': float(month_totals.social_security or 0),
                    'medicare': float(month_totals.medicare or 0)
                })
            else:
                monthly_breakdown.append({
                    'month': month,
                    'wages': 0,
                    'federal_tax': 0,
                    'social_security': 0,
                    'medicare': 0
                })
        
        return QuarterlyReport(
            company_id=company_id,
            year=year,
            quarter=quarter,
            total_wages=totals.total_wages or Decimal('0'),
            total_federal_tax=totals.total_federal_tax or Decimal('0'),
            total_social_security_tax=totals.total_social_security or Decimal('0'),
            total_medicare_tax=totals.total_medicare or Decimal('0'),
            employee_count=totals.employee_count or 0,
            monthly_breakdown=monthly_breakdown
        )
    
    async def generate_year_end_report(
        self,
        db: AsyncSession,
        company_id: int,
        year: int
    ) -> YearEndReport:
        """Generate year-end W-2 summary report"""
        
        # Get all payroll runs for the year
        runs_result = await db.execute(
            select(PayrollRun).where(
                and_(
                    PayrollRun.company_id == company_id,
                    extract('year', PayrollRun.pay_date) == year,
                    PayrollRun.status == 'completed'
                )
            )
        )
        payroll_runs = runs_result.scalars().all()
        run_ids = [run.id for run in payroll_runs]
        
        if not run_ids:
            return YearEndReport(
                company_id=company_id,
                year=year,
                total_employees=0,
                total_wages=Decimal('0'),
                total_federal_tax=Decimal('0'),
                total_state_tax=Decimal('0'),
                total_social_security=Decimal('0'),
                total_medicare=Decimal('0'),
                employee_w2_data=[]
            )
        
        # Get employee W-2 data
        w2_result = await db.execute(
            select(
                Employee.id,
                Employee.first_name,
                Employee.last_name,
                Employee.employee_number,
                Employee.ssn,
                func.sum(TaxCalculation.gross_pay).label('total_wages'),
                func.sum(TaxCalculation.federal_income_tax).label('federal_tax'),
                func.sum(TaxCalculation.work_state_income_tax).label('state_tax'),
                func.sum(TaxCalculation.federal_social_security).label('social_security'),
                func.sum(TaxCalculation.federal_medicare).label('medicare')
            )
            .join(TaxCalculation)
            .where(TaxCalculation.payroll_run_id.in_(run_ids))
            .group_by(Employee.id, Employee.first_name, Employee.last_name, 
                     Employee.employee_number, Employee.ssn)
            .order_by(Employee.last_name, Employee.first_name)
        )
        
        employee_w2_data = []
        total_wages = Decimal('0')
        total_federal_tax = Decimal('0')
        total_state_tax = Decimal('0')
        total_social_security = Decimal('0')
        total_medicare = Decimal('0')
        
        for row in w2_result:
            wages = row.total_wages or Decimal('0')
            federal_tax = row.federal_tax or Decimal('0')
            state_tax = row.state_tax or Decimal('0')
            social_security = row.social_security or Decimal('0')
            medicare = row.medicare or Decimal('0')
            
            total_wages += wages
            total_federal_tax += federal_tax
            total_state_tax += state_tax
            total_social_security += social_security
            total_medicare += medicare
            
            employee_w2_data.append({
                'employee_id': row.id,
                'employee_name': f"{row.first_name} {row.last_name}",
                'employee_number': row.employee_number,
                'ssn': row.ssn,
                'wages': float(wages),
                'federal_tax': float(federal_tax),
                'state_tax': float(state_tax),
                'social_security': float(social_security),
                'medicare': float(medicare)
            })
        
        return YearEndReport(
            company_id=company_id,
            year=year,
            total_employees=len(employee_w2_data),
            total_wages=total_wages,
            total_federal_tax=total_federal_tax,
            total_state_tax=total_state_tax,
            total_social_security=total_social_security,
            total_medicare=total_medicare,
            employee_w2_data=employee_w2_data
        )
    
    async def generate_payroll_summary_by_department(
        self,
        db: AsyncSession,
        company_id: int,
        start_date: date,
        end_date: date
    ) -> Dict[str, Dict[str, float]]:
        """Generate payroll summary grouped by department"""
        
        # Get payroll runs in date range
        runs_result = await db.execute(
            select(PayrollRun).where(
                and_(
                    PayrollRun.company_id == company_id,
                    PayrollRun.pay_date >= start_date,
                    PayrollRun.pay_date <= end_date,
                    PayrollRun.status == 'completed'
                )
            )
        )
        payroll_runs = runs_result.scalars().all()
        run_ids = [run.id for run in payroll_runs]
        
        if not run_ids:
            return {}
        
        # Get department summary
        dept_result = await db.execute(
            select(
                Employee.department,
                func.count(func.distinct(Employee.id)).label('employee_count'),
                func.sum(TaxCalculation.gross_pay).label('total_gross'),
                func.sum(TaxCalculation.total_taxes).label('total_taxes'),
                func.sum(TaxCalculation.net_pay).label('total_net')
            )
            .join(TaxCalculation)
            .where(TaxCalculation.payroll_run_id.in_(run_ids))
            .group_by(Employee.department)
            .order_by(Employee.department)
        )
        
        department_summary = {}
        for row in dept_result:
            department = row.department or 'Unassigned'
            department_summary[department] = {
                'employee_count': row.employee_count,
                'total_gross': float(row.total_gross or 0),
                'total_taxes': float(row.total_taxes or 0),
                'total_net': float(row.total_net or 0),
                'average_gross': float((row.total_gross or 0) / row.employee_count) if row.employee_count > 0 else 0
            }
        
        return department_summary