"""
Payroll tax calculation utilities for the payroll processing service.
"""
from datetime import date
from typing import Dict, List, Optional, Tuple

from ..models.payroll_models import (
from ..schemas.payroll_schemas import PayrollTaxItem
from decimal import Decimal, ROUND_HALF_UP
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.config import settings
from app.core.logging import logger




    Employee, TaxCode, TaxBracket, TaxCalculation, Payslip, PayPeriod
)


class PayrollTaxCalculator:
    """Handles payroll tax calculations for employees."""
    
    def __init__(self, db: Session):
        """  Init  ."""
        """Initialize the tax calculator with a database session."""
        self.db = db
    
    def calculate_taxes(
        self,
        employee: Employee,
        pay_period: PayPeriod,
        taxable_income: Decimal,
        pay_date: date,
        is_regular_pay: bool = True
    ) -> List[PayrollTaxItem]:
        """Calculate Taxes."""
        """
        Calculate all applicable taxes for an employee.
        
        Args:
            employee: The employee
            pay_period: The pay period
            taxable_income: Taxable income amount
            pay_date: Date of payment (for tax rate determination)
            is_regular_pay: Whether this is a regular pay run (affects tax calculations)
            
        Returns:
            List of tax items with details
        """
        taxes = []
        
        # Get all active tax codes for the employee's location
        tax_codes = self._get_applicable_tax_codes(
            employee=employee,
            pay_date=pay_date,
            is_regular_pay=is_regular_pay
        )
        
        # Calculate each tax
        for tax_code in tax_codes:
            tax_amount = self._calculate_tax_amount(
                tax_code=tax_code,
                taxable_income=taxable_income,
                pay_period=pay_period,
                employee=employee
            )
            
            if tax_amount > 0:
                taxes.append(
                    PayrollTaxItem(
                        code=tax_code.code,
                        name=tax_code.name,
                        amount=tax_amount,
                        is_employer_tax=tax_code.is_employer_tax,
                        ytd_amount=self._get_ytd_taxes(
                            employee.id, 
                            tax_code.id, 
                            pay_period.end_date.year
                        )
                    )
                )
        
        return taxes
    
    def _get_applicable_tax_codes(
        self,
        employee: Employee,
        pay_date: date,
        is_regular_pay: bool = True
    ) -> List[TaxCode]:
        """ Get Applicable Tax Codes."""
        """
        Get all tax codes that apply to the employee based on their location.
        
        Args:
            employee: The employee
            pay_date: Date to check tax code validity
            is_regular_pay: Whether this is a regular pay run
            
        Returns:
            List of applicable tax codes
        """
        # Base query for active tax codes
        query = self.db.query(TaxCode).filter(
            TaxCode.is_active == True,
            TaxCode.effective_date <= pay_date,
            or_(
                TaxCode.expiration_date.is_(None),
                TaxCode.expiration_date >= pay_date
            )
        )
        
        # Filter by employee's location
        if employee.state:
            query = query.filter(
                or_(
                    and_(
                        TaxCode.state.isnot(None),
                        TaxCode.state == employee.state
                    ),
                    TaxCode.state.is_(None)
                )
            )
        
        if employee.country:
            query = query.filter(
                or_(
                    and_(
                        TaxCode.country.isnot(None),
                        TaxCode.country == employee.country
                    ),
                    TaxCode.country.is_(None)
                )
            )
        
        # Filter by pay type if needed
        if is_regular_pay:
            query = query.filter(TaxCode.applies_to_regular_pay == True)
        
        return query.all()
    
    def _calculate_tax_amount(
        self,
        tax_code: TaxCode,
        taxable_income: Decimal,
        pay_period: PayPeriod,
        employee: Employee
    ) -> Decimal:
        """ Calculate Tax Amount."""
        """
        Calculate tax amount based on tax code and taxable income.
        
        Args:
            tax_code: The tax code to use for calculation
            taxable_income: Taxable income amount
            pay_period: The pay period
            employee: The employee
            
        Returns:
            Calculated tax amount
        """
        if taxable_income <= 0 or not tax_code.is_active:
            return Decimal("0.00")
        
        # Get the appropriate tax calculation method
        calculation = tax_code.calculation_method or "PERCENTAGE"
        
        if calculation == "FLAT_RATE":
            return tax_code.rate.quantize(Decimal("0.01"), ROUND_HALF_UP)
        
        elif calculation == "PERCENTAGE":
            return (taxable_income * (tax_code.rate / 100)).quantize(
                Decimal("0.01"), 
                ROUND_HALF_UP
            )
        
        elif calculation == "BRACKETED":
            return self._calculate_bracketed_tax(
                tax_code=tax_code,
                taxable_income=taxable_income,
                pay_period=pay_period,
                employee=employee
            )
        
        return Decimal("0.00")
    
    def _calculate_bracketed_tax(
        self,
        tax_code: TaxCode,
        taxable_income: Decimal,
        pay_period: PayPeriod,
        employee: Employee
    ) -> Decimal:
        """ Calculate Bracketed Tax."""
        """
        Calculate tax using tax brackets.
        
        Args:
            tax_code: The tax code
            taxable_income: Taxable income amount
            pay_period: The pay period
            employee: The employee
            
        Returns:
            Calculated tax amount
        """
        # Get applicable tax brackets
        brackets = (
            self.db.query(TaxBracket)
            .filter(
                TaxBracket.tax_code_id == tax_code.id,
                TaxBracket.is_active == True,
                TaxBracket.effective_date <= pay_period.end_date,
                or_(
                    TaxBracket.expiration_date.is_(None),
                    TaxBracket.expiration_date >= pay_period.start_date
                )
            )
            .order_by(TaxBracket.lower_bound.asc())
            .all()
        )
        
        if not brackets:
            logger.warning(f"No active tax brackets found for tax code {tax_code.code}")
            return Decimal("0.00")
        
        # Calculate tax using the brackets
        remaining_income = taxable_income
        total_tax = Decimal("0.00")
        
        for bracket in brackets:
            if remaining_income <= 0:
                break
                
            # Calculate the amount of income in this bracket
            bracket_width = (
                bracket.upper_bound - bracket.lower_bound 
                if bracket.upper_bound is not None 
                else remaining_income
            )
            
            income_in_bracket = min(remaining_income, bracket_width)
            
            # Calculate tax for this bracket
            if bracket.rate_type == "PERCENTAGE":
                bracket_tax = income_in_bracket * (bracket.rate / 100)
            else:  # FIXED_AMOUNT
                bracket_tax = bracket.rate
            
            # Add any additional amount
            if bracket.additional_amount is not None:
                bracket_tax += bracket.additional_amount
            
            total_tax += bracket_tax
            remaining_income -= income_in_bracket
        
        # Apply any annualization factor for partial year calculations
        if tax_code.is_annual and tax_code.annualization_factor:
            total_tax = total_tax / Decimal(str(tax_code.annualization_factor))
        
        # Round to the nearest cent
        return total_tax.quantize(Decimal("0.01"), ROUND_HALF_UP)
    
    def _get_ytd_taxes(
        self,
        employee_id: UUID,
        tax_code_id: UUID,
        year: int
    ) -> Decimal:
        """ Get Ytd Taxes."""
        """
        Get year-to-date taxes paid for a specific tax code.
        
        Args:
            employee_id: ID of the employee
            tax_code_id: ID of the tax code
            year: Calendar year
            
        Returns:
            Total YTD taxes for the tax code
        """
        # In a real implementation, this would query the payslips table
        # to get the sum of taxes paid for the given employee and tax code
        # for the specified year up to the current date
        
        # For now, return a placeholder value
        return Decimal("0.00")
