from typing import Dict, List, Optional
from decimal import Decimal
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .models import Employee, PayrollRun, TaxCalculation
from .schemas import MultiStateTaxRequest, TaxCalculationResult

class MultiStateTaxService:
    """Service for multi-state tax calculations"""
    
    # State tax rates and rules (simplified - in production would be from external service)
    STATE_TAX_RATES = {
        'CA': {'rate': Decimal('0.0725'), 'standard_deduction': Decimal('4803')},
        'NY': {'rate': Decimal('0.0685'), 'standard_deduction': Decimal('8000')},
        'TX': {'rate': Decimal('0.0000'), 'standard_deduction': Decimal('0')},  # No state income tax
        'FL': {'rate': Decimal('0.0000'), 'standard_deduction': Decimal('0')},  # No state income tax
        'WA': {'rate': Decimal('0.0000'), 'standard_deduction': Decimal('0')},  # No state income tax
        'IL': {'rate': Decimal('0.0495'), 'standard_deduction': Decimal('2375')},
        'PA': {'rate': Decimal('0.0307'), 'standard_deduction': Decimal('0')},
        'OH': {'rate': Decimal('0.0399'), 'standard_deduction': Decimal('2150')},
        'GA': {'rate': Decimal('0.0575'), 'standard_deduction': Decimal('2700')},
        'NC': {'rate': Decimal('0.0525'), 'standard_deduction': Decimal('10750')}
    }
    
    # State disability insurance rates
    SDI_RATES = {
        'CA': {'rate': Decimal('0.009'), 'wage_base': Decimal('153164')},
        'NY': {'rate': Decimal('0.005'), 'wage_base': Decimal('120000')},
        'NJ': {'rate': Decimal('0.0033'), 'wage_base': Decimal('147000')},
        'RI': {'rate': Decimal('0.013'), 'wage_base': Decimal('81500')},
        'HI': {'rate': Decimal('0.005'), 'wage_base': Decimal('57800')}
    }
    
    # State unemployment rates (employer portion)
    SUI_RATES = {
        'CA': {'rate': Decimal('0.034'), 'wage_base': Decimal('7000')},
        'NY': {'rate': Decimal('0.0425'), 'wage_base': Decimal('12000')},
        'TX': {'rate': Decimal('0.0275'), 'wage_base': Decimal('9000')},
        'FL': {'rate': Decimal('0.027'), 'wage_base': Decimal('7000')},
        'IL': {'rate': Decimal('0.0325'), 'wage_base': Decimal('12960')}
    }
    
    async def calculate_multi_state_taxes(
        self,
        db: AsyncSession,
        employee_id: int,
        gross_pay: Decimal,
        work_state: str,
        residence_state: str,
        pay_period: date
    ) -> TaxCalculationResult:
        """Calculate taxes for employee working in different state than residence"""
        
        # Get employee details
        result = await db.execute(select(Employee).where(Employee.id == employee_id))
        employee = result.scalar_one_or_none()
        
        if not employee:
            raise ValueError("Employee not found")
        
        # Federal taxes (same regardless of state)
        federal_taxes = self._calculate_federal_taxes(gross_pay, employee.filing_status)
        
        # State taxes for work state
        work_state_taxes = self._calculate_state_taxes(gross_pay, work_state, employee.filing_status)
        
        # State taxes for residence state (if different)
        residence_state_taxes = Decimal('0')
        if work_state != residence_state:
            residence_state_taxes = self._calculate_state_taxes(gross_pay, residence_state, employee.filing_status)
            # Apply credit for taxes paid to work state
            residence_state_taxes = max(Decimal('0'), residence_state_taxes - work_state_taxes['income_tax'])
        
        # State disability insurance
        sdi_tax = self._calculate_sdi_tax(gross_pay, work_state, employee.ytd_wages)
        
        # State unemployment (employer portion)
        sui_tax = self._calculate_sui_tax(gross_pay, work_state, employee.ytd_wages)
        
        # Local taxes (simplified)
        local_taxes = self._calculate_local_taxes(gross_pay, work_state)
        
        return TaxCalculationResult(
            employee_id=employee_id,
            gross_pay=gross_pay,
            federal_income_tax=federal_taxes['income_tax'],
            federal_social_security=federal_taxes['social_security'],
            federal_medicare=federal_taxes['medicare'],
            work_state_income_tax=work_state_taxes['income_tax'],
            residence_state_income_tax=residence_state_taxes,
            state_disability_tax=sdi_tax,
            state_unemployment_tax=sui_tax,
            local_taxes=local_taxes,
            total_taxes=federal_taxes['total'] + work_state_taxes['income_tax'] + residence_state_taxes + sdi_tax + local_taxes,
            net_pay=gross_pay - (federal_taxes['total'] + work_state_taxes['income_tax'] + residence_state_taxes + sdi_tax + local_taxes)
        )
    
    def _calculate_federal_taxes(self, gross_pay: Decimal, filing_status: str) -> Dict[str, Decimal]:
        """Calculate federal taxes"""
        # Simplified federal tax calculation
        # In production, would use actual tax tables
        
        # Social Security (6.2% up to wage base)
        ss_rate = Decimal('0.062')
        ss_wage_base = Decimal('160200')  # 2023 limit
        social_security = min(gross_pay * ss_rate, ss_wage_base * ss_rate)
        
        # Medicare (1.45% + 0.9% additional for high earners)
        medicare_rate = Decimal('0.0145')
        medicare = gross_pay * medicare_rate
        
        # Additional Medicare tax for high earners
        if gross_pay > Decimal('200000'):  # Simplified threshold
            additional_medicare = (gross_pay - Decimal('200000')) * Decimal('0.009')
            medicare += additional_medicare
        
        # Federal income tax (simplified)
        if filing_status == 'single':
            if gross_pay <= Decimal('10275'):
                income_tax = gross_pay * Decimal('0.10')
            elif gross_pay <= Decimal('41775'):
                income_tax = Decimal('1027.50') + (gross_pay - Decimal('10275')) * Decimal('0.12')
            else:
                income_tax = Decimal('4807.50') + (gross_pay - Decimal('41775')) * Decimal('0.22')
        else:  # married filing jointly
            if gross_pay <= Decimal('20550'):
                income_tax = gross_pay * Decimal('0.10')
            elif gross_pay <= Decimal('83550'):
                income_tax = Decimal('2055') + (gross_pay - Decimal('20550')) * Decimal('0.12')
            else:
                income_tax = Decimal('9615') + (gross_pay - Decimal('83550')) * Decimal('0.22')
        
        return {
            'income_tax': income_tax,
            'social_security': social_security,
            'medicare': medicare,
            'total': income_tax + social_security + medicare
        }
    
    def _calculate_state_taxes(self, gross_pay: Decimal, state: str, filing_status: str) -> Dict[str, Decimal]:
        """Calculate state income taxes"""
        if state not in self.STATE_TAX_RATES:
            return {'income_tax': Decimal('0')}
        
        state_info = self.STATE_TAX_RATES[state]
        rate = state_info['rate']
        standard_deduction = state_info['standard_deduction']
        
        # Apply standard deduction
        taxable_income = max(Decimal('0'), gross_pay - standard_deduction)
        income_tax = taxable_income * rate
        
        return {'income_tax': income_tax}
    
    def _calculate_sdi_tax(self, gross_pay: Decimal, state: str, ytd_wages: Decimal) -> Decimal:
        """Calculate state disability insurance tax"""
        if state not in self.SDI_RATES:
            return Decimal('0')
        
        sdi_info = self.SDI_RATES[state]
        rate = sdi_info['rate']
        wage_base = sdi_info['wage_base']
        
        # Check if YTD wages exceed wage base
        if ytd_wages >= wage_base:
            return Decimal('0')
        
        # Calculate taxable wages for this pay period
        remaining_wage_base = wage_base - ytd_wages
        taxable_wages = min(gross_pay, remaining_wage_base)
        
        return taxable_wages * rate
    
    def _calculate_sui_tax(self, gross_pay: Decimal, state: str, ytd_wages: Decimal) -> Decimal:
        """Calculate state unemployment insurance tax (employer portion)"""
        if state not in self.SUI_RATES:
            return Decimal('0')
        
        sui_info = self.SUI_RATES[state]
        rate = sui_info['rate']
        wage_base = sui_info['wage_base']
        
        # Check if YTD wages exceed wage base
        if ytd_wages >= wage_base:
            return Decimal('0')
        
        # Calculate taxable wages for this pay period
        remaining_wage_base = wage_base - ytd_wages
        taxable_wages = min(gross_pay, remaining_wage_base)
        
        return taxable_wages * rate
    
    def _calculate_local_taxes(self, gross_pay: Decimal, state: str) -> Decimal:
        """Calculate local taxes (simplified)"""
        # Local tax rates vary by city/county
        # This is a simplified implementation
        local_tax_states = {
            'NY': Decimal('0.03'),  # NYC local tax
            'PA': Decimal('0.01'),  # Philadelphia local tax
            'OH': Decimal('0.025'), # Cleveland local tax
        }
        
        if state in local_tax_states:
            return gross_pay * local_tax_states[state]
        
        return Decimal('0')
    
    async def get_tax_summary_by_state(
        self,
        db: AsyncSession,
        payroll_run_id: int
    ) -> Dict[str, Dict[str, Decimal]]:
        """Get tax summary grouped by state for a payroll run"""
        
        # Get all tax calculations for the payroll run
        result = await db.execute(
            select(TaxCalculation)
            .where(TaxCalculation.payroll_run_id == payroll_run_id)
        )
        tax_calculations = result.scalars().all()
        
        state_summary = {}
        
        for calc in tax_calculations:
            state = calc.work_state or 'Unknown'
            
            if state not in state_summary:
                state_summary[state] = {
                    'total_gross': Decimal('0'),
                    'total_federal_income': Decimal('0'),
                    'total_state_income': Decimal('0'),
                    'total_social_security': Decimal('0'),
                    'total_medicare': Decimal('0'),
                    'total_sdi': Decimal('0'),
                    'total_sui': Decimal('0'),
                    'employee_count': 0
                }
            
            state_summary[state]['total_gross'] += calc.gross_pay
            state_summary[state]['total_federal_income'] += calc.federal_income_tax
            state_summary[state]['total_state_income'] += calc.work_state_income_tax
            state_summary[state]['total_social_security'] += calc.federal_social_security
            state_summary[state]['total_medicare'] += calc.federal_medicare
            state_summary[state]['total_sdi'] += calc.state_disability_tax
            state_summary[state]['total_sui'] += calc.state_unemployment_tax
            state_summary[state]['employee_count'] += 1
        
        return state_summary