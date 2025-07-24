"""
Tax calculation service for the Payroll module.
"""
from typing import Dict, List
from decimal import Decimal
from uuid import UUID

from app.modules.core_financials.payroll.schemas.tax_calculation import (
    TaxCalculationRequest, TaxCalculationResult, TaxBracket, TaxRule,
    TaxTypeEnum, FilingStatusEnum
)


class TaxCalculationService:
    """Service for calculating payroll taxes."""
    
    # 2024 Federal Tax Brackets (Single)
    FEDERAL_TAX_BRACKETS_SINGLE = [
        TaxBracket(min_income=Decimal("0"), max_income=Decimal("11000"), rate=Decimal("0.10")),
        TaxBracket(min_income=Decimal("11000"), max_income=Decimal("44725"), rate=Decimal("0.12"), base_tax=Decimal("1100")),
        TaxBracket(min_income=Decimal("44725"), max_income=Decimal("95375"), rate=Decimal("0.22"), base_tax=Decimal("5147")),
        TaxBracket(min_income=Decimal("95375"), max_income=Decimal("182050"), rate=Decimal("0.24"), base_tax=Decimal("16290")),
        TaxBracket(min_income=Decimal("182050"), max_income=Decimal("231250"), rate=Decimal("0.32"), base_tax=Decimal("37104")),
        TaxBracket(min_income=Decimal("231250"), max_income=Decimal("578125"), rate=Decimal("0.35"), base_tax=Decimal("52832")),
        TaxBracket(min_income=Decimal("578125"), max_income=None, rate=Decimal("0.37"), base_tax=Decimal("174238.25"))
    ]
    
    # 2024 Federal Tax Brackets (Married Filing Jointly)
    FEDERAL_TAX_BRACKETS_MARRIED = [
        TaxBracket(min_income=Decimal("0"), max_income=Decimal("22000"), rate=Decimal("0.10")),
        TaxBracket(min_income=Decimal("22000"), max_income=Decimal("89450"), rate=Decimal("0.12"), base_tax=Decimal("2200")),
        TaxBracket(min_income=Decimal("89450"), max_income=Decimal("190750"), rate=Decimal("0.22"), base_tax=Decimal("10294")),
        TaxBracket(min_income=Decimal("190750"), max_income=Decimal("364200"), rate=Decimal("0.24"), base_tax=Decimal("32580")),
        TaxBracket(min_income=Decimal("364200"), max_income=Decimal("462500"), rate=Decimal("0.32"), base_tax=Decimal("74208")),
        TaxBracket(min_income=Decimal("462500"), max_income=Decimal("693750"), rate=Decimal("0.35"), base_tax=Decimal("105664")),
        TaxBracket(min_income=Decimal("693750"), max_income=None, rate=Decimal("0.37"), base_tax=Decimal("186601.25"))
    ]
    
    # Standard deductions for 2024
    STANDARD_DEDUCTIONS = {
        FilingStatusEnum.SINGLE: Decimal("13850"),
        FilingStatusEnum.MARRIED_JOINT: Decimal("27700"),
        FilingStatusEnum.MARRIED_SEPARATE: Decimal("13850"),
        FilingStatusEnum.HEAD_OF_HOUSEHOLD: Decimal("20800")
    }
    
    # Social Security and Medicare rates
    SOCIAL_SECURITY_RATE = Decimal("0.062")  # 6.2%
    SOCIAL_SECURITY_WAGE_BASE = Decimal("160200")  # 2024 wage base
    MEDICARE_RATE = Decimal("0.0145")  # 1.45%
    MEDICARE_ADDITIONAL_RATE = Decimal("0.009")  # 0.9% additional for high earners
    MEDICARE_ADDITIONAL_THRESHOLD = Decimal("200000")
    
    # Unemployment tax rates (employer portion)
    FUTA_RATE = Decimal("0.006")  # 0.6%
    FUTA_WAGE_BASE = Decimal("7000")
    
    @staticmethod
    def calculate_taxes(request: TaxCalculationRequest) -> TaxCalculationResult:
        """Calculate all taxes for an employee."""
        
        # Annualize the gross pay for tax calculations
        annual_gross = TaxCalculationService._annualize_pay(request.gross_pay, request.pay_period)
        
        # Calculate federal income tax
        federal_tax = TaxCalculationService._calculate_federal_income_tax(
            annual_gross, request.filing_status, request.allowances
        )
        
        # Calculate state income tax (simplified - using 5% flat rate)
        state_tax = TaxCalculationService._calculate_state_income_tax(
            annual_gross, request.state or "CA"
        )
        
        # Calculate FICA taxes
        social_security_tax = TaxCalculationService._calculate_social_security_tax(annual_gross)
        medicare_tax = TaxCalculationService._calculate_medicare_tax(annual_gross)
        
        # Calculate unemployment taxes (usually employer-paid, but included for completeness)
        unemployment_tax = TaxCalculationService._calculate_unemployment_tax(annual_gross)
        
        # Disability tax (state-specific, using CA as example)
        disability_tax = TaxCalculationService._calculate_disability_tax(annual_gross)
        
        # Convert annual taxes back to pay period
        period_multiplier = TaxCalculationService._get_period_multiplier(request.pay_period)
        
        federal_tax_period = federal_tax / period_multiplier
        state_tax_period = state_tax / period_multiplier
        social_security_period = social_security_tax / period_multiplier
        medicare_period = medicare_tax / period_multiplier
        unemployment_period = unemployment_tax / period_multiplier
        disability_period = disability_tax / period_multiplier
        
        # Add additional withholding
        federal_tax_period += request.additional_withholding
        
        # Calculate totals
        total_tax = (federal_tax_period + state_tax_period + social_security_period + 
                    medicare_period + unemployment_period + disability_period)
        net_pay = request.gross_pay - total_tax
        
        # Calculate tax rates
        effective_rate = (total_tax / request.gross_pay) * 100 if request.gross_pay > 0 else Decimal("0")
        marginal_rate = TaxCalculationService._get_marginal_tax_rate(annual_gross, request.filing_status)
        
        return TaxCalculationResult(
            employee_id=request.employee_id,
            gross_pay=request.gross_pay,
            federal_income_tax=federal_tax_period,
            state_income_tax=state_tax_period,
            social_security_tax=social_security_period,
            medicare_tax=medicare_period,
            unemployment_tax=unemployment_period,
            disability_tax=disability_period,
            total_tax=total_tax,
            net_pay=net_pay,
            effective_tax_rate=effective_rate,
            marginal_tax_rate=marginal_rate
        )
    
    @staticmethod
    def _annualize_pay(pay_amount: Decimal, pay_period: str) -> Decimal:
        """Convert pay amount to annual equivalent."""
        multipliers = {
            "weekly": 52,
            "bi_weekly": 26,
            "semi_monthly": 24,
            "monthly": 12,
            "annual": 1
        }
        return pay_amount * Decimal(str(multipliers.get(pay_period, 26)))
    
    @staticmethod
    def _get_period_multiplier(pay_period: str) -> Decimal:
        """Get multiplier to convert annual to pay period."""
        multipliers = {
            "weekly": 52,
            "bi_weekly": 26,
            "semi_monthly": 24,
            "monthly": 12,
            "annual": 1
        }
        return Decimal(str(multipliers.get(pay_period, 26)))
    
    @staticmethod
    def _calculate_federal_income_tax(
        annual_gross: Decimal, 
        filing_status: FilingStatusEnum, 
        allowances: int
    ) -> Decimal:
        """Calculate federal income tax."""
        
        # Get appropriate tax brackets
        if filing_status == FilingStatusEnum.MARRIED_JOINT:
            brackets = TaxCalculationService.FEDERAL_TAX_BRACKETS_MARRIED
        else:
            brackets = TaxCalculationService.FEDERAL_TAX_BRACKETS_SINGLE
        
        # Apply standard deduction
        standard_deduction = TaxCalculationService.STANDARD_DEDUCTIONS[filing_status]
        taxable_income = max(Decimal("0"), annual_gross - standard_deduction)
        
        # Apply allowances (simplified - $4300 per allowance for 2024)
        allowance_deduction = Decimal(str(allowances)) * Decimal("4300")
        taxable_income = max(Decimal("0"), taxable_income - allowance_deduction)
        
        # Calculate tax using brackets
        tax = Decimal("0")
        for bracket in brackets:
            if taxable_income <= bracket.min_income:
                break
                
            bracket_income = min(taxable_income, bracket.max_income or taxable_income) - bracket.min_income
            tax = bracket.base_tax + (bracket_income * bracket.rate)
            
            if bracket.max_income and taxable_income <= bracket.max_income:
                break
        
        return max(Decimal("0"), tax)
    
    @staticmethod
    def _calculate_state_income_tax(annual_gross: Decimal, state: str) -> Decimal:
        """Calculate state income tax (simplified)."""
        # Simplified state tax calculation - using flat rates
        state_rates = {
            "CA": Decimal("0.05"),  # 5%
            "NY": Decimal("0.045"), # 4.5%
            "TX": Decimal("0"),     # No state income tax
            "FL": Decimal("0"),     # No state income tax
        }
        
        rate = state_rates.get(state, Decimal("0.03"))  # Default 3%
        return annual_gross * rate
    
    @staticmethod
    def _calculate_social_security_tax(annual_gross: Decimal) -> Decimal:
        """Calculate Social Security tax."""
        taxable_wages = min(annual_gross, TaxCalculationService.SOCIAL_SECURITY_WAGE_BASE)
        return taxable_wages * TaxCalculationService.SOCIAL_SECURITY_RATE
    
    @staticmethod
    def _calculate_medicare_tax(annual_gross: Decimal) -> Decimal:
        """Calculate Medicare tax."""
        medicare_tax = annual_gross * TaxCalculationService.MEDICARE_RATE
        
        # Additional Medicare tax for high earners
        if annual_gross > TaxCalculationService.MEDICARE_ADDITIONAL_THRESHOLD:
            additional_wages = annual_gross - TaxCalculationService.MEDICARE_ADDITIONAL_THRESHOLD
            medicare_tax += additional_wages * TaxCalculationService.MEDICARE_ADDITIONAL_RATE
        
        return medicare_tax
    
    @staticmethod
    def _calculate_unemployment_tax(annual_gross: Decimal) -> Decimal:
        """Calculate unemployment tax (FUTA)."""
        taxable_wages = min(annual_gross, TaxCalculationService.FUTA_WAGE_BASE)
        return taxable_wages * TaxCalculationService.FUTA_RATE
    
    @staticmethod
    def _calculate_disability_tax(annual_gross: Decimal) -> Decimal:
        """Calculate state disability tax (using CA SDI as example)."""
        # California SDI rate for 2024: 0.9% on wages up to $153,164
        sdi_rate = Decimal("0.009")
        sdi_wage_base = Decimal("153164")
        
        taxable_wages = min(annual_gross, sdi_wage_base)
        return taxable_wages * sdi_rate
    
    @staticmethod
    def _get_marginal_tax_rate(annual_gross: Decimal, filing_status: FilingStatusEnum) -> Decimal:
        """Get marginal tax rate for the income level."""
        if filing_status == FilingStatusEnum.MARRIED_JOINT:
            brackets = TaxCalculationService.FEDERAL_TAX_BRACKETS_MARRIED
        else:
            brackets = TaxCalculationService.FEDERAL_TAX_BRACKETS_SINGLE
        
        for bracket in reversed(brackets):
            if annual_gross >= bracket.min_income:
                return bracket.rate * 100  # Return as percentage
        
        return Decimal("0")
    
    @staticmethod
    def calculate_batch_taxes(requests: List[TaxCalculationRequest]) -> List[TaxCalculationResult]:
        """Calculate taxes for multiple employees."""
        results = []
        for request in requests:
            result = TaxCalculationService.calculate_taxes(request)
            results.append(result)
        return results