"""
Payslip models for the Payroll module.
"""
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import Column, Date, Enum, ForeignKey, Numeric, String, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

<<<<<<< HEAD:backend/app/modules/core_financials/payroll/models/payslip.py
from app.core.database import Base
=======
from app.core.db.base import Base
>>>>>>> e96df7278ce4216131b6c65d411c0723f4de7f91:backend/app/models/payslip.py
from app.modules.core_financials.payroll.models.base import PayrollBase


class Payslip(PayrollBase, Base):
    """Payslip model representing an employee's payment details for a pay period."""
    __tablename__ = "payroll_payslips"

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
    pay_period_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_pay_periods.id'), 
        nullable=False,
        index=True
    )
    
    # Payslip details
    payslip_number = Column(String(50), unique=True, index=True, nullable=False)
    issue_date = Column(Date, default=date.today, nullable=False)
    payment_date = Column(Date, nullable=False)
    
    # Working days/hours
    working_days = Column(Numeric(5, 2), default=0, nullable=False)  # Calendar days in period
    paid_days = Column(Numeric(5, 2), default=0, nullable=False)     # Days paid (excl. leaves)
    regular_hours = Column(Numeric(8, 2), default=0, nullable=False)  # Regular working hours
    overtime_hours = Column(Numeric(8, 2), default=0, nullable=False) # Overtime hours
    
    # Earnings
    basic_salary = Column(Numeric(15, 2), default=0, nullable=False)
    overtime_pay = Column(Numeric(15, 2), default=0, nullable=False)
    bonuses = Column(Numeric(15, 2), default=0, nullable=False)
    allowances = Column(Numeric(15, 2), default=0, nullable=False)
    other_earnings = Column(Numeric(15, 2), default=0, nullable=False)
    gross_pay = Column(Numeric(15, 2), default=0, nullable=False)
    
    # Deductions
    tax_deductions = Column(Numeric(15, 2), default=0, nullable=False)
    social_security = Column(Numeric(15, 2), default=0, nullable=False)
    health_insurance = Column(Numeric(15, 2), default=0, nullable=False)
    retirement_contributions = Column(Numeric(15, 2), default=0, nullable=False)
    loan_repayments = Column(Numeric(15, 2), default=0, nullable=False)
    other_deductions = Column(Numeric(15, 2), default=0, nullable=False)
    total_deductions = Column(Numeric(15, 2), default=0, nullable=False)
    
    # Net pay and payment
    net_pay = Column(Numeric(15, 2), default=0, nullable=False)
    currency = Column(String(3), default='USD', nullable=False)
    payment_method = Column(String(50), nullable=True)
    payment_reference = Column(String(100), nullable=True)
    
    # Status
    status = Column(
        Enum('DRAFT', 'PENDING', 'APPROVED', 'PROCESSED', 'PAID', 'CANCELLED', 'REJECTED',
             name='payslip_status_enum'),
        default='DRAFT',
        nullable=False,
        index=True
    )
    
    # Approval workflow
    is_approved = Column(Boolean, default=False, nullable=False)
    approved_at = Column(Date, nullable=True)
    approved_by = Column(String(50), nullable=True)
    
    # Payment processing
    is_paid = Column(Boolean, default=False, nullable=False)
    paid_at = Column(Date, nullable=True)
    payment_receipt_number = Column(String(50), nullable=True)
    
    # Notes and attachments
    notes = Column(Text, nullable=True)
    attachment_url = Column(String(255), nullable=True)
    
    # Relationships
    employee = relationship("Employee", back_populates="payslips")
    pay_period = relationship("PayPeriod", back_populates="payslips")
    earnings = relationship("PayslipEarning", back_populates="payslip", cascade="all, delete-orphan")
    deductions = relationship("PayslipDeduction", back_populates="payslip", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Payslip {self.payslip_number} - {self.employee.full_name if self.employee else 'Unknown'} ({self.pay_period.name if self.pay_period else 'No Period'})>"
    
    def calculate_totals(self):
        """Calculate all totals based on earnings and deductions."""
        # Sum up all earnings
        total_earnings = sum(
            [self.basic_salary, self.overtime_pay, self.bonuses, 
             self.allowances, self.other_earnings],
            Decimal('0.00')
        )
        
        # Sum up all deductions
        total_deductions = sum(
            [self.tax_deductions, self.social_security, self.health_insurance,
             self.retirement_contributions, self.loan_repayments, self.other_deductions],
            Decimal('0.00')
        )
        
        # Update fields
        self.gross_pay = total_earnings
        self.total_deductions = total_deductions
        self.net_pay = self.gross_pay - self.total_deductions
    
    @property
    def is_overdue(self):
        """Check if the payment is overdue."""
        if self.is_paid:
            return False
        return date.today() > self.payment_date
    
    def get_status_display(self):
        """Return a user-friendly status name."""
        status_map = {
            'DRAFT': 'Draft',
            'PENDING': 'Pending Approval',
            'APPROVED': 'Approved',
            'PROCESSED': 'Processed',
            'PAID': 'Paid',
            'CANCELLED': 'Cancelled',
            'REJECTED': 'Rejected'
        }
        return status_map.get(self.status, self.status)


class PayslipEarning(PayrollBase, Base):
    """Individual earning line items on a payslip."""
    __tablename__ = "payroll_payslip_earnings"
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # References
    payslip_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_payslips.id'), 
        nullable=False,
        index=True
    )
    
    # Earning details
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    amount = Column(Numeric(15, 2), nullable=False)
    quantity = Column(Numeric(10, 2), default=1, nullable=False)
    rate = Column(Numeric(15, 2), nullable=True)  # Rate per unit (hour, day, etc.)
    unit = Column(String(20), nullable=True)      # e.g., 'HOUR', 'DAY', 'MONTH', 'UNIT'
    is_taxable = Column(Boolean, default=True, nullable=False)
    
    # Categorization
    earning_type = Column(
        Enum('REGULAR', 'OVERTIME', 'BONUS', 'ALLOWANCE', 'COMMISSION', 'REIMBURSEMENT', 'OTHER',
             name='earning_type_enum'),
        nullable=False
    )
    
    # Relationships
    payslip = relationship("Payslip", back_populates="earnings")
    
    def __repr__(self):
        return f"<PayslipEarning {self.name}: {self.amount} {self.unit or ''}>"


class PayslipDeduction(PayrollBase, Base):
    """Individual deduction line items on a payslip."""
    __tablename__ = "payroll_payslip_deductions"
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # References
    payslip_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_payslips.id'), 
        nullable=False,
        index=True
    )
    
    # Deduction details
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    amount = Column(Numeric(15, 2), nullable=False)
    is_pretax = Column(Boolean, default=False, nullable=False)  # If deduction is pre-tax
    is_statutory = Column(Boolean, default=False, nullable=False)  # If required by law
    
    # Categorization
    deduction_type = Column(
        Enum('TAX', 'SOCIAL_SECURITY', 'HEALTH_INSURANCE', 'RETIREMENT', 'LOAN', 'ADVANCE', 'OTHER',
             name='deduction_type_enum'),
        nullable=False
    )
    
    # Relationships
    payslip = relationship("Payslip", back_populates="deductions")
    
    def __repr__(self):
        return f"<PayslipDeduction {self.name}: {self.amount}>"
