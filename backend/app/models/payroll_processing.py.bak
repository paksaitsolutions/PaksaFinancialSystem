"""
Payroll processing models for the Payroll module.
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


class PayrollRunStatus(PyEnum):
    """Status of a payroll run."""
    DRAFT = "DRAFT"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    PAID = "PAID"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"


class PayrollRunType(PyEnum):
    """Type of payroll run."""
    REGULAR = "REGULAR"
    BONUS = "BONUS"
    COMMISSION = "COMMISSION"
    TERMINATION = "TERMINATION"
    ADJUSTMENT = "ADJUSTMENT"
    SUPPLEMENTAL = "SUPPLEMENTAL"
    OFF_CYCLE = "OFF_CYCLE"
    TAX_ADJUSTMENT = "TAX_ADJUSTMENT"
    OTHER = "OTHER"


class PayrollRun(PayrollBase, Base):
    """Represents a payroll processing run for a specific pay period."""
    __tablename__ = "payroll_runs"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # Payroll run identification
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    payroll_run_number = Column(String(50), unique=True, index=True, nullable=False)
    
    # Pay period details
    pay_period_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_pay_periods.id'), 
        nullable=False,
        index=True
    )
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=False, index=True)
    pay_date = Column(Date, nullable=False, index=True)
    
    # Run type and status
    run_type = Column(
        Enum(PayrollRunType, name='payroll_run_type_enum'),
        default=PayrollRunType.REGULAR,
        nullable=False
    )
    status = Column(
        Enum(PayrollRunStatus, name='payroll_run_status_enum'),
        default=PayrollRunStatus.DRAFT,
        nullable=False,
        index=True
    )
    
    # Totals
    total_gross_pay = Column(Numeric(15, 2), default=0, nullable=False)
    total_net_pay = Column(Numeric(15, 2), default=0, nullable=False)
    total_taxes = Column(Numeric(15, 2), default=0, nullable=False)
    total_deductions = Column(Numeric(15, 2), default=0, nullable=False)
    total_benefits = Column(Numeric(15, 2), default=0, nullable=False)
    total_reimbursements = Column(Numeric(15, 2), default=0, nullable=False)
    
    # Employee counts
    employee_count = Column(Integer, default=0, nullable=False)
    processed_employee_count = Column(Integer, default=0, nullable=False)
    
    # Approval workflow
    submitted_at = Column(DateTime, nullable=True)
    submitted_by_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_employees.id'), 
        nullable=True,
        index=True
    )
    approved_at = Column(DateTime, nullable=True)
    approved_by_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_employees.id'), 
        nullable=True,
        index=True
    )
    processed_at = Column(DateTime, nullable=True)
    processed_by_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_employees.id'), 
        nullable=True,
        index=True
    )
    completed_at = Column(DateTime, nullable=True)
    
    # Payment information
    payment_method = Column(String(50), nullable=True)  # e.g., DIRECT_DEPOSIT, CHECK, WIRE_TRANSFER
    bank_account_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_bank_accounts.id'), 
        nullable=True,
        index=True
    )
    payment_reference = Column(String(100), nullable=True)
    
    # Metadata
    notes = Column(Text, nullable=True)
    custom_fields = Column(JSONB, nullable=True, default=dict)
    
    # Relationships
    pay_period = relationship("PayPeriod", back_populates="payroll_runs")
    payroll_entries = relationship("PayrollEntry", back_populates="payroll_run", cascade="all, delete-orphan")
    submitted_by = relationship("Employee", foreign_keys=[submitted_by_id])
    approved_by = relationship("Employee", foreign_keys=[approved_by_id])
    processed_by = relationship("Employee", foreign_keys=[processed_by_id])
    bank_account = relationship("BankAccount")
    
    def __repr__(self):
        return f"<PayrollRun {self.payroll_run_number}: {self.start_date} - {self.end_date}>"
    
    @property
    def is_editable(self):
        """Check if the payroll run can be edited."""
        return self.status in [PayrollRunStatus.DRAFT, PayrollRunStatus.PENDING_APPROVAL]
    
    @property
    def is_approved(self):
        """Check if the payroll run is approved."""
        return self.status in [PayrollRunStatus.APPROVED, PayrollRunStatus.PROCESSING, 
                             PayrollRunStatus.COMPLETED, PayrollRunStatus.PAID]
    
    @property
    def is_processed(self):
        """Check if the payroll run has been processed."""
        return self.status in [PayrollRunStatus.PROCESSING, PayrollRunStatus.COMPLETED, PayrollRunStatus.PAID]
    
    @property
    def is_paid(self):
        """Check if the payroll run has been paid."""
        return self.status == PayrollRunStatus.PAID
    
    def calculate_totals(self):
        """Calculate payroll run totals from payroll entries."""
        self.total_gross_pay = sum((entry.gross_pay for entry in self.payroll_entries), Decimal('0.00'))
        self.total_net_pay = sum((entry.net_pay for entry in self.payroll_entries), Decimal('0.00'))
        self.total_taxes = sum((entry.total_taxes for entry in self.payroll_entries), Decimal('0.00'))
        self.total_deductions = sum((entry.total_deductions for entry in self.payroll_entries), Decimal('0.00'))
        self.total_benefits = sum((entry.total_benefits for entry in self.payroll_entries), Decimal('0.00'))
        self.total_reimbursements = sum((entry.total_reimbursements for entry in self.payroll_entries), Decimal('0.00'))
        
        # Update employee counts
        self.employee_count = len(self.payroll_entries)
        self.processed_employee_count = sum(1 for entry in self.payroll_entries 
                                          if entry.status in ['APPROVED', 'PROCESSED', 'PAID'])
    
    def submit_for_approval(self, submitted_by):
        """Submit the payroll run for approval."""
        if self.status == PayrollRunStatus.DRAFT:
            self.status = PayrollRunStatus.PENDING_APPROVAL
            self.submitted_at = datetime.utcnow()
            self.submitted_by_id = submitted_by.id if hasattr(submitted_by, 'id') else submitted_by
    
    def approve(self, approved_by):
        """Approve the payroll run."""
        if self.status == PayrollRunStatus.PENDING_APPROVAL:
            self.status = PayrollRunStatus.APPROVED
            self.approved_at = datetime.utcnow()
            self.approved_by_id = approved_by.id if hasattr(approved_by, 'id') else approved_by
    
    def process(self, processed_by):
        """Mark the payroll run as processing."""
        if self.status == PayrollRunStatus.APPROVED:
            self.status = PayrollRunStatus.PROCESSING
            self.processed_at = datetime.utcnow()
            self.processed_by_id = processed_by.id if hasattr(processed_by, 'id') else processed_by
    
    def complete(self):
        """Mark the payroll run as completed."""
        if self.status == PayrollRunStatus.PROCESSING:
            self.status = PayrollRunStatus.COMPLETED
            self.completed_at = datetime.utcnow()
    
    def mark_as_paid(self):
        """Mark the payroll run as paid."""
        if self.status in [PayrollRunStatus.COMPLETED, PayrollRunStatus.PROCESSING]:
            self.status = PayrollRunStatus.PAID
            if not self.completed_at:
                self.completed_at = datetime.utcnow()
    
    def cancel(self):
        """Cancel the payroll run."""
        if self.status in [PayrollRunStatus.DRAFT, PayrollRunStatus.PENDING_APPROVAL]:
            self.status = PayrollRunStatus.CANCELLED


class PayrollEntryStatus(PyEnum):
    """Status of a payroll entry."""
    DRAFT = "DRAFT"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    PROCESSING = "PROCESSING"
    PAID = "PAID"
    CANCELLED = "CANCELLED"
    ERROR = "ERROR"


class PayrollEntry(PayrollBase, Base):
    """Represents an employee's payroll entry in a payroll run."""
    __tablename__ = "payroll_entries"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # References
    payroll_run_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_runs.id'), 
        nullable=False,
        index=True
    )
    employee_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_employees.id'), 
        nullable=False,
        index=True
    )
    timesheet_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_timesheets.id'), 
        nullable=True,
        index=True
    )
    
    # Pay details
    pay_rate = Column(Numeric(15, 2), nullable=False)
    pay_rate_type = Column(
        Enum('SALARY', 'HOURLY', 'DAILY', 'WEEKLY', 'BIWEEKLY', 'MONTHLY', 'ANNUAL', 'PIECEWORK', 'COMMISSION', 
             name='pay_rate_type_enum'),
        nullable=False
    )
    pay_frequency = Column(
        Enum('WEEKLY', 'BIWEEKLY', 'SEMIMONTHLY', 'MONTHLY', 'QUARTERLY', 'ANNUAL', 'CUSTOM', 
             name='pay_frequency_enum'),
        nullable=False
    )
    
    # Hours and amounts
    regular_hours = Column(Numeric(8, 2), default=0, nullable=False)
    overtime_hours = Column(Numeric(8, 2), default=0, nullable=False)
    double_overtime_hours = Column(Numeric(8, 2), default=0, nullable=False)
    other_hours = Column(Numeric(8, 2), default=0, nullable=False)
    
    regular_rate = Column(Numeric(15, 2), default=0, nullable=False)
    overtime_rate = Column(Numeric(15, 2), default=0, nullable=False)
    double_overtime_rate = Column(Numeric(15, 2), default=0, nullable=False)
    
    # Earnings
    regular_pay = Column(Numeric(15, 2), default=0, nullable=False)
    overtime_pay = Column(Numeric(15, 2), default=0, nullable=False)
    double_overtime_pay = Column(Numeric(15, 2), default=0, nullable=False)
    bonus_pay = Column(Numeric(15, 2), default=0, nullable=False)
    commission_pay = Column(Numeric(15, 2), default=0, nullable=False)
    reimbursement_pay = Column(Numeric(15, 2), default=0, nullable=False)
    other_earnings = Column(Numeric(15, 2), default=0, nullable=False)
    
    # Deductions and taxes
    tax_withholdings = Column(Numeric(15, 2), default=0, nullable=False)
    benefit_deductions = Column(Numeric(15, 2), default=0, nullable=False)
    other_deductions = Column(Numeric(15, 2), default=0, nullable=False)
    
    # Totals
    gross_pay = Column(Numeric(15, 2), default=0, nullable=False)
    total_taxes = Column(Numeric(15, 2), default=0, nullable=False)
    total_deductions = Column(Numeric(15, 2), default=0, nullable=False)
    total_benefits = Column(Numeric(15, 2), default=0, nullable=False)
    total_reimbursements = Column(Numeric(15, 2), default=0, nullable=False)
    net_pay = Column(Numeric(15, 2), default=0, nullable=False)
    
    # YTD totals (as of this payroll)
    ytd_gross_pay = Column(Numeric(15, 2), default=0, nullable=False)
    ytd_taxes = Column(Numeric(15, 2), default=0, nullable=False)
    ytd_deductions = Column(Numeric(15, 2), default=0, nullable=False)
    ytd_benefits = Column(Numeric(15, 2), default=0, nullable=False)
    ytd_net_pay = Column(Numeric(15, 2), default=0, nullable=False)
    
    # Status
    status = Column(
        Enum(PayrollEntryStatus, name='payroll_entry_status_enum'),
        default=PayrollEntryStatus.DRAFT,
        nullable=False,
        index=True
    )
    
    # Payment information
    payment_method = Column(String(50), nullable=True)  # Overrides employee default if set
    bank_account_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_bank_accounts.id'), 
        nullable=True,
        index=True
    )
    payment_reference = Column(String(100), nullable=True)
    
    # Metadata
    notes = Column(Text, nullable=True)
    custom_fields = Column(JSONB, nullable=True, default=dict)
    
    # Relationships
    payroll_run = relationship("PayrollRun", back_populates="payroll_entries")
    employee = relationship("Employee", back_populates="payroll_entries")
    timesheet = relationship("Timesheet")
    bank_account = relationship("BankAccount")
    earnings = relationship("PayrollEarning", back_populates="payroll_entry", cascade="all, delete-orphan")
    deductions = relationship("PayrollDeduction", back_populates="payroll_entry", cascade="all, delete-orphan")
    taxes = relationship("PayrollTax", back_populates="payroll_entry", cascade="all, delete-orphan")
    benefits = relationship("PayrollBenefit", back_populates="payroll_entry", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<PayrollEntry {self.employee.full_name} - {self.net_pay}>"
