"""
Attendance and time tracking models for the Payroll module.
"""
from datetime import datetime, time, date, timedelta
from decimal import Decimal
from sqlalchemy import Column, Date, DateTime, Enum, ForeignKey, Numeric, String, Text, Boolean, Integer, Time, Interval
from sqlalchemy.orm import relationship, validates
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.core.database import Base
from app.modules.core_financials.payroll.models.base import PayrollBase


class WorkSchedule(PayrollBase, Base):
    """Defines work schedules for employees or departments."""
    __tablename__ = "payroll_work_schedules"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # Schedule identification
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    schedule_code = Column(String(50), unique=True, index=True, nullable=False)
    
    # Schedule type
    schedule_type = Column(
        Enum('FIXED', 'FLEXIBLE', 'ROTATING', 'SHIFT', 'CUSTOM', name='schedule_type_enum'),
        default='FIXED',
        nullable=False
    )
    
    # Time zone
    time_zone = Column(String(50), default='UTC', nullable=False)
    
    # Default working hours per day
    default_work_hours = Column(Numeric(5, 2), default=8.0, nullable=False)
    
    # Overtime rules
    daily_overtime_after = Column(Numeric(5, 2), default=8.0, nullable=False)  # Hours after which daily OT starts
    weekly_overtime_after = Column(Numeric(5, 2), default=40.0, nullable=False)  # Hours after which weekly OT starts
    
    # Breaks
    has_break = Column(Boolean, default=True, nullable=False)
    break_duration = Column(Interval, default=timedelta(minutes=30), nullable=False)  # Default break duration
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Relationships
    schedule_shifts = relationship("WorkScheduleShift", back_populates="work_schedule", cascade="all, delete-orphan")
    employee_assignments = relationship("EmployeeWorkSchedule", back_populates="work_schedule")
    
    def __repr__(self):
        return f"<WorkSchedule {self.schedule_code}: {self.name}>"
    
    def get_shift_for_date(self, target_date):
        """Get the shift for a specific date based on the schedule's rotation pattern."""
        if not self.schedule_shifts:
            return None
            
        if self.schedule_type == 'FIXED':
            # For fixed schedules, return the first shift (only one should exist)
            return self.schedule_shifts[0]
            
        elif self.schedule_type == 'ROTATING':
            # For rotating schedules, calculate based on the rotation pattern
            # This is a simplified example - a real implementation would consider the rotation cycle
            shift_count = len(self.schedule_shifts)
            if shift_count == 0:
                return None
                
            # Simple rotation based on day of year
            day_of_year = target_date.timetuple().tm_yday - 1
            shift_index = day_of_year % shift_count
            return self.schedule_shifts[shift_index]
            
        # Add other schedule types as needed
        
        return None


class WorkScheduleShift(PayrollBase, Base):
    """Defines shifts within a work schedule."""
    __tablename__ = "payroll_work_schedule_shifts"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # References
    work_schedule_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_work_schedules.id'), 
        nullable=False,
        index=True
    )
    
    # Shift identification
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    shift_code = Column(String(50), index=True, nullable=False)
    
    # Shift timing
    start_time = Column(Time, nullable=False)  # e.g., 09:00
    end_time = Column(Time, nullable=False)    # e.g., 17:00
    
    # Days of the week (bitmask or boolean columns)
    monday = Column(Boolean, default=True, nullable=False)
    tuesday = Column(Boolean, default=True, nullable=False)
    wednesday = Column(Boolean, default=True, nullable=False)
    thursday = Column(Boolean, default=True, nullable=False)
    friday = Column(Boolean, default=True, nullable=False)
    saturday = Column(Boolean, default=False, nullable=False)
    sunday = Column(Boolean, default=False, nullable=False)
    
    # Break rules
    break_duration = Column(Interval, nullable=True)  # Overrides schedule default if set
    
    # Overtime rules (override schedule defaults if needed)
    is_overtime_eligible = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    work_schedule = relationship("WorkSchedule", back_populates="schedule_shifts")
    
    def __repr__(self):
        return f"<WorkScheduleShift {self.shift_code}: {self.start_time} - {self.end_time}>"
    
    @property
    def duration(self):
        """Calculate the duration of the shift in hours."""
        if not self.start_time or not self.end_time:
            return Decimal('0.00')
            
        # Convert times to datetime objects for calculation
        start_dt = datetime.combine(date.today(), self.start_time)
        end_dt = datetime.combine(
            date.today() + timedelta(days=1) if self.end_time < self.start_time else date.today(),
            self.end_time
        )
        
        # Calculate duration in hours
        duration_seconds = (end_dt - start_dt).total_seconds()
        return Decimal(str(duration_seconds / 3600)).quantize(Decimal('0.01'))
    
    def is_working_day(self, day_of_week):
        """Check if this shift is active on the given day of week (0=Monday, 6=Sunday)."""
        days = [self.monday, self.tuesday, self.wednesday, self.thursday,
                self.friday, self.saturday, self.sunday]
        return days[day_of_week] if 0 <= day_of_week <= 6 else False


class EmployeeWorkSchedule(PayrollBase, Base):
    """Assigns work schedules to employees."""
    __tablename__ = "payroll_employee_work_schedules"
    __table_args__ = (
        # Ensure one active schedule per employee
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
    work_schedule_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_work_schedules.id'), 
        nullable=False,
        index=True
    )
    
    # Effective date range
    effective_from = Column(Date, nullable=False, index=True)
    effective_to = Column(Date, nullable=True, index=True)  # NULL means no end date
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Relationships
    employee = relationship("Employee", backref="work_schedules")
    work_schedule = relationship("WorkSchedule", back_populates="employee_assignments")
    
    def __repr__(self):
        return f"<EmployeeWorkSchedule {self.employee.full_name} - {self.work_schedule.name}>"
    
    @property
    def is_current(self):
        """Check if this schedule is currently active."""
        today = date.today()
        return (self.is_active and 
                self.effective_from <= today and 
                (self.effective_to is None or today <= self.effective_to))


class AttendanceRecord(PayrollBase, Base):
    """Tracks employee attendance and working hours."""
    __tablename__ = "payroll_attendance_records"
    __table_args__ = (
        # Ensure one record per employee per day
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
    schedule_shift_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_work_schedule_shifts.id'), 
        nullable=True,
        index=True
    )
    
    # Date and time tracking
    work_date = Column(Date, nullable=False, index=True)
    clock_in = Column(DateTime, nullable=True, index=True)
    clock_out = Column(DateTime, nullable=True, index=True)
    
    # Break tracking
    break_start = Column(DateTime, nullable=True)
    break_end = Column(DateTime, nullable=True)
    
    # Duration calculations
    scheduled_hours = Column(Numeric(5, 2), default=0, nullable=False)
    actual_hours = Column(Numeric(5, 2), default=0, nullable=False)
    regular_hours = Column(Numeric(5, 2), default=0, nullable=False)
    overtime_hours = Column(Numeric(5, 2), default=0, nullable=False)
    
    # Status
    status = Column(
        Enum('PRESENT', 'ABSENT', 'HOLIDAY', 'LEAVE', 'HALF_DAY', 'LATE', 'EARLY_DEPARTURE',
             'NO_SHOW', 'EXCUSED', 'OTHER', name='attendance_status_enum'),
        default='PRESENT',
        nullable=False,
        index=True
    )
    
    # Approval
    is_approved = Column(Boolean, default=False, nullable=False)
    approved_by_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_employees.id'), 
        nullable=True,
        index=True
    )
    approved_at = Column(DateTime, nullable=True)
    
    # Notes and adjustments
    notes = Column(Text, nullable=True)
    adjustment_notes = Column(Text, nullable=True)
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id], backref="attendance_records")
    schedule_shift = relationship("WorkScheduleShift")
    approved_by = relationship("Employee", foreign_keys=[approved_by_id])
    
    def __repr__(self):
        return f"<AttendanceRecord {self.employee.full_name} - {self.work_date} ({self.status})>"
    
    @property
    def is_clocked_in(self):
        """Check if the employee is currently clocked in."""
        return self.clock_in is not None and self.clock_out is None
    
    @property
    def is_on_break(self):
        """Check if the employee is currently on a break."""
        return self.break_start is not None and self.break_end is None
    
    def calculate_hours(self):
        """Calculate worked hours based on clock in/out times."""
        if not self.clock_in or not self.clock_out:
            self.actual_hours = Decimal('0.00')
            self.regular_hours = Decimal('0.00')
            self.overtime_hours = Decimal('0.00')
            return
            
        # Calculate total duration in hours
        total_seconds = (self.clock_out - self.clock_in).total_seconds()
        self.actual_hours = Decimal(str(total_seconds / 3600)).quantize(Decimal('0.01'))
        
        # Get employee's work schedule for the day
        schedule = self.employee.get_work_schedule(self.work_date)
        if not schedule:
            # No schedule found, all hours are regular
            self.regular_hours = self.actual_hours
            self.overtime_hours = Decimal('0.00')
            return
            
        # Calculate regular vs. overtime based on schedule
        daily_regular_hours = schedule.work_schedule.default_work_hours
        
        if self.actual_hours <= daily_regular_hours:
            self.regular_hours = self.actual_hours
            self.overtime_hours = Decimal('0.00')
        else:
            self.regular_hours = daily_regular_hours
            self.overtime_hours = self.actual_hours - daily_regular_hours
    
    def clock_in_employee(self, clock_time=None):
        """Record clock in time."""
        if clock_time is None:
            clock_time = datetime.now()
            
        self.clock_in = clock_time
        self.clock_out = None
        self.status = 'PRESENT'
        
        # If this is a new record, set the work date
        if not self.work_date:
            self.work_date = clock_time.date()
    
    def clock_out_employee(self, clock_time=None):
        """Record clock out time and calculate hours."""
        if clock_time is None:
            clock_time = datetime.now()
            
        self.clock_out = clock_time
        self.calculate_hours()
    
    def start_break(self, break_time=None):
        """Start a break."""
        if break_time is None:
            break_time = datetime.now()
            
        self.break_start = break_time
        self.break_end = None
    
    def end_break(self, break_time=None):
        """End a break and update break duration."""
        if break_time is None:
            break_time = datetime.now()
            
        self.break_end = break_time
        # Recalculate hours to account for break
        self.calculate_hours()
    
    def approve(self, approved_by, notes=None):
        """Approve the attendance record."""
        self.is_approved = True
        self.approved_by_id = approved_by.id if hasattr(approved_by, 'id') else approved_by
        self.approved_at = datetime.utcnow()
        self.adjustment_notes = notes or self.adjustment_notes
