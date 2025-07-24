"""
Payroll calculation models for the Payroll module.
"""
from datetime import date, datetime
from decimal import Decimal
from enum import Enum as PyEnum
from sqlalchemy import Column, Date, DateTime, Enum, ForeignKey, Numeric, String, Text, Boolean, Integer, JSON
from sqlalchemy.orm import relationship, validates
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

from app.core.db.base import Base
from app.modules.core_financials.payroll.models.base import PayrollBase


class PayrollEarningType(PyEnum):
    """Types of earnings in payroll."""
    REGULAR = "REGULAR"
    OVERTIME = "OVERTIME"
    DOUBLE_OVERTIME = "DOUBLE_OVERTIME"
    BONUS = "BONUS"
    COMMISSION = "COMMISSION"
    TIP = "TIP"
    VACATION = "VACATION"
    SICK_LEAVE = "SICK_LEAVE"
    HOLIDAY = "HOLIDAY"
    PERSONAL_LEAVE = "PERSONAL_LEAVE"
    BEREAVEMENT = "BEREAVEMENT"
    JURY_DUTY = "JURY_DUTY"
    MILITARY_LEAVE = "MILITARY_LEAVE"
    SEVERANCE = "SEVERANCE"
    RETROACTIVE = "RETROACTIVE"
    OTHER = "OTHER"


class PayrollDeductionType(PyEnum):
    """Types of deductions in payroll."""
    TAX = "TAX"
    BENEFIT = "BENEFIT"
    GARNISHMENT = "GARNISHMENT"
    LOAN = "LOAN"
    ADVANCE = "ADVANCE"
    UNION_DUES = "UNION_DUES"
    CHARITABLE_CONTRIBUTION = "CHARITABLE_CONTRIBUTION"
    RETIREMENT = "RETIREMENT"
    INSURANCE = "INSURANCE"
    PARKING = "PARKING"
    MEAL = "MEAL"
    UNIFORM = "UNIFORM"
    OTHER = "OTHER"


class PayrollTaxType(PyEnum):
    """Types of taxes in payroll."""
    FEDERAL_INCOME_TAX = "FEDERAL_INCOME_TAX"
    STATE_INCOME_TAX = "STATE_INCOME_TAX"
    LOCAL_INCOME_TAX = "LOCAL_INCOME_TAX"
    SOCIAL_SECURITY = "SOCIAL_SECURITY"
    MEDICARE = "MEDICARE"
    ADDITIONAL_MEDICARE = "ADDITIONAL_MEDICARE"
    FEDERAL_UNEMPLOYMENT = "FEDERAL_UNEMPLOYMENT"
    STATE_UNEMPLOYMENT = "STATE_UNEMPLOYMENT"
    STATE_DISABILITY = "STATE_DISABILITY"
    STATE_FAMILY_LEAVE = "STATE_FAMILY_LEAVE"
    OTHER = "OTHER"


class PayrollBenefitType(PyEnum):
    """Types of benefits in payroll."""
    HEALTH_INSURANCE = "HEALTH_INSURANCE"
    DENTAL_INSURANCE = "DENTAL_INSURANCE"
    VISION_INSURANCE = "VISION_INSURANCE"
    LIFE_INSURANCE = "LIFE_INSURANCE"
    DISABILITY_INSURANCE = "DISABILITY_INSURANCE"
    RETIREMENT = "RETIREMENT"
    PENSION = "PENSION"
    STOCK_OPTIONS = "STOCK_OPTIONS"
    TUITION_REIMBURSEMENT = "TUITION_REIMBURSEMENT"
    CHILD_CARE = "CHILD_CARE"
    TRANSPORTATION = "TRANSPORTATION"
    MEAL = "MEAL"
    OTHER = "OTHER"


class PayrollEarning(PayrollBase, Base):
    """Represents an earning line item in a payroll entry."""
    __tablename__ = "payroll_earnings"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # References
    payroll_entry_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_entries.id'), 
        nullable=False,
        index=True
    )
    earning_code_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_earning_codes.id'), 
        nullable=True,
        index=True
    )
    
    # Earning details
    earning_type = Column(
        Enum(PayrollEarningType, name='payroll_earning_type_enum'),
        nullable=False
    )
    description = Column(String(255), nullable=True)
    
    # Amount calculation
    quantity = Column(Numeric(10, 2), default=1, nullable=False)  # Hours, units, etc.
    rate = Column(Numeric(15, 2), nullable=False)  # Rate per unit
    amount = Column(Numeric(15, 2), nullable=False)  # Calculated: quantity * rate
    
    # Tax and deduction impact
    is_taxable = Column(Boolean, default=True, nullable=False)
    is_pretax = Column(Boolean, default=False, nullable=False)
    is_imputed_income = Column(Boolean, default=False, nullable=False)
    
    # YTD tracking
    ytd_amount = Column(Numeric(15, 2), default=0, nullable=False)
    
    # Metadata
    custom_fields = Column(JSONB, nullable=True, default=dict)
    
    # Relationships
    payroll_entry = relationship("PayrollEntry", back_populates="earnings")
    earning_code = relationship("EarningCode")
    
    def __repr__(self):
        return f"<PayrollEarning {self.earning_type}: {self.amount}>"
    
    @validates('quantity', 'rate')
    def validate_positive_values(self, key, value):
        """Ensure quantity and rate are non-negative."""
        if value < 0:
            raise ValueError(f"{key} cannot be negative")
        return value
    
    def calculate_amount(self):
        """Calculate the amount based on quantity and rate."""
        self.amount = (self.quantity * self.rate).quantize(Decimal('0.01'))


class PayrollDeduction(PayrollBase, Base):
    """Represents a deduction line item in a payroll entry."""
    __tablename__ = "payroll_deductions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # References
    payroll_entry_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_entries.id'), 
        nullable=False,
        index=True
    )
    deduction_code_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_deduction_codes.id'), 
        nullable=True,
        index=True
    )
    
    # Deduction details
    deduction_type = Column(
        Enum(PayrollDeductionType, name='payroll_deduction_type_enum'),
        nullable=False
    )
    description = Column(String(255), nullable=True)
    
    # Amount calculation
    amount = Column(Numeric(15, 2), nullable=False)
    is_percentage = Column(Boolean, default=False, nullable=False)
    percentage = Column(Numeric(5, 2), nullable=True)  # If is_percentage is True
    max_amount = Column(Numeric(15, 2), nullable=True)  # Maximum amount for percentage-based deductions
    
    # Tax impact
    is_pretax = Column(Boolean, default=False, nullable=False)
    affects_taxable_income = Column(Boolean, default=True, nullable=False)
    
    # YTD tracking
    ytd_amount = Column(Numeric(15, 2), default=0, nullable=False)
    
    # Metadata
    custom_fields = Column(JSONB, nullable=True, default=dict)
    
    # Relationships
    payroll_entry = relationship("PayrollEntry", back_populates="deductions")
    deduction_code = relationship("DeductionCode")
    
    def __repr__(self):
        return f"<PayrollDeduction {self.deduction_type}: {self.amount}>"
    
    def calculate_amount(self, base_amount=None):
        """Calculate the deduction amount based on the base amount if percentage-based."""
        if self.is_percentage and base_amount is not None:
            calculated = (base_amount * (self.percentage / 100)).quantize(Decimal('0.01'))
            if self.max_amount is not None and calculated > self.max_amount:
                self.amount = self.max_amount
            else:
                self.amount = calculated


class PayrollTax(PayrollBase, Base):
    """Represents a tax line item in a payroll entry."""
    __tablename__ = "payroll_taxes"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # References
    payroll_entry_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_entries.id'), 
        nullable=False,
        index=True
    )
    tax_code_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_tax_codes.id'), 
        nullable=True,
        index=True
    )
    
    # Tax details
    tax_type = Column(
        Enum(PayrollTaxType, name='payroll_tax_type_enum'),
        nullable=False
    )
    description = Column(String(255), nullable=True)
    
    # Amount calculation
    taxable_amount = Column(Numeric(15, 2), nullable=False)
    tax_rate = Column(Numeric(7, 4), nullable=False)  # Stored as decimal (e.g., 7.5% = 0.075)
    tax_amount = Column(Numeric(15, 2), nullable=False)
    
    # Employer portion (for taxes like FICA where employer pays a portion)
    employer_taxable_amount = Column(Numeric(15, 2), nullable=True)
    employer_tax_rate = Column(Numeric(7, 4), nullable=True)
    employer_tax_amount = Column(Numeric(15, 2), nullable=True)
    
    # YTD tracking
    ytd_taxable_amount = Column(Numeric(15, 2), default=0, nullable=False)
    ytd_tax_amount = Column(Numeric(15, 2), default=0, nullable=False)
    
    # Metadata
    custom_fields = Column(JSONB, nullable=True, default=dict)
    
    # Relationships
    payroll_entry = relationship("PayrollEntry", back_populates="taxes")
    tax_code = relationship("TaxCode")
    
    def __repr__(self):
        return f"<PayrollTax {self.tax_type}: {self.tax_amount}>"


class PayrollBenefit(PayrollBase, Base):
    """Represents a benefit line item in a payroll entry."""
    __tablename__ = "payroll_benefits"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # References
    payroll_entry_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_entries.id'), 
        nullable=False,
        index=True
    )
    benefit_plan_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_benefit_plans.id'), 
        nullable=True,
        index=True
    )
    
    # Benefit details
    benefit_type = Column(
        Enum(PayrollBenefitType, name='payroll_benefit_type_enum'),
        nullable=False
    )
    description = Column(String(255), nullable=True)
    
    # Amount calculation
    employee_amount = Column(Numeric(15, 2), default=0, nullable=False)  # Employee contribution
    employer_amount = Column(Numeric(15, 2), default=0, nullable=False)  # Employer contribution
    
    # Tax impact
    is_pretax = Column(Boolean, default=False, nullable=False)
    is_taxable = Column(Boolean, default=False, nullable=False)
    
    # YTD tracking
    ytd_employee_amount = Column(Numeric(15, 2), default=0, nullable=False)
    ytd_employer_amount = Column(Numeric(15, 2), default=0, nullable=False)
    
    # Metadata
    custom_fields = Column(JSONB, nullable=True, default=dict)
    
    # Relationships
    payroll_entry = relationship("PayrollEntry", back_populates="benefits")
    benefit_plan = relationship("BenefitPlan")
    
    def __repr__(self):
        return f"<PayrollBenefit {self.benefit_type}: Employee={self.employee_amount}, Employer={self.employer_amount}>"
