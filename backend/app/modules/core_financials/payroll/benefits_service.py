from typing import Dict, List, Optional
from decimal import Decimal
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from .models import Employee, BenefitPlan, EmployeeBenefit, PayrollRun
from .schemas import BenefitCalculationRequest, BenefitCalculationResult

class BenefitsService:
    """Service for employee benefits integration and calculations"""
    
    async def calculate_benefit_deductions(
        self,
        db: AsyncSession,
        employee_id: int,
        gross_pay: Decimal,
        pay_period: date
    ) -> BenefitCalculationResult:
        """Calculate all benefit deductions for an employee"""
        
        # Get employee benefits
        result = await db.execute(
            select(EmployeeBenefit)
            .where(
                and_(
                    EmployeeBenefit.employee_id == employee_id,
                    EmployeeBenefit.is_active == True,
                    EmployeeBenefit.effective_date <= pay_period
                )
            )
        )
        employee_benefits = result.scalars().all()
        
        total_deductions = Decimal('0')
        total_employer_contributions = Decimal('0')
        benefit_details = []
        
        for emp_benefit in employee_benefits:
            # Get benefit plan details
            plan_result = await db.execute(
                select(BenefitPlan).where(BenefitPlan.id == emp_benefit.benefit_plan_id)
            )
            plan = plan_result.scalar_one_or_none()
            
            if not plan:
                continue
            
            # Calculate deduction based on benefit type
            deduction_amount, employer_contribution = self._calculate_benefit_amount(
                plan, emp_benefit, gross_pay
            )
            
            total_deductions += deduction_amount
            total_employer_contributions += employer_contribution
            
            benefit_details.append({
                'benefit_name': plan.name,
                'benefit_type': plan.benefit_type,
                'employee_deduction': float(deduction_amount),
                'employer_contribution': float(employer_contribution),
                'coverage_level': emp_benefit.coverage_level
            })
        
        return BenefitCalculationResult(
            employee_id=employee_id,
            total_deductions=total_deductions,
            total_employer_contributions=total_employer_contributions,
            benefit_details=benefit_details
        )
    
    def _calculate_benefit_amount(
        self,
        plan: 'BenefitPlan',
        employee_benefit: 'EmployeeBenefit',
        gross_pay: Decimal
    ) -> tuple[Decimal, Decimal]:
        """Calculate benefit deduction and employer contribution"""
        
        if plan.benefit_type == 'health_insurance':
            return self._calculate_health_insurance(plan, employee_benefit, gross_pay)
        elif plan.benefit_type == 'dental_insurance':
            return self._calculate_dental_insurance(plan, employee_benefit)
        elif plan.benefit_type == 'vision_insurance':
            return self._calculate_vision_insurance(plan, employee_benefit)
        elif plan.benefit_type == '401k':
            return self._calculate_401k(plan, employee_benefit, gross_pay)
        elif plan.benefit_type == 'life_insurance':
            return self._calculate_life_insurance(plan, employee_benefit, gross_pay)
        elif plan.benefit_type == 'disability_insurance':
            return self._calculate_disability_insurance(plan, employee_benefit, gross_pay)
        elif plan.benefit_type == 'hsa':
            return self._calculate_hsa(plan, employee_benefit, gross_pay)
        elif plan.benefit_type == 'fsa':
            return self._calculate_fsa(plan, employee_benefit, gross_pay)
        else:
            return Decimal('0'), Decimal('0')
    
    def _calculate_health_insurance(
        self,
        plan: 'BenefitPlan',
        employee_benefit: 'EmployeeBenefit',
        gross_pay: Decimal
    ) -> tuple[Decimal, Decimal]:
        """Calculate health insurance premiums"""
        
        # Premium rates by coverage level
        premium_rates = {
            'employee_only': plan.employee_cost or Decimal('200'),
            'employee_spouse': plan.employee_cost or Decimal('400'),
            'employee_children': plan.employee_cost or Decimal('350'),
            'family': plan.employee_cost or Decimal('600')
        }
        
        total_premium = premium_rates.get(employee_benefit.coverage_level, Decimal('200'))
        
        # Calculate employee and employer portions
        if plan.employer_contribution_type == 'percentage':
            employer_percentage = plan.employer_contribution_amount or Decimal('0.8')
            employer_contribution = total_premium * employer_percentage
            employee_deduction = total_premium - employer_contribution
        else:  # fixed amount
            employer_contribution = plan.employer_contribution_amount or Decimal('160')
            employee_deduction = max(Decimal('0'), total_premium - employer_contribution)
        
        return employee_deduction, employer_contribution
    
    def _calculate_dental_insurance(
        self,
        plan: 'BenefitPlan',
        employee_benefit: 'EmployeeBenefit'
    ) -> tuple[Decimal, Decimal]:
        """Calculate dental insurance premiums"""
        
        premium_rates = {
            'employee_only': Decimal('25'),
            'employee_spouse': Decimal('50'),
            'employee_children': Decimal('45'),
            'family': Decimal('75')
        }
        
        total_premium = premium_rates.get(employee_benefit.coverage_level, Decimal('25'))
        
        # Typically employer pays 100% of dental
        employer_contribution = total_premium
        employee_deduction = Decimal('0')
        
        return employee_deduction, employer_contribution
    
    def _calculate_vision_insurance(
        self,
        plan: 'BenefitPlan',
        employee_benefit: 'EmployeeBenefit'
    ) -> tuple[Decimal, Decimal]:
        """Calculate vision insurance premiums"""
        
        premium_rates = {
            'employee_only': Decimal('10'),
            'employee_spouse': Decimal('20'),
            'employee_children': Decimal('18'),
            'family': Decimal('30')
        }
        
        total_premium = premium_rates.get(employee_benefit.coverage_level, Decimal('10'))
        
        # Typically employer pays 100% of vision
        employer_contribution = total_premium
        employee_deduction = Decimal('0')
        
        return employee_deduction, employer_contribution
    
    def _calculate_401k(
        self,
        plan: 'BenefitPlan',
        employee_benefit: 'EmployeeBenefit',
        gross_pay: Decimal
    ) -> tuple[Decimal, Decimal]:
        """Calculate 401k contributions"""
        
        # Employee contribution
        contribution_rate = employee_benefit.employee_contribution_rate or Decimal('0.06')
        employee_contribution = gross_pay * contribution_rate
        
        # Apply annual limit (2023 limit: $22,500)
        annual_limit = Decimal('22500')
        # In production, would check YTD contributions
        employee_contribution = min(employee_contribution, annual_limit / 26)  # Bi-weekly
        
        # Employer match
        match_rate = plan.employer_contribution_amount or Decimal('0.03')
        employer_match = min(employee_contribution, gross_pay * match_rate)
        
        return employee_contribution, employer_match
    
    def _calculate_life_insurance(
        self,
        plan: 'BenefitPlan',
        employee_benefit: 'EmployeeBenefit',
        gross_pay: Decimal
    ) -> tuple[Decimal, Decimal]:
        """Calculate life insurance premiums"""
        
        # Basic life insurance (typically 1x salary) is usually employer-paid
        # Additional coverage is employee-paid
        
        coverage_amount = employee_benefit.coverage_amount or (gross_pay * 26)  # Annual salary
        
        # Rate per $1000 of coverage (varies by age)
        rate_per_1000 = Decimal('0.50')  # Simplified rate
        
        monthly_premium = (coverage_amount / 1000) * rate_per_1000
        
        # Basic coverage (up to $50,000) is employer-paid
        basic_coverage = min(coverage_amount, Decimal('50000'))
        additional_coverage = max(Decimal('0'), coverage_amount - basic_coverage)
        
        employer_premium = (basic_coverage / 1000) * rate_per_1000
        employee_premium = (additional_coverage / 1000) * rate_per_1000
        
        return employee_premium, employer_premium
    
    def _calculate_disability_insurance(
        self,
        plan: 'BenefitPlan',
        employee_benefit: 'EmployeeBenefit',
        gross_pay: Decimal
    ) -> tuple[Decimal, Decimal]:
        """Calculate disability insurance premiums"""
        
        # Short-term disability: typically 0.5% of salary
        # Long-term disability: typically 0.3% of salary
        
        annual_salary = gross_pay * 26  # Bi-weekly to annual
        
        if plan.name.lower().find('short') != -1:
            rate = Decimal('0.005')
        else:  # Long-term
            rate = Decimal('0.003')
        
        monthly_premium = (annual_salary * rate) / 12
        
        # Employer typically pays 100%
        return Decimal('0'), monthly_premium
    
    def _calculate_hsa(
        self,
        plan: 'BenefitPlan',
        employee_benefit: 'EmployeeBenefit',
        gross_pay: Decimal
    ) -> tuple[Decimal, Decimal]:
        """Calculate Health Savings Account contributions"""
        
        # Employee contribution
        contribution_amount = employee_benefit.contribution_amount or Decimal('100')
        
        # Apply annual limits (2023: $3,650 individual, $7,300 family)
        annual_limit = Decimal('3650') if employee_benefit.coverage_level == 'employee_only' else Decimal('7300')
        max_per_period = annual_limit / 26  # Bi-weekly
        
        employee_contribution = min(contribution_amount, max_per_period)
        
        # Employer contribution (if any)
        employer_contribution = plan.employer_contribution_amount or Decimal('0')
        
        return employee_contribution, employer_contribution
    
    def _calculate_fsa(
        self,
        plan: 'BenefitPlan',
        employee_benefit: 'EmployeeBenefit',
        gross_pay: Decimal
    ) -> tuple[Decimal, Decimal]:
        """Calculate Flexible Spending Account contributions"""
        
        # Employee contribution
        contribution_amount = employee_benefit.contribution_amount or Decimal('75')
        
        # Apply annual limits (2023: $3,050 for healthcare FSA)
        annual_limit = Decimal('3050')
        max_per_period = annual_limit / 26  # Bi-weekly
        
        employee_contribution = min(contribution_amount, max_per_period)
        
        # FSA is employee-funded
        return employee_contribution, Decimal('0')
    
    async def get_benefit_enrollment_summary(
        self,
        db: AsyncSession,
        company_id: int
    ) -> Dict[str, any]:
        """Get benefit enrollment summary for company"""
        
        # Get all active employees
        employees_result = await db.execute(
            select(Employee).where(
                and_(Employee.company_id == company_id, Employee.is_active == True)
            )
        )
        total_employees = len(employees_result.scalars().all())
        
        # Get benefit enrollments
        enrollments_result = await db.execute(
            select(EmployeeBenefit, BenefitPlan)
            .join(BenefitPlan)
            .join(Employee)
            .where(
                and_(
                    Employee.company_id == company_id,
                    EmployeeBenefit.is_active == True
                )
            )
        )
        
        enrollments = enrollments_result.all()
        
        # Summarize by benefit type
        benefit_summary = {}
        for enrollment, plan in enrollments:
            benefit_type = plan.benefit_type
            
            if benefit_type not in benefit_summary:
                benefit_summary[benefit_type] = {
                    'enrolled_count': 0,
                    'enrollment_rate': 0,
                    'total_employee_cost': Decimal('0'),
                    'total_employer_cost': Decimal('0')
                }
            
            benefit_summary[benefit_type]['enrolled_count'] += 1
        
        # Calculate enrollment rates
        for benefit_type in benefit_summary:
            benefit_summary[benefit_type]['enrollment_rate'] = (
                benefit_summary[benefit_type]['enrolled_count'] / total_employees * 100
                if total_employees > 0 else 0
            )
        
        return {
            'total_employees': total_employees,
            'benefit_summary': benefit_summary
        }