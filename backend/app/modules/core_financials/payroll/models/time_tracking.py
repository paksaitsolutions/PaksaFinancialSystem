"""
Time tracking and project time allocation models for the Payroll module.
"""
from datetime import datetime, date, time, timedelta
from decimal import Decimal
from enum import Enum as PyEnum
from sqlalchemy import Column, Date, DateTime, Enum, ForeignKey, Numeric, String, Text, Boolean, Integer, Time, Interval, Table
from sqlalchemy.orm import relationship, validates
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

from app.core.database import Base
from app.modules.core_financials.payroll.models.base import PayrollBase


class TimeEntryType(PyEnum):
    """Types of time entries that can be recorded."""
    REGULAR = "REGULAR"
    OVERTIME = "OVERTIME"
    HOLIDAY = "HOLIDAY"
    VACATION = "VACATION"
    SICK_LEAVE = "SICK_LEAVE"
    PERSONAL_LEAVE = "PERSONAL_LEAVE"
    BEREAVEMENT = "BEREAVEMENT"
    JURY_DUTY = "JURY_DUTY"
    MILITARY_LEAVE = "MILITARY_LEAVE"
    TRAINING = "TRAINING"
    MEETING = "MEETING"
    BREAK = "BREAK"
    MEAL = "MEAL"
    UNAUTHORIZED = "UNAUTHORIZED"
    OTHER = "OTHER"


class TimeEntryStatus(PyEnum):
    """Status of a time entry."""
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PROCESSED = "PROCESSED"
    PAID = "PAID"


class TimeTrackingProject(PayrollBase, Base):
    """Projects or tasks that employees can log time against."""
    __tablename__ = "payroll_time_tracking_projects"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # Project identification
    name = Column(String(200), nullable=False, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Project details
    client_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_clients.id'), 
        nullable=True,
        index=True
    )
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    is_billable = Column(Boolean, default=True, nullable=False)
    billing_rate = Column(Numeric(12, 2), nullable=True)  # Default billing rate per hour
    
    # Budget tracking
    budget_hours = Column(Numeric(10, 2), nullable=True)
    budget_amount = Column(Numeric(15, 2), nullable=True)
    
    # Status
    status = Column(
        Enum('ACTIVE', 'ON_HOLD', 'COMPLETED', 'CANCELLED', name='project_status_enum'),
        default='ACTIVE',
        nullable=False,
        index=True
    )
    
    # Metadata
    custom_fields = Column(JSONB, nullable=True, default=dict)
    
    # Relationships
    client = relationship("Client", backref="time_tracking_projects")
    tasks = relationship("TimeTrackingTask", back_populates="project", cascade="all, delete-orphan")
    time_entries = relationship("TimeEntry", back_populates="project")
    
    def __repr__(self):
        return f"<TimeTrackingProject {self.code}: {self.name}>"
    
    @property
    def total_logged_hours(self):
        """Calculate total hours logged against this project."""
        return sum(
            (entry.hours for entry in self.time_entries 
             if entry.status in ['APPROVED', 'PROCESSED', 'PAID']),
            Decimal('0.00')
        )
    
    @property
    def remaining_budget_hours(self):
        """Calculate remaining budget hours."""
        if self.budget_hours is None:
            return None
        return max(Decimal('0.00'), self.budget_hours - self.total_logged_hours)
    
    @property
    def budget_utilization(self):
        """Calculate budget utilization percentage."""
        if not self.budget_hours or self.budget_hours == 0:
            return None
        return (self.total_logged_hours / self.budget_hours) * 100


class TimeTrackingTask(PayrollBase, Base):
    """Tasks within a project that employees can log time against."""
    __tablename__ = "payroll_time_tracking_tasks"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # References
    project_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_time_tracking_projects.id'), 
        nullable=False,
        index=True
    )
    parent_task_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_time_tracking_tasks.id'), 
        nullable=True,
        index=True
    )
    
    # Task identification
    name = Column(String(200), nullable=False, index=True)
    code = Column(String(50), index=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Task details
    is_billable = Column(Boolean, default=True, nullable=False)
    billing_rate = Column(Numeric(12, 2), nullable=True)  # Overrides project rate if set
    
    # Budget tracking
    budget_hours = Column(Numeric(10, 2), nullable=True)
    
    # Status
    status = Column(
        Enum('NOT_STARTED', 'IN_PROGRESS', 'ON_HOLD', 'COMPLETED', 'CANCELLED', name='task_status_enum'),
        default='NOT_STARTED',
        nullable=False,
        index=True
    )
    
    # Relationships
    project = relationship("TimeTrackingProject", back_populates="tasks")
    parent_task = relationship("TimeTrackingTask", remote_side=[id], backref="subtasks")
    time_entries = relationship("TimeEntry", back_populates="task")
    
    def __repr__(self):
        return f"<TimeTrackingTask {self.code}: {self.name}>"
    
    @property
    def full_code(self):
        """Get the full task code including parent project code."""
        return f"{self.project.code}-{self.code}" if self.project else self.code
    
    @property
    def total_logged_hours(self):
        """Calculate total hours logged against this task and its subtasks."""
        # Direct time entries on this task
        direct_hours = sum(
            (entry.hours for entry in self.time_entries 
             if entry.status in ['APPROVED', 'PROCESSED', 'PAID']),
            Decimal('0.00')
        )
        
        # Hours from subtasks
        subtask_hours = sum(
            (subtask.total_logged_hours for subtask in self.subtasks),
            Decimal('0.00')
        )
        
        return direct_hours + subtask_hours


class TimeEntry(PayrollBase, Base):
    """Records time spent by employees on projects and tasks."""
    __tablename__ = "payroll_time_entries"

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
    project_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_time_tracking_projects.id'), 
        nullable=False,
        index=True
    )
    task_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_time_tracking_tasks.id'), 
        nullable=True,
        index=True
    )
    timesheet_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_timesheets.id'), 
        nullable=True,
        index=True
    )
    
    # Time tracking
    entry_date = Column(Date, nullable=False, index=True)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=True)
    
    # Duration in hours (can be entered manually or calculated)
    hours = Column(Numeric(5, 2), nullable=False)
    
    # Entry type and status
    entry_type = Column(
        Enum(TimeEntryType, name='time_entry_type_enum'),
        default=TimeEntryType.REGULAR,
        nullable=False
    )
    status = Column(
        Enum(TimeEntryStatus, name='time_entry_status_enum'),
        default=TimeEntryStatus.DRAFT,
        nullable=False,
        index=True
    )
    
    # Billing information
    is_billable = Column(Boolean, default=True, nullable=False)
    billing_rate = Column(Numeric(12, 2), nullable=True)  # Overrides project/task rate if set
    billing_amount = Column(Numeric(15, 2), nullable=True)  # Calculated: hours * billing_rate
    
    # Approval
    approved_by_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_employees.id'), 
        nullable=True,
        index=True
    )
    approved_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Metadata
    description = Column(Text, nullable=True)
    location = Column(String(100), nullable=True)  # GPS coordinates or location name
    is_remote = Column(Boolean, default=False, nullable=False)
    custom_fields = Column(JSONB, nullable=True, default=dict)
    
    # System fields
    created_by_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_employees.id'), 
        nullable=False,
        index=True
    )
    last_modified_by_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_employees.id'), 
        nullable=True,
        index=True
    )
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id], backref="time_entries")
    project = relationship("TimeTrackingProject", back_populates="time_entries")
    task = relationship("TimeTrackingTask", back_populates="time_entries")
    timesheet = relationship("Timesheet", back_populates="time_entries")
    approved_by = relationship("Employee", foreign_keys=[approved_by_id])
    created_by = relationship("Employee", foreign_keys=[created_by_id])
    last_modified_by = relationship("Employee", foreign_keys=[last_modified_by_id])
    
    def __repr__(self):
        return f"<TimeEntry {self.employee.full_name} - {self.entry_date} ({self.hours}h)>"
    
    @property
    def is_editable(self):
        """Check if the time entry can be edited."""
        return self.status in [TimeEntryStatus.DRAFT, TimeEntryStatus.SUBMITTED, TimeEntryStatus.REJECTED]
    
    @property
    def is_approved(self):
        """Check if the time entry is approved."""
        return self.status == TimeEntryStatus.APPROVED
    
    def calculate_hours(self):
        """Calculate hours based on start and end times."""
        if not self.start_time or not self.end_time:
            return
            
        # Calculate duration in hours
        start_dt = datetime.combine(self.entry_date, self.start_time)
        end_dt = datetime.combine(
            self.entry_date + timedelta(days=1) if self.end_time < self.start_time else self.entry_date,
            self.end_time
        )
        
        duration_seconds = (end_dt - start_dt).total_seconds()
        self.hours = Decimal(str(duration_seconds / 3600)).quantize(Decimal('0.01'))
        
        # Update billing amount if needed
        self._calculate_billing()
    
    def _calculate_billing(self):
        """Calculate the billing amount based on hours and rate."""
        if not self.is_billable:
            self.billing_amount = Decimal('0.00')
            return
            
        # Determine the billing rate (entry > task > project > 0)
        rate = self.billing_rate
        if rate is None and self.task and self.task.billing_rate is not None:
            rate = self.task.billing_rate
        if rate is None and self.project and self.project.billing_rate is not None:
            rate = self.project.billing_rate
        if rate is None:
            rate = Decimal('0.00')
            
        self.billing_amount = (self.hours * rate).quantize(Decimal('0.01'))
    
    def submit_for_approval(self):
        """Submit the time entry for approval."""
        if self.status == TimeEntryStatus.DRAFT:
            self.status = TimeEntryStatus.SUBMITTED
    
    def approve(self, approved_by, notes=None):
        """Approve the time entry."""
        if self.status in [TimeEntryStatus.SUBMITTED, TimeEntryStatus.REJECTED]:
            self.status = TimeEntryStatus.APPROVED
            self.approved_by_id = approved_by.id if hasattr(approved_by, 'id') else approved_by
            self.approved_at = datetime.utcnow()
            self.rejection_reason = None
    
    def reject(self, rejected_by, reason):
        """Reject the time entry with a reason."""
        if self.status == TimeEntryStatus.SUBMITTED:
            self.status = TimeEntryStatus.REJECTED
            self.rejection_reason = reason


class Timesheet(PayrollBase, Base):
    """A collection of time entries for a specific time period."""
    __tablename__ = "payroll_timesheets"

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
    
    # Time period
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=False, index=True)
    
    # Status
    status = Column(
        Enum('DRAFT', 'SUBMITTED', 'APPROVED', 'REJECTED', 'PROCESSED', 'PAID', name='timesheet_status_enum'),
        default='DRAFT',
        nullable=False,
        index=True
    )
    
    # Totals
    total_hours = Column(Numeric(8, 2), default=0, nullable=False)
    regular_hours = Column(Numeric(8, 2), default=0, nullable=False)
    overtime_hours = Column(Numeric(8, 2), default=0, nullable=False)
    
    # Billing
    total_billable_hours = Column(Numeric(8, 2), default=0, nullable=False)
    total_billing_amount = Column(Numeric(15, 2), default=0, nullable=False)
    
    # Approval
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
    rejected_at = Column(DateTime, nullable=True)
    rejected_by_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_employees.id'), 
        nullable=True,
        index=True
    )
    rejection_reason = Column(Text, nullable=True)
    
    # Processing
    processed_at = Column(DateTime, nullable=True)
    processed_by_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_employees.id'), 
        nullable=True,
        index=True
    )
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id], backref="timesheets")
    time_entries = relationship("TimeEntry", back_populates="timesheet")
    submitted_by = relationship("Employee", foreign_keys=[submitted_by_id])
    approved_by = relationship("Employee", foreign_keys=[approved_by_id])
    rejected_by = relationship("Employee", foreign_keys=[rejected_by_id])
    processed_by = relationship("Employee", foreign_keys=[processed_by_id])
    
    def __repr__(self):
        return f"<Timesheet {self.employee.full_name} - {self.start_date} to {self.end_date}>"
    
    @property
    def is_editable(self):
        """Check if the timesheet can be edited."""
        return self.status in ['DRAFT', 'REJECTED']
    
    @property
    def is_approved(self):
        """Check if the timesheet is approved."""
        return self.status == 'APPROVED'
    
    def calculate_totals(self):
        """Calculate totals based on time entries."""
        self.total_hours = sum((entry.hours for entry in self.time_entries), Decimal('0.00'))
        self.regular_hours = sum(
            (entry.hours for entry in self.time_entries 
             if entry.entry_type == TimeEntryType.REGULAR),
            Decimal('0.00')
        )
        self.overtime_hours = sum(
            (entry.hours for entry in self.time_entries 
             if entry.entry_type == TimeEntryType.OVERTIME),
            Decimal('0.00')
        )
        
        # Calculate billable totals
        billable_entries = [e for e in self.time_entries if e.is_billable and e.billing_amount is not None]
        self.total_billable_hours = sum((e.hours for e in billable_entries), Decimal('0.00'))
        self.total_billing_amount = sum((e.billing_amount for e in billable_entries), Decimal('0.00'))
    
    def submit(self, submitted_by):
        """Submit the timesheet for approval."""
        if self.status == 'DRAFT':
            self.status = 'SUBMITTED'
            self.submitted_at = datetime.utcnow()
            self.submitted_by_id = submitted_by.id if hasattr(submitted_by, 'id') else submitted_by
            
            # Update status of all time entries
            for entry in self.time_entries:
                if entry.status == TimeEntryStatus.DRAFT:
                    entry.status = TimeEntryStatus.SUBMITTED
    
    def approve(self, approved_by, notes=None):
        """Approve the timesheet."""
        if self.status == 'SUBMITTED':
            self.status = 'APPROVED'
            self.approved_at = datetime.utcnow()
            self.approved_by_id = approved_by.id if hasattr(approved_by, 'id') else approved_by
            self.rejection_reason = None
            
            # Update status of all time entries
            for entry in self.time_entries:
                if entry.status == TimeEntryStatus.SUBMITTED:
                    entry.status = TimeEntryStatus.APPROVED
                    entry.approved_by_id = self.approved_by_id
                    entry.approved_at = self.approved_at
    
    def reject(self, rejected_by, reason):
        """Reject the timesheet with a reason."""
        if self.status == 'SUBMITTED':
            self.status = 'REJECTED'
            self.rejected_at = datetime.utcnow()
            self.rejected_by_id = rejected_by.id if hasattr(rejected_by, 'id') else rejected_by
            self.rejection_reason = reason
    
    def process(self, processed_by):
        """Mark the timesheet as processed."""
        if self.status == 'APPROVED':
            self.status = 'PROCESSED'
            self.processed_at = datetime.utcnow()
            self.processed_by_id = processed_by.id if hasattr(processed_by, 'id') else processed_by
            
            # Update status of all time entries
            for entry in self.time_entries:
                if entry.status == TimeEntryStatus.APPROVED:
                    entry.status = TimeEntryStatus.PROCESSED
