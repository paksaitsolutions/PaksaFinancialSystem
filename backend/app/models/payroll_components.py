"""
Payroll component models for earnings, deductions, taxes, and benefits.
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


class TimesheetStatus(PyEnum):
    """Status of a timesheet."""
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PROCESSED = "PROCESSED"


class Timesheet(PayrollBase, Base):
    """Employee timesheet for tracking work hours and leave."""
    __tablename__ = "payroll_timesheets"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # Timesheet identification
    timesheet_number = Column(String(50), unique=True, index=True, nullable=False)
    employee_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_employees.id'), 
        nullable=False,
        index=True
    )
    
    # Time period
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=False, index=True)
    
    # Status
    status = Column(
        Enum(TimesheetStatus, name='timesheet_status_enum'),
        default=TimesheetStatus.DRAFT,
        nullable=False,
        index=True
    )
    
    # Hours tracking
    regular_hours = Column(Numeric(8, 2), default=0, nullable=False)
    overtime_hours = Column(Numeric(8, 2), default=0, nullable=False)
    double_overtime_hours = Column(Numeric(8, 2), default=0, nullable=False)
    vacation_hours = Column(Numeric(8, 2), default=0, nullable=False)
    sick_hours = Column(Numeric(8, 2), default=0, nullable=False)
    holiday_hours = Column(Numeric(8, 2), default=0, nullable=False)
    other_hours = Column(Numeric(8, 2), default=0, nullable=False)
    
    # Approval workflow
    submitted_at = Column(DateTime, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    approved_by_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_employees.id'), 
        nullable=True,
        index=True
    )
    rejected_at = Column(DateTime, nullable=True)
    rejected_reason = Column(Text, nullable=True)
    
    # Metadata
    notes = Column(Text, nullable=True)
    custom_fields = Column(JSONB, nullable=True, default=dict)
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id], backref="timesheets")
    approved_by = relationship("Employee", foreign_keys=[approved_by_id])
    timesheet_entries = relationship("TimesheetEntry", back_populates="timesheet", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Timesheet {self.timesheet_number}: {self.employee_id} ({self.start_date} - {self.end_date})>"
    
    @property
    def total_hours(self):
        """Calculate total hours worked."""
        return (self.regular_hours + self.overtime_hours + self.double_overtime_hours + 
                self.vacation_hours + self.sick_hours + self.holiday_hours + self.other_hours)
    
    def submit(self):
        """Mark timesheet as submitted."""
        if self.status == TimesheetStatus.DRAFT:
            self.status = TimesheetStatus.SUBMITTED
            self.submitted_at = datetime.utcnow()
    
    def approve(self, approved_by):
        """Approve the timesheet."""
        if self.status == TimesheetStatus.SUBMITTED:
            self.status = TimesheetStatus.APPROVED
            self.approved_at = datetime.utcnow()
            self.approved_by_id = approved_by.id if hasattr(approved_by, 'id') else approved_by
    
    def reject(self, reason):
        """Reject the timesheet."""
        if self.status == TimesheetStatus.SUBMITTED:
            self.status = TimesheetStatus.REJECTED
            self.rejected_at = datetime.utcnow()
            self.rejected_reason = reason


class TimesheetEntry(PayrollBase, Base):
    """Individual entries within a timesheet."""
    __tablename__ = "payroll_timesheet_entries"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # Parent timesheet
    timesheet_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_timesheets.id'), 
        nullable=False,
        index=True
    )
    
    # Entry details
    entry_date = Column(Date, nullable=False, index=True)
    project_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_projects.id'), 
        nullable=True,
        index=True
    )
    task_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_tasks.id'), 
        nullable=True,
        index=True
    )
    
    # Time tracking
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    duration_minutes = Column(Integer, default=0, nullable=False)
    
    # Hours by type
    regular_hours = Column(Numeric(8, 2), default=0, nullable=False)
    overtime_hours = Column(Numeric(8, 2), default=0, nullable=False)
    double_overtime_hours = Column(Numeric(8, 2), default=0, nullable=False)
    vacation_hours = Column(Numeric(8, 2), default=0, nullable=False)
    sick_hours = Column(Numeric(8, 2), default=0, nullable=False)
    holiday_hours = Column(Numeric(8, 2), default=0, nullable=False)
    other_hours = Column(Numeric(8, 2), default=0, nullable=False)
    
    # Status
    is_billable = Column(Boolean, default=True, nullable=False)
    is_approved = Column(Boolean, default=False, nullable=False)
    
    # Metadata
    notes = Column(Text, nullable=True)
    custom_fields = Column(JSONB, nullable=True, default=dict)
    
    # Relationships
    timesheet = relationship("Timesheet", back_populates="timesheet_entries")
    project = relationship("Project")
    task = relationship("Task")
    
    def __repr__(self):
        return f"<TimesheetEntry {self.entry_date}: {self.duration_minutes} minutes>"
    
    @property
    def total_hours(self):
        """Calculate total hours for this entry."""
        return (self.regular_hours + self.overtime_hours + self.double_overtime_hours + 
                self.vacation_hours + self.sick_hours + self.holiday_hours + self.other_hours)


class PayrollEarning(PayrollBase, Base):
    """Earnings for a payroll entry."""
    __tablename__ = "payroll_earnings"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # Parent entry
    payroll_entry_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_entries.id'), 
        nullable=False,
        index=True
    )
    
    # Earning details
    earning_code_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_earning_codes.id'), 
        nullable=False,
        index=True
    )
    
    # Amount and rate
    rate = Column(Numeric(15, 4), nullable=False)
    quantity = Column(Numeric(15, 4), default=1, nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    
    # Tax impact
    is_taxable = Column(Boolean, default=True, nullable=False)
    is_pretax = Column(Boolean, default=False, nullable=False)
    
    # GL posting
    gl_account_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_gl_accounts.id'), 
        nullable=True,
        index=True
    )
    
    # Metadata
    description = Column(Text, nullable=True)
    custom_fields = Column(JSONB, nullable=True, default=dict)
    
    # Relationships
    payroll_entry = relationship("PayrollEntry", back_populates="earnings")
    earning_code = relationship("EarningCode")
    gl_account = relationship("GLAccount")
    
    def __repr__(self):
        return f"<PayrollEarning {self.earning_code_id}: {self.amount}>"


class PayrollDeduction(PayrollBase, Base):
    """Deductions for a payroll entry."""
    __tablename__ = "payroll_deductions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # Parent entry
    payroll_entry_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_entries.id'), 
        nullable=False,
        index=True
    )
    
    # Deduction details
    deduction_code_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_deduction_codes.id'), 
        nullable=False,
        index=True
    )
    
    # Amount and rate
    amount = Column(Numeric(15, 2), nullable=False)
    rate = Column(Numeric(7, 4), nullable=True)  # For percentage-based deductions
    
    # Tax impact
    is_pretax = Column(Boolean, default=False, nullable=False)
    affects_taxable_income = Column(Boolean, default=True, nullable=False)
    
    # GL posting
    gl_account_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_gl_accounts.id'), 
        nullable=True,
        index=True
    )
    
    # Metadata
    description = Column(Text, nullable=True)
    custom_fields = Column(JSONB, nullable=True, default=dict)
    
    # Relationships
    payroll_entry = relationship("PayrollEntry", back_populates="deductions")
    deduction_code = relationship("DeductionCode")
    gl_account = relationship("GLAccount")
    
    def __repr__(self):
        return f"<PayrollDeduction {self.deduction_code_id}: {self.amount}>"


class PayrollTax(PayrollBase, Base):
    """Tax calculations for a payroll entry."""
    __tablename__ = "payroll_taxes"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # Parent entry
    payroll_entry_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_entries.id'), 
        nullable=False,
        index=True
    )
    
    # Tax details
    tax_code_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_tax_codes.id'), 
        nullable=False,
        index=True
    )
    
    # Tax calculations
    taxable_amount = Column(Numeric(15, 2), nullable=False)
    tax_amount = Column(Numeric(15, 2), nullable=False)
    employer_tax_amount = Column(Numeric(15, 2), default=0, nullable=False)
    
    # GL posting
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
    
    # Metadata
    description = Column(Text, nullable=True)
    custom_fields = Column(JSONB, nullable=True, default=dict)
    
    # Relationships
    payroll_entry = relationship("PayrollEntry", back_populates="taxes")
    tax_code = relationship("TaxCode")
    employee_liability_account = relationship(
        "GLAccount", 
        foreign_keys=[employee_liability_account_id]
    )
    employer_liability_account = relationship(
        "GLAccount", 
        foreign_keys=[employer_liability_account_id]
    )
    
    def __repr__(self):
        return f"<PayrollTax {self.tax_code_id}: {self.tax_amount}>"


class PayrollBenefit(PayrollBase, Base):
    """Benefit contributions for a payroll entry."""
    __tablename__ = "payroll_benefits"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # Parent entry
    payroll_entry_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_entries.id'), 
        nullable=False,
        index=True
    )
    
    # Benefit details
    benefit_plan_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_benefit_plans.id'), 
        nullable=False,
        index=True
    )
    
    # Contributions
    employee_contribution = Column(Numeric(15, 2), default=0, nullable=False)
    employer_contribution = Column(Numeric(15, 2), default=0, nullable=False)
    
    # GL posting
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
    
    # Metadata
    description = Column(Text, nullable=True)
    custom_fields = Column(JSONB, nullable=True, default=dict)
    
    # Relationships
    payroll_entry = relationship("PayrollEntry", back_populates="benefits")
    benefit_plan = relationship("BenefitPlan")
    employee_contra_account = relationship(
        "GLAccount", 
        foreign_keys=[employee_contra_account_id]
    )
    employer_contra_account = relationship(
        "GLAccount", 
        foreign_keys=[employer_contra_account_id]
    )
    
    def __repr__(self):
        return f"<PayrollBenefit {self.benefit_plan_id}: Employee={self.employee_contribution}, Employer={self.employer_contribution}>"
