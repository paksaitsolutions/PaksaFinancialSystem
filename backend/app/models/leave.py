"""
Leave and Attendance models for the Payroll module.
"""
from datetime import date, datetime, timedelta
from decimal import Decimal
from sqlalchemy import Column, Date, DateTime, Enum, ForeignKey, Numeric, String, Text, Boolean, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.core.db.base import Base
from app.modules.core_financials.payroll.models.base import PayrollBase


class LeavePolicy(PayrollBase, Base):
    """Leave policy model defining different types of leave and their rules."""
    __tablename__ = "payroll_leave_policies"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # Policy identification
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    policy_code = Column(String(50), unique=True, index=True, nullable=False)
    
    # Policy type
    leave_type = Column(
        Enum('PAID_LEAVE', 'SICK_LEAVE', 'VACATION', 'MATERNITY_LEAVE', 'PATERNITY_LEAVE',
             'BEREAVEMENT_LEAVE', 'COMPASSIONATE_LEAVE', 'STUDY_LEAVE', 'SABBATICAL',
             'UNPAID_LEAVE', 'OTHER', name='leave_type_enum'),
        nullable=False
    )
    
    # Accrual rules
    accrual_method = Column(
        Enum('NONE', 'ANNUAL', 'MONTHLY', 'HOURLY', 'CUSTOM', name='accrual_method_enum'),
        default='NONE',
        nullable=False
    )
    
    # Accrual details
    days_per_year = Column(Numeric(5, 2), default=0, nullable=False)  # For annual accrual
    max_carryover_days = Column(Numeric(5, 2), nullable=True)  # Max days that can be carried over
    max_balance = Column(Numeric(5, 2), nullable=True)  # Maximum balance that can be accrued
    
    # Carryover rules
    carryover_expiry_days = Column(Integer, nullable=True)  # Days after which carryover expires
    carryover_expiry_date = Column(Date, nullable=True)  # Specific date when carryover expires (e.g., end of fiscal year)
    
    # Approval workflow
    requires_approval = Column(Boolean, default=True, nullable=False)
    approval_workflow_id = Column(UUID(as_uuid=True), nullable=True)  # Reference to workflow definition
    
    # Documentation requirements
    requires_documentation = Column(Boolean, default=False, nullable=False)
    documentation_notes = Column(Text, nullable=True)
    
    # Pay impact
    is_paid = Column(Boolean, default=True, nullable=False)
    pay_percentage = Column(Numeric(5, 2), default=100, nullable=False)  # Percentage of normal pay
    
    # Eligibility
    eligibility_condition = Column(Text, nullable=True)  # JSON or expression for eligibility
    min_service_days = Column(Integer, default=0, nullable=False)  # Minimum service days to be eligible
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Relationships
    leave_balances = relationship("EmployeeLeaveBalance", back_populates="leave_policy")
    leave_requests = relationship("LeaveRequest", back_populates="leave_policy")
    
    def __repr__(self):
        return f"<LeavePolicy {self.policy_code}: {self.name}>"
    
    def is_employee_eligible(self, employee, as_of_date=None):
        """Check if an employee is eligible for this leave policy."""
        if not self.is_active:
            return False
            
        if as_of_date is None:
            as_of_date = date.today()
            
        # Check minimum service days
        if self.min_service_days > 0 and employee.hire_date:
            service_days = (as_of_date - employee.hire_date).days
            if service_days < self.min_service_days:
                return False
                
        # Additional eligibility checks can be added here
        # based on eligibility_condition
        
        return True
    
    def calculate_accrual(self, employee, start_date, end_date):
        """Calculate leave accrual for an employee over a date range."""
        if self.accrual_method == 'NONE':
            return Decimal('0.00')
            
        if not self.is_employee_eligible(employee, end_date):
            return Decimal('0.00')
        
        # Simple daily accrual calculation
        if self.accrual_method == 'ANNUAL':
            # Convert annual days to daily rate
            daily_rate = Decimal(str(self.days_per_year)) / Decimal('365.0')
            days = (end_date - start_date).days + 1
            return (daily_rate * Decimal(days)).quantize(Decimal('0.01'))
            
        # Add other accrual methods as needed
        
        return Decimal('0.00')


class EmployeeLeaveBalance(PayrollBase, Base):
    """Tracks an employee's leave balance for a specific leave policy."""
    __tablename__ = "payroll_employee_leave_balances"
    __table_args__ = (
        # Ensure one balance record per employee per policy
        {'sqlite_autoincrement': True},
    )

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
    leave_policy_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_leave_policies.id'), 
        nullable=False,
        index=True
    )
    
    # Balance tracking
    opening_balance = Column(Numeric(8, 2), default=0, nullable=False)
    accrued = Column(Numeric(8, 2), default=0, nullable=False)
    taken = Column(Numeric(8, 2), default=0, nullable=False)
    adjusted = Column(Numeric(8, 2), default=0, nullable=False)  # Manual adjustments
    carried_over = Column(Numeric(8, 2), default=0, nullable=False)  # From previous period
    
    # Current balance (calculated)
    @property
    def current_balance(self):
        return (self.opening_balance + self.accrued - self.taken + 
                self.adjusted + self.carried_over)
    
    # Period information
    period_start_date = Column(Date, nullable=False, index=True)
    period_end_date = Column(Date, nullable=False, index=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Relationships
    employee = relationship("Employee", backref="leave_balances")
    leave_policy = relationship("LeavePolicy", back_populates="leave_balances")
    
    def __repr__(self):
        return f"<EmployeeLeaveBalance {self.leave_policy.name}: {self.current_balance} days>"
    
    def update_balance(self, as_of_date=None):
        """Update the balance by calculating accruals up to the specified date."""
        if as_of_date is None:
            as_of_date = date.today()
            
        if as_of_date <= self.period_start_date:
            return self.current_balance
            
        # Calculate accruals since last update
        last_update = max(self.period_start_date, self.updated_at.date() \
                         if self.updated_at else self.period_start_date)
        
        if as_of_date > last_update:
            accrual_days = self.leave_policy.calculate_accrual(
                self.employee, last_update, as_of_date)
            self.accrued += accrual_days
            
        return self.current_balance


class LeaveRequest(PayrollBase, Base):
    """Employee leave request and approval tracking."""
    __tablename__ = "payroll_leave_requests"

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
    leave_policy_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_leave_policies.id'), 
        nullable=False,
        index=True
    )
    
    # Leave details
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=False, index=True)
    is_half_day = Column(Boolean, default=False, nullable=False)
    half_day_period = Column(
        Enum('MORNING', 'AFTERNOON', name='half_day_period_enum'),
        nullable=True
    )
    
    # Duration (in days)
    requested_days = Column(Numeric(5, 2), nullable=False)
    approved_days = Column(Numeric(5, 2), nullable=True)
    
    # Status
    status = Column(
        Enum('DRAFT', 'PENDING', 'APPROVED', 'REJECTED', 'CANCELLED', 'IN_PROGRESS', 'COMPLETED',
             name='leave_request_status_enum'),
        default='DRAFT',
        nullable=False,
        index=True
    )
    
    # Approval workflow
    approver_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_employees.id'), 
        nullable=True,
        index=True
    )
    approved_at = Column(DateTime, nullable=True)
    approval_notes = Column(Text, nullable=True)
    
    # Request details
    reason = Column(Text, nullable=True)
    contact_info = Column(String(255), nullable=True)
    
    # Documentation
    document_url = Column(String(255), nullable=True)
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id], backref="leave_requests")
    leave_policy = relationship("LeavePolicy", back_populates="leave_requests")
    approver = relationship("Employee", foreign_keys=[approver_id])
    
    def __repr__(self):
        return f"<LeaveRequest {self.employee.full_name} - {self.start_date} to {self.end_date} ({self.status})>"
    
    @property
    def duration(self):
        """Calculate the duration of the leave request in days."""
        if self.is_half_day:
            return Decimal('0.5')
        return Decimal(str((self.end_date - self.start_date).days + 1))
    
    def approve(self, approved_by, approved_days=None, notes=None):
        """Approve the leave request."""
        if self.status not in ['PENDING', 'DRAFT']:
            raise ValueError(f"Cannot approve leave request in status: {self.status}")
            
        self.status = 'APPROVED'
        self.approver_id = approved_by.id if hasattr(approved_by, 'id') else approved_by
        self.approved_at = datetime.utcnow()
        self.approval_notes = notes
        
        if approved_days is not None:
            self.approved_days = Decimal(str(approved_days)).quantize(Decimal('0.01'))
        else:
            self.approved_days = self.requested_days
    
    def reject(self, rejected_by, reason=None):
        """Reject the leave request."""
        if self.status not in ['PENDING', 'DRAFT']:
            raise ValueError(f"Cannot reject leave request in status: {self.status}")
            
        self.status = 'REJECTED'
        self.approver_id = rejected_by.id if hasattr(rejected_by, 'id') else rejected_by
        self.approved_at = datetime.utcnow()
        self.approval_notes = reason or "Leave request rejected"
    
    def cancel(self, cancelled_by, reason=None):
        """Cancel the leave request."""
        if self.status in ['COMPLETED', 'CANCELLED']:
            raise ValueError(f"Cannot cancel leave request in status: {self.status}")
            
        self.status = 'CANCELLED'
        self.updated_by = cancelled_by.id if hasattr(cancelled_by, 'id') else cancelled_by
        self.approval_notes = f"{self.approval_notes or ''}\nCancelled: {reason or 'No reason provided'}".strip()
