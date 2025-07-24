"""
Tax models for the Payroll module.
"""
from datetime import date
from sqlalchemy import Column, Date, Enum, ForeignKey, Numeric, String, Text, Boolean, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.core.db.base import Base
from app.modules.core_financials.payroll.models.base import PayrollBase


class TaxTable(PayrollBase, Base):
    """Tax table model for different tax brackets and rules."""
    __tablename__ = "payroll_tax_tables"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # Tax table identification
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    country = Column(String(2), nullable=False, index=True)  # ISO 3166-1 alpha-2
    state = Column(String(100), nullable=True, index=True)
    
    # Effective date range
    effective_from = Column(Date, nullable=False, index=True)
    effective_to = Column(Date, nullable=True, index=True)
    
    # Tax type (income tax, social security, etc.)
    tax_type = Column(
        Enum('INCOME_TAX', 'SOCIAL_SECURITY', 'MEDICARE', 'UNEMPLOYMENT', 'LOCAL_TAX', 'OTHER',
             name='tax_type_enum'),
        nullable=False
    )
    
    # Calculation method
    calculation_method = Column(
        Enum('FLAT_RATE', 'GRADUATED', 'FIXED_AMOUNT', 'PERCENTAGE', 'TIERED', name='tax_calculation_method_enum'),
        nullable=False
    )
    
    # Default rates/amounts (can be overridden by brackets)
    default_rate = Column(Numeric(5, 4), nullable=True)  # For percentage-based calculations
    fixed_amount = Column(Numeric(15, 2), nullable=True)  # For fixed amount calculations
    
    # Annualization factor (for converting between pay periods)
    annualization_factor = Column(Numeric(10, 4), default=1.0, nullable=False)
    
    # Relationships
    tax_brackets = relationship("TaxBracket", back_populates="tax_table", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<TaxTable {self.name} ({self.country}{f'-{self.state}' if self.state else ''})>"
    
    @property
    def is_active(self):
        """Check if the tax table is currently active."""
        today = date.today()
        return (self.effective_from <= today and 
                (self.effective_to is None or today <= self.effective_to))


class TaxBracket(PayrollBase, Base):
    """Tax bracket model for graduated tax calculations."""
    __tablename__ = "payroll_tax_brackets"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # Reference to tax table
    tax_table_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_tax_tables.id'), 
        nullable=False,
        index=True
    )
    
    # Bracket range
    min_amount = Column(Numeric(15, 2), nullable=False)
    max_amount = Column(Numeric(15, 2), nullable=True)  # None means no upper limit
    
    # Bracket details
    rate = Column(Numeric(5, 4), nullable=False)  # Tax rate for this bracket
    base_tax_amount = Column(Numeric(15, 2), default=0, nullable=False)  # Base tax for this bracket
    
    # Bracket type
    bracket_type = Column(
        Enum('SINGLE', 'MARRIED_FILING_JOINTLY', 'MARRIED_FILING_SEPARATELY', 
             'HEAD_OF_HOUSEHOLD', 'QUALIFYING_WIDOW', 'ALL', name='tax_bracket_type_enum'),
        default='ALL',
        nullable=False
    )
    
    # Relationships
    tax_table = relationship("TaxTable", back_populates="tax_brackets")
    
    def __repr__(self):
        max_str = f"{self.max_amount:,.2f}" if self.max_amount is not None else "∞"
        return f"<TaxBracket {self.min_amount:,.2f}-{max_str} @ {self.rate:.2%}>"
    
    def calculate_tax(self, taxable_amount):
        """Calculate tax for the given amount within this bracket."""
        if self.max_amount is not None and taxable_amount > self.max_amount:
            taxable_in_bracket = self.max_amount - self.min_amount + 1
        else:
            taxable_in_bracket = max(0, taxable_amount - self.min_amount + 1)
            
        return (self.base_tax_amount + 
                (taxable_in_bracket * self.rate)).quantize(Decimal('0.01'))


class EmployeeTax(PayrollBase, Base):
    """Employee-specific tax settings and calculations."""
    __tablename__ = "payroll_employee_taxes"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # References
    employee_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_employees.id'), 
        nullable=False,
        index=True
    )
    
    # Tax identification
    tax_id = Column(String(50), nullable=True, index=True)
    tax_filing_status = Column(
        Enum('SINGLE', 'MARRIED_FILING_JOINTLY', 'MARRIED_FILING_SEPARATELY', 
             'HEAD_OF_HOUSEHOLD', 'QUALIFYING_WIDOW', 'NON_RESIDENT', 'EXEMPT',
             name='tax_filing_status_enum'),
        nullable=False,
        default='SINGLE'
    )
    
    # Allowances and exemptions
    federal_allowances = Column(Integer, default=0, nullable=False)
    state_allowances = Column(Integer, default=0, nullable=True)
    additional_withholding = Column(Numeric(15, 2), default=0, nullable=False)
    
    # Tax credits
    tax_credits = Column(Numeric(15, 2), default=0, nullable=False)
    
    # Tax tables (references)
    federal_income_tax_table_id = Column(UUID(as_uuid=True), ForeignKey('payroll_tax_tables.id'), nullable=True)
    state_income_tax_table_id = Column(UUID(as_uuid=True), ForeignKey('payroll_tax_tables.id'), nullable=True)
    local_income_tax_table_id = Column(UUID(as_uuid=True), ForeignKey('payroll_tax_tables.id'), nullable=True)
    
    # Social Security and Medicare
    social_security_number = Column(String(50), nullable=True, index=True)
    is_social_security_exempt = Column(Boolean, default=False, nullable=False)
    is_medicare_exempt = Column(Boolean, default=False, nullable=False)
    
    # Additional tax information
    is_non_resident_alien = Column(Boolean, default=False, nullable=False)
    tax_treaty_country = Column(String(2), nullable=True)  # ISO 3166-1 alpha-2
    
    # Relationships
    employee = relationship("Employee", backref="tax_settings")
    federal_income_tax_table = relationship("TaxTable", foreign_keys=[federal_income_tax_table_id])
    state_income_tax_table = relationship("TaxTable", foreign_keys=[state_income_tax_table_id])
    local_income_tax_table = relationship("TaxTable", foreign_keys=[local_income_tax_table_id])
    
    def __repr__(self):
        return f"<EmployeeTax for Employee {self.employee_id}>"
