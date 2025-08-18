"""
Payroll code tables for the Payroll module.
"""
from datetime import date, datetime
from decimal import Decimal
from enum import Enum as PyEnum
from sqlalchemy import Column, Date, DateTime, Enum, ForeignKey, Numeric, String, Text, Boolean, Integer, JSON
from sqlalchemy.orm import relationship, validates
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

from app.core.database import Base
from app.modules.core_financials.payroll.models.base import PayrollBase


class EarningCode(PayrollBase, Base):
    """Earning codes for payroll processing."""
    __tablename__ = "payroll_earning_codes"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # Code identification
    code = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Earning type
    earning_type = Column(
        Enum('REGULAR', 'OVERTIME', 'DOUBLE_OVERTIME', 'BONUS', 'COMMISSION', 'TIP', 'VACATION', 
             'SICK_LEAVE', 'HOLIDAY', 'PERSONAL_LEAVE', 'BEREAVEMENT', 'JURY_DUTY', 'MILITARY_LEAVE', 
             'SEVERANCE', 'RETROACTIVE', 'OTHER', name='earning_type_enum'),
        nullable=False
    )
    
    # Tax and deduction impact
    is_taxable = Column(Boolean, default=True, nullable=False)
    is_pretax = Column(Boolean, default=False, nullable=False)
    is_imputed_income = Column(Boolean, default=False, nullable=False)
    
    # Rate information
    has_fixed_rate = Column(Boolean, default=False, nullable=False)
    fixed_rate = Column(Numeric(15, 2), nullable=True)
    
    # GL Account mapping
    gl_account_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_gl_accounts.id'), 
        nullable=True,
        index=True
    )
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    effective_date = Column(Date, nullable=False, default=date.today)
    expiration_date = Column(Date, nullable=True)
    
    # Metadata
    custom_fields = Column(JSONB, nullable=True, default=dict)
    
    # Relationships
    gl_account = relationship("GLAccount")
    
    def __repr__(self):
        return f"<EarningCode {self.code}: {self.name}>"
    
    @property
    def is_current(self):
        """Check if the earning code is currently active."""
        today = date.today()
        return (self.is_active and 
                self.effective_date <= today and 
                (self.expiration_date is None or today <= self.expiration_date))


class DeductionCode(PayrollBase, Base):
    """Deduction codes for payroll processing."""
    __tablename__ = "payroll_deduction_codes"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # Code identification
    code = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Deduction type
    deduction_type = Column(
        Enum('TAX', 'BENEFIT', 'GARNISHMENT', 'LOAN', 'ADVANCE', 'UNION_DUES', 
             'CHARITABLE_CONTRIBUTION', 'RETIREMENT', 'INSURANCE', 'PARKING', 
             'MEAL', 'UNIFORM', 'OTHER', name='deduction_type_enum'),
        nullable=False
    )
    
    # Calculation method
    calculation_method = Column(
        Enum('FIXED_AMOUNT', 'PERCENTAGE', 'FLAT_RATE', 'TIERED', name='deduction_calculation_method_enum'),
        default='FIXED_AMOUNT',
        nullable=False
    )
    
    # Amount or rate
    amount = Column(Numeric(15, 2), nullable=True)
    percentage = Column(Numeric(5, 2), nullable=True)  # For percentage-based deductions
    
    # Limits
    minimum_amount = Column(Numeric(15, 2), nullable=True)
    maximum_amount = Column(Numeric(15, 2), nullable=True)
    
    # Tax impact
    is_pretax = Column(Boolean, default=False, nullable=False)
    affects_taxable_income = Column(Boolean, default=True, nullable=False)
    
    # GL Account mapping
    gl_account_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_gl_accounts.id'), 
        nullable=True,
        index=True
    )
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    effective_date = Column(Date, nullable=False, default=date.today)
    expiration_date = Column(Date, nullable=True)
    
    # Metadata
    custom_fields = Column(JSONB, nullable=True, default=dict)
    
    # Relationships
    gl_account = relationship("GLAccount")
    
    def __repr__(self):
        return f"<DeductionCode {self.code}: {self.name}>"
    
    @property
    def is_current(self):
        """Check if the deduction code is currently active."""
        today = date.today()
        return (self.is_active and 
                self.effective_date <= today and 
                (self.expiration_date is None or today <= self.expiration_date))


class TaxCode(PayrollBase, Base):
    """Tax codes for payroll processing."""
    __tablename__ = "payroll_tax_codes"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # Code identification
    code = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Tax type
    tax_type = Column(
        Enum('FEDERAL_INCOME_TAX', 'STATE_INCOME_TAX', 'LOCAL_INCOME_TAX', 'SOCIAL_SECURITY', 
             'MEDICARE', 'ADDITIONAL_MEDICARE', 'FEDERAL_UNEMPLOYMENT', 'STATE_UNEMPLOYMENT', 
             'STATE_DISABILITY', 'STATE_FAMILY_LEAVE', 'OTHER', name='tax_code_type_enum'),
        nullable=False
    )
    
    # Jurisdiction
    country = Column(String(2), nullable=False, index=True)  # ISO 3166-1 alpha-2
    state = Column(String(2), nullable=True, index=True)     # For state/province level taxes
    locality = Column(String(100), nullable=True, index=True) # For local/city level taxes
    
    # Tax rates
    employee_rate = Column(Numeric(7, 4), nullable=True)  # As decimal (e.g., 7.5% = 0.075)
    employer_rate = Column(Numeric(7, 4), nullable=True)  # As decimal (e.g., 7.5% = 0.075)
    
    # Wage base limits
    wage_base_limit = Column(Numeric(15, 2), nullable=True)  # Null means no limit
    
    # GL Account mapping
    employee_liability_account_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_gl_accounts.id'), 
        nullable=True,
        index=True
    )
    employer_liability_account_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_gl_accounts.id'), 
        nullable=True,
        index=True
    )
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    effective_date = Column(Date, nullable=False, default=date.today)
    expiration_date = Column(Date, nullable=True)
    
    # Metadata
    custom_fields = Column(JSONB, nullable=True, default=dict)
    
    # Relationships
    employee_liability_account = relationship(
        "GLAccount", 
        foreign_keys=[employee_liability_account_id]
    )
    employer_liability_account = relationship(
        "GLAccount", 
        foreign_keys=[employer_liability_account_id]
    )
    
    def __repr__(self):
        return f"<TaxCode {self.code}: {self.name}>"
    
    @property
    def is_current(self):
        """Check if the tax code is currently active."""
        today = date.today()
        return (self.is_active and 
                self.effective_date <= today and 
                (self.expiration_date is None or today <= self.expiration_date))


class BenefitPlan(PayrollBase, Base):
    """Benefit plans for payroll processing."""
    __tablename__ = "payroll_benefit_plans"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # Plan identification
    plan_code = Column(String(20), unique=True, index=True, nullable=False)
    plan_name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Plan type
    benefit_type = Column(
        Enum('HEALTH_INSURANCE', 'DENTAL_INSURANCE', 'VISION_INSURANCE', 'LIFE_INSURANCE', 
             'DISABILITY_INSURANCE', 'RETIREMENT', 'PENSION', 'STOCK_OPTIONS', 
             'TUITION_REIMBURSEMENT', 'CHILD_CARE', 'TRANSPORTATION', 'MEAL', 'OTHER', 
             name='benefit_plan_type_enum'),
        nullable=False
    )
    
    # Plan details
    provider_name = Column(String(100), nullable=True)
    plan_number = Column(String(50), nullable=True)
    policy_number = Column(String(50), nullable=True)
    
    # Employee and employer contributions
    employee_contribution_type = Column(
        Enum('FIXED_AMOUNT', 'PERCENTAGE', 'FLAT_RATE', 'TIERED', 'NONE', name='contribution_type_enum'),
        default='NONE',
        nullable=False
    )
    employee_contribution_amount = Column(Numeric(15, 2), nullable=True)
    employee_contribution_percentage = Column(Numeric(5, 2), nullable=True)  # For percentage-based contributions
    
    employer_contribution_type = Column(
        Enum('FIXED_AMOUNT', 'PERCENTAGE', 'FLAT_RATE', 'TIERED', 'NONE', name='contribution_type_enum'),
        default='NONE',
        nullable=False
    )
    employer_contribution_amount = Column(Numeric(15, 2), nullable=True)
    employer_contribution_percentage = Column(Numeric(5, 2), nullable=True)  # For percentage-based contributions
    
    # Limits
    annual_maximum = Column(Numeric(15, 2), nullable=True)
    lifetime_maximum = Column(Numeric(15, 2), nullable=True)
    
    # Tax impact
    is_employee_contribution_pretax = Column(Boolean, default=False, nullable=False)
    is_employer_contribution_taxable = Column(Boolean, default=False, nullable=False)
    
    # GL Account mapping
    employee_contra_account_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_gl_accounts.id'), 
        nullable=True,
        index=True
    )
    employer_contra_account_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_gl_accounts.id'), 
        nullable=True,
        index=True
    )
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    effective_date = Column(Date, nullable=False, default=date.today)
    expiration_date = Column(Date, nullable=True)
    
    # Metadata
    custom_fields = Column(JSONB, nullable=True, default=dict)
    
    # Relationships
    employee_contra_account = relationship(
        "GLAccount", 
        foreign_keys=[employee_contra_account_id]
    )
    employer_contra_account = relationship(
        "GLAccount", 
        foreign_keys=[employer_contra_account_id]
    )
    
    def __repr__(self):
        return f"<BenefitPlan {self.plan_code}: {self.plan_name}>"
    
    @property
    def is_current(self):
        """Check if the benefit plan is currently active."""
        today = date.today()
        return (self.is_active and 
                self.effective_date <= today and 
                (self.expiration_date is None or today <= self.expiration_date))


class PayPeriod(PayrollBase, Base):
    """Pay periods for payroll processing."""
    __tablename__ = "payroll_pay_periods"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # Period identification
    period_name = Column(String(100), nullable=False, index=True)
    period_description = Column(Text, nullable=True)
    
    # Date range
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=False, index=True)
    pay_date = Column(Date, nullable=False, index=True)
    
    # Period type
    period_type = Column(
        Enum('WEEKLY', 'BIWEEKLY', 'SEMIMONTHLY', 'MONTHLY', 'QUARTERLY', 'ANNUAL', 'CUSTOM', 
             name='pay_period_type_enum'),
        nullable=False
    )
    
    # Status
    is_open = Column(Boolean, default=True, nullable=False, index=True)
    is_processed = Column(Boolean, default=False, nullable=False, index=True)
    is_closed = Column(Boolean, default=False, nullable=False, index=True)
    
    # Processing information
    processed_at = Column(DateTime, nullable=True)
    processed_by_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_employees.id'), 
        nullable=True,
        index=True
    )
    
    # Relationships
    processed_by = relationship("Employee")
    payroll_runs = relationship("PayrollRun", back_populates="pay_period")
    
    def __repr__(self):
        return f"<PayPeriod {self.period_name}: {self.start_date} to {self.end_date}>"
    
    @property
    def is_current(self):
        """Check if this is the current pay period."""
        today = date.today()
        return self.start_date <= today <= self.end_date
    
    @property
    def is_future(self):
        """Check if this is a future pay period."""
        return date.today() < self.start_date
    
    @property
    def is_past(self):
        """Check if this is a past pay period."""
        return date.today() > self.end_date
    
    def close(self, processed_by):
        """Close the pay period."""
        if not self.is_closed:
            self.is_open = False
            self.is_processed = True
            self.is_closed = True
            self.processed_at = datetime.utcnow()
            self.processed_by_id = processed_by.id if hasattr(processed_by, 'id') else processed_by
