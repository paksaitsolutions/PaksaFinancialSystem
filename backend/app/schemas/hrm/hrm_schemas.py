"""
HRM schemas.
"""
from typing import List, Optional
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel

class EmployeeBase(BaseModel):
    """Base employee schema."""
    employee_id: str
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    manager_id: Optional[UUID] = None
    hire_date: date
    employment_type: str = "full_time"
    salary: Optional[Decimal] = None
    currency_code: str = "USD"
    date_of_birth: Optional[date] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None
    is_active: bool = True

class EmployeeCreate(EmployeeBase):
    """Create employee schema."""
    pass

class EmployeeUpdate(BaseModel):
    """Update employee schema."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    salary: Optional[Decimal] = None
    is_active: Optional[bool] = None

class EmployeeResponse(EmployeeBase):
    """Employee response schema."""
    id: UUID
    tenant_id: UUID
    termination_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class LeaveRequestBase(BaseModel):
    """Base leave request schema."""
    leave_type: str
    start_date: date
    end_date: date
    days_requested: Decimal
    reason: Optional[str] = None

class LeaveRequestCreate(LeaveRequestBase):
    """Create leave request schema."""
    pass

class LeaveRequestUpdate(BaseModel):
    """Update leave request schema."""
    status: Optional[str] = None
    rejection_reason: Optional[str] = None

class LeaveRequestResponse(LeaveRequestBase):
    """Leave request response schema."""
    id: UUID
    employee_id: UUID
    status: str
    approved_by: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class AttendanceRecordBase(BaseModel):
    """Base attendance record schema."""
    date: date
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    break_start: Optional[datetime] = None
    break_end: Optional[datetime] = None
    status: str = "present"
    notes: Optional[str] = None

class AttendanceRecordCreate(AttendanceRecordBase):
    """Create attendance record schema."""
    pass

class AttendanceRecordResponse(AttendanceRecordBase):
    """Attendance record response schema."""
    id: UUID
    employee_id: UUID
    hours_worked: Optional[str] = None
    overtime_hours: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class PerformanceReviewBase(BaseModel):
    """Base performance review schema."""
    reviewer_id: UUID
    review_period_start: date
    review_period_end: date
    review_type: str = "annual"
    overall_rating: Optional[Decimal] = None
    technical_skills: Optional[Decimal] = None
    communication: Optional[Decimal] = None
    teamwork: Optional[Decimal] = None
    leadership: Optional[Decimal] = None
    strengths: Optional[str] = None
    areas_for_improvement: Optional[str] = None
    goals_next_period: Optional[str] = None
    manager_comments: Optional[str] = None

class PerformanceReviewCreate(PerformanceReviewBase):
    """Create performance review schema."""
    pass

class PerformanceReviewResponse(PerformanceReviewBase):
    """Performance review response schema."""
    id: UUID
    employee_id: UUID
    status: str
    employee_comments: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class HRAnalytics(BaseModel):
    """HR analytics schema."""
    total_employees: int
    active_employees: int
    pending_leave_requests: int
    average_attendance: float
    department_breakdown: List[dict]
    recent_hires: List[dict]