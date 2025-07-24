"""
Payroll reporting service for the Payroll module.
"""
from typing import List, Optional, Dict, Any
from datetime import date
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, extract

from app.models.employee import Employee
from app.models.payslip import Payslip
from app.models.pay_period import PayPeriod
from app.models.benefits import EmployeeBenefit, BenefitPlan
from app.modules.core_financials.payroll.schemas.payroll_reporting import (
    PayrollReportRequest, PayrollSummaryReport, EmployeeEarningsReport,
    TaxLiabilityReport, BenefitsReport, DepartmentCostsReport, YearEndSummary
)


class PayrollReportingService:
    """Service for generating payroll reports."""
    
    @staticmethod
    def generate_payroll_summary_report(
        db: Session,
        start_date: date,
        end_date: date,
        department: Optional[str] = None
    ) -> PayrollSummaryReport:
        """Generate payroll summary report."""
        
        # Base query for payslips in date range
        query = db.query(Payslip, Employee, PayPeriod).join(
            Employee, Payslip.employee_id == Employee.id
        ).join(
            PayPeriod, Payslip.pay_period_id == PayPeriod.id
        ).filter(
            and_(
                PayPeriod.start_date >= start_date,
                PayPeriod.end_date <= end_date
            )
        )
        
        if department:
            query = query.filter(Employee.department == department)
        
        payslips = query.all()
        
        # Calculate totals
        total_employees = len(set(p.employee_id for p, e, pp in payslips))
        total_gross = sum(p.gross_pay for p, e, pp in payslips)
        total_net = sum(p.net_pay for p, e, pp in payslips)
        total_taxes = sum(p.tax_deductions for p, e, pp in payslips)
        
        # Calculate benefits
        benefits_query = db.query(func.sum(EmployeeBenefit.employee_contribution)).join(
            Employee, EmployeeBenefit.employee_id == Employee.id
        ).filter(
            and_(
                EmployeeBenefit.effective_date >= start_date,
                EmployeeBenefit.effective_date <= end_date,
                EmployeeBenefit.is_active == True
            )
        )
        
        if department:
            benefits_query = benefits_query.filter(Employee.department == department)
        
        total_benefits = benefits_query.scalar() or Decimal("0.00")
        
        # Group by department
        by_department = {}
        dept_data = {}
        
        for payslip, employee, pay_period in payslips:
            dept = employee.department
            if dept not in dept_data:
                dept_data[dept] = {
                    'employees': set(),
                    'gross_pay': Decimal("0.00"),
                    'net_pay': Decimal("0.00"),
                    'taxes': Decimal("0.00")
                }
            
            dept_data[dept]['employees'].add(employee.id)
            dept_data[dept]['gross_pay'] += payslip.gross_pay
            dept_data[dept]['net_pay'] += payslip.net_pay
            dept_data[dept]['taxes'] += payslip.tax_deductions
        
        for dept, data in dept_data.items():
            by_department[dept] = {
                'employee_count': len(data['employees']),
                'gross_pay': data['gross_pay'],
                'net_pay': data['net_pay'],
                'taxes': data['taxes']
            }
        
        return PayrollSummaryReport(
            period_start=start_date,
            period_end=end_date,
            total_employees=total_employees,
            total_gross_pay=total_gross,
            total_net_pay=total_net,
            total_taxes=total_taxes,
            total_benefits=total_benefits,
            by_department=by_department
        )
    
    @staticmethod
    def generate_employee_earnings_report(
        db: Session,
        start_date: date,
        end_date: date,
        employee_ids: Optional[List[str]] = None
    ) -> List[EmployeeEarningsReport]:
        """Generate employee earnings report."""
        
        query = db.query(Payslip, Employee, PayPeriod).join(
            Employee, Payslip.employee_id == Employee.id
        ).join(
            PayPeriod, Payslip.pay_period_id == PayPeriod.id
        ).filter(
            and_(
                PayPeriod.start_date >= start_date,
                PayPeriod.end_date <= end_date
            )
        )
        
        if employee_ids:
            query = query.filter(Employee.id.in_(employee_ids))
        
        payslips = query.all()
        
        # Group by employee
        employee_data = {}
        for payslip, employee, pay_period in payslips:
            emp_id = str(employee.id)
            if emp_id not in employee_data:
                employee_data[emp_id] = {
                    'employee': employee,
                    'total_gross': Decimal("0.00"),
                    'total_net': Decimal("0.00"),
                    'total_taxes': Decimal("0.00"),
                    'pay_periods': []
                }
            
            employee_data[emp_id]['total_gross'] += payslip.gross_pay
            employee_data[emp_id]['total_net'] += payslip.net_pay
            employee_data[emp_id]['total_taxes'] += payslip.tax_deductions
            
            employee_data[emp_id]['pay_periods'].append({
                'period_start': pay_period.start_date,
                'period_end': pay_period.end_date,
                'gross_pay': payslip.gross_pay,
                'net_pay': payslip.net_pay,
                'taxes': payslip.tax_deductions
            })
        
        # Get benefits for each employee
        reports = []
        for emp_id, data in employee_data.items():
            employee = data['employee']
            
            # Calculate benefits
            benefits_total = db.query(func.sum(EmployeeBenefit.employee_contribution)).filter(
                and_(
                    EmployeeBenefit.employee_id == employee.id,
                    EmployeeBenefit.effective_date >= start_date,
                    EmployeeBenefit.effective_date <= end_date,
                    EmployeeBenefit.is_active == True
                )
            ).scalar() or Decimal("0.00")
            
            reports.append(EmployeeEarningsReport(
                employee_id=employee.id,
                employee_name=employee.full_name,
                employee_code=employee.employee_id,
                department=employee.department,
                total_gross=data['total_gross'],
                total_net=data['total_net'],
                total_taxes=data['total_taxes'],
                total_benefits=benefits_total,
                pay_periods=data['pay_periods']
            ))
        
        return reports
    
    @staticmethod
    def generate_tax_liability_report(
        db: Session,
        start_date: date,
        end_date: date
    ) -> TaxLiabilityReport:
        """Generate tax liability report."""
        
        payslips = db.query(Payslip, Employee, PayPeriod).join(
            Employee, Payslip.employee_id == Employee.id
        ).join(
            PayPeriod, Payslip.pay_period_id == PayPeriod.id
        ).filter(
            and_(
                PayPeriod.start_date >= start_date,
                PayPeriod.end_date <= end_date
            )
        ).all()
        
        # Calculate tax totals (simplified - would need actual tax breakdown)
        total_taxes = sum(p.tax_deductions for p, e, pp in payslips)
        
        # Estimate tax breakdown (in real implementation, this would come from tax calculation)
        federal_tax = total_taxes * Decimal("0.60")  # ~60% federal
        state_tax = total_taxes * Decimal("0.15")    # ~15% state
        social_security = total_taxes * Decimal("0.15")  # ~15% SS
        medicare = total_taxes * Decimal("0.08")     # ~8% Medicare
        unemployment = total_taxes * Decimal("0.02") # ~2% unemployment
        
        # By employee breakdown
        by_employee = []
        employee_taxes = {}
        
        for payslip, employee, pay_period in payslips:
            emp_id = str(employee.id)
            if emp_id not in employee_taxes:
                employee_taxes[emp_id] = {
                    'employee_name': employee.full_name,
                    'employee_code': employee.employee_id,
                    'total_taxes': Decimal("0.00")
                }
            employee_taxes[emp_id]['total_taxes'] += payslip.tax_deductions
        
        for emp_data in employee_taxes.values():
            by_employee.append(emp_data)
        
        return TaxLiabilityReport(
            period_start=start_date,
            period_end=end_date,
            federal_income_tax=federal_tax,
            state_income_tax=state_tax,
            social_security_tax=social_security,
            medicare_tax=medicare,
            unemployment_tax=unemployment,
            total_tax_liability=total_taxes,
            by_employee=by_employee
        )
    
    @staticmethod
    def generate_benefits_report(
        db: Session,
        start_date: date,
        end_date: date
    ) -> BenefitsReport:
        """Generate benefits report."""
        
        benefits = db.query(EmployeeBenefit, Employee, BenefitPlan).join(
            Employee, EmployeeBenefit.employee_id == Employee.id
        ).join(
            BenefitPlan, EmployeeBenefit.benefit_plan_id == BenefitPlan.id
        ).filter(
            and_(
                EmployeeBenefit.effective_date >= start_date,
                EmployeeBenefit.effective_date <= end_date,
                EmployeeBenefit.is_active == True
            )
        ).all()
        
        total_employee_contrib = sum(b.employee_contribution for b, e, p in benefits)
        total_employer_contrib = sum(b.employer_contribution for b, e, p in benefits)
        
        # Group by benefit type
        by_benefit_type = {}
        benefit_type_data = {}
        
        for benefit, employee, plan in benefits:
            benefit_type = plan.benefit_type
            if benefit_type not in benefit_type_data:
                benefit_type_data[benefit_type] = {
                    'employee_contributions': Decimal("0.00"),
                    'employer_contributions': Decimal("0.00"),
                    'enrollment_count': 0
                }
            
            benefit_type_data[benefit_type]['employee_contributions'] += benefit.employee_contribution
            benefit_type_data[benefit_type]['employer_contributions'] += benefit.employer_contribution
            benefit_type_data[benefit_type]['enrollment_count'] += 1
        
        by_benefit_type = benefit_type_data
        
        # By employee
        by_employee = []
        employee_benefits = {}
        
        for benefit, employee, plan in benefits:
            emp_id = str(employee.id)
            if emp_id not in employee_benefits:
                employee_benefits[emp_id] = {
                    'employee_name': employee.full_name,
                    'employee_code': employee.employee_id,
                    'total_employee_contribution': Decimal("0.00"),
                    'total_employer_contribution': Decimal("0.00"),
                    'benefits': []
                }
            
            employee_benefits[emp_id]['total_employee_contribution'] += benefit.employee_contribution
            employee_benefits[emp_id]['total_employer_contribution'] += benefit.employer_contribution
            employee_benefits[emp_id]['benefits'].append({
                'plan_name': plan.name,
                'benefit_type': plan.benefit_type,
                'employee_contribution': benefit.employee_contribution,
                'employer_contribution': benefit.employer_contribution
            })
        
        by_employee = list(employee_benefits.values())
        
        return BenefitsReport(
            period_start=start_date,
            period_end=end_date,
            total_employee_contributions=total_employee_contrib,
            total_employer_contributions=total_employer_contrib,
            by_benefit_type=by_benefit_type,
            by_employee=by_employee
        )
    
    @staticmethod
    def generate_department_costs_report(
        db: Session,
        start_date: date,
        end_date: date
    ) -> DepartmentCostsReport:
        """Generate department costs report."""
        
        payslips = db.query(Payslip, Employee, PayPeriod).join(
            Employee, Payslip.employee_id == Employee.id
        ).join(
            PayPeriod, Payslip.pay_period_id == PayPeriod.id
        ).filter(
            and_(
                PayPeriod.start_date >= start_date,
                PayPeriod.end_date <= end_date
            )
        ).all()
        
        # Group by department
        dept_costs = {}
        
        for payslip, employee, pay_period in payslips:
            dept = employee.department
            if dept not in dept_costs:
                dept_costs[dept] = {
                    'department': dept,
                    'employee_count': set(),
                    'gross_pay': Decimal("0.00"),
                    'taxes': Decimal("0.00"),
                    'benefits': Decimal("0.00")
                }
            
            dept_costs[dept]['employee_count'].add(employee.id)
            dept_costs[dept]['gross_pay'] += payslip.gross_pay
            dept_costs[dept]['taxes'] += payslip.tax_deductions
        
        # Add benefits costs by department
        for dept in dept_costs.keys():
            benefits_cost = db.query(func.sum(EmployeeBenefit.employer_contribution)).join(
                Employee, EmployeeBenefit.employee_id == Employee.id
            ).filter(
                and_(
                    Employee.department == dept,
                    EmployeeBenefit.effective_date >= start_date,
                    EmployeeBenefit.effective_date <= end_date,
                    EmployeeBenefit.is_active == True
                )
            ).scalar() or Decimal("0.00")
            
            dept_costs[dept]['benefits'] = benefits_cost
        
        # Convert to list format
        departments = []
        total_cost = Decimal("0.00")
        
        for dept_data in dept_costs.values():
            dept_total = dept_data['gross_pay'] + dept_data['taxes'] + dept_data['benefits']
            total_cost += dept_total
            
            departments.append({
                'department': dept_data['department'],
                'employee_count': len(dept_data['employee_count']),
                'gross_pay': dept_data['gross_pay'],
                'taxes': dept_data['taxes'],
                'benefits': dept_data['benefits'],
                'total_cost': dept_total
            })
        
        return DepartmentCostsReport(
            period_start=start_date,
            period_end=end_date,
            departments=departments,
            total_cost=total_cost
        )
    
    @staticmethod
    def generate_year_end_summary(
        db: Session,
        year: int
    ) -> YearEndSummary:
        """Generate year-end summary report."""
        
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        
        payslips = db.query(Payslip, Employee, PayPeriod).join(
            Employee, Payslip.employee_id == Employee.id
        ).join(
            PayPeriod, Payslip.pay_period_id == PayPeriod.id
        ).filter(
            and_(
                PayPeriod.start_date >= start_date,
                PayPeriod.end_date <= end_date
            )
        ).all()
        
        total_employees = len(set(p.employee_id for p, e, pp in payslips))
        total_gross = sum(p.gross_pay for p, e, pp in payslips)
        total_net = sum(p.net_pay for p, e, pp in payslips)
        total_taxes = sum(p.tax_deductions for p, e, pp in payslips)
        
        # Calculate benefits
        total_benefits = db.query(func.sum(EmployeeBenefit.employee_contribution)).filter(
            and_(
                extract('year', EmployeeBenefit.effective_date) == year,
                EmployeeBenefit.is_active == True
            )
        ).scalar() or Decimal("0.00")
        
        # Quarterly breakdown
        quarterly_breakdown = []
        for quarter in range(1, 5):
            q_start = date(year, (quarter-1)*3 + 1, 1)
            if quarter == 4:
                q_end = date(year, 12, 31)
            else:
                q_end = date(year, quarter*3, 28)  # Simplified
            
            q_payslips = [p for p, e, pp in payslips if q_start <= pp.start_date <= q_end]
            
            quarterly_breakdown.append({
                'quarter': quarter,
                'gross_pay': sum(p.gross_pay for p in q_payslips),
                'net_pay': sum(p.net_pay for p in q_payslips),
                'taxes': sum(p.tax_deductions for p in q_payslips)
            })
        
        # Top earners
        employee_earnings = {}
        for payslip, employee, pay_period in payslips:
            emp_id = str(employee.id)
            if emp_id not in employee_earnings:
                employee_earnings[emp_id] = {
                    'employee_name': employee.full_name,
                    'employee_code': employee.employee_id,
                    'department': employee.department,
                    'total_gross': Decimal("0.00")
                }
            employee_earnings[emp_id]['total_gross'] += payslip.gross_pay
        
        top_earners = sorted(
            employee_earnings.values(),
            key=lambda x: x['total_gross'],
            reverse=True
        )[:10]  # Top 10
        
        return YearEndSummary(
            year=year,
            total_employees=total_employees,
            total_gross_pay=total_gross,
            total_net_pay=total_net,
            total_taxes=total_taxes,
            total_benefits=total_benefits,
            quarterly_breakdown=quarterly_breakdown,
            top_earners=top_earners
        )