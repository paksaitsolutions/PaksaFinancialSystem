"""
Comprehensive HRM Schemas
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, validator

# Base Schemas
class HRMBase(BaseModel):
    class Config:
        from_attributes = True

# Employee Schemas
class EmployeeBase(HRMBase):
    employee_id: str
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    email: str
    phone_number: str
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    marital_status: Optional[str] = None
    national_id: Optional[str] = None
    job_title: str
    department_id: Optional[UUID] = None
    manager_id: Optional[UUID] = None
    hire_date: date
    employment_type: str = "FULL_TIME"
    base_salary: Decimal = Decimal('0.00')
    is_active: bool = True

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(HRMBase):
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    marital_status: Optional[str] = None
    job_title: Optional[str] = None
    department_id: Optional[UUID] = None
    manager_id: Optional[UUID] = None
    employment_type: Optional[str] = None
    base_salary: Optional[Decimal] = None
    is_active: Optional[bool] = None

class EmployeeResponse(EmployeeBase):
    id: UUID
    tenant_id: UUID
    full_name: str
    created_at: datetime
    updated_at: datetime
    
    # Nested relationships
    department: Optional['DepartmentResponse'] = None
    manager: Optional['EmployeeResponse'] = None

# Department Schemas
class DepartmentBase(HRMBase):
    name: str
    description: Optional[str] = None
    manager_id: Optional[UUID] = None
    parent_department_id: Optional[UUID] = None
    budget: Optional[Decimal] = None
    is_active: bool = True

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentUpdate(HRMBase):
    name: Optional[str] = None
    description: Optional[str] = None
    manager_id: Optional[UUID] = None
    parent_department_id: Optional[UUID] = None
    budget: Optional[Decimal] = None
    is_active: Optional[bool] = None

class DepartmentResponse(DepartmentBase):
    id: UUID
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime
    employee_count: int = 0
    
    # Nested relationships
    manager: Optional[EmployeeResponse] = None
    parent_department: Optional['DepartmentResponse'] = None

# Leave Request Schemas
class LeaveRequestBase(HRMBase):
    leave_type: str
    start_date: date
    end_date: date
    reason: Optional[str] = None

class LeaveRequestCreate(LeaveRequestBase):
    @validator('end_date')
    def end_date_must_be_after_start_date(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('End date must be after start date')
        return v

class LeaveRequestUpdate(HRMBase):
    leave_type: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    reason: Optional[str] = None
    status: Optional[str] = None

class LeaveRequestResponse(LeaveRequestBase):
    id: UUID
    tenant_id: UUID
    employee_id: UUID
    days_requested: int
    status: str
    approved_by: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    # Nested relationships
    employee: Optional[EmployeeResponse] = None
    approver: Optional[EmployeeResponse] = None

# Attendance Schemas
class AttendanceRecordBase(HRMBase):
    date: date
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    break_duration: Optional[int] = None  # in minutes
    status: str = "PRESENT"
    notes: Optional[str] = None

class AttendanceRecordCreate(AttendanceRecordBase):
    pass

class AttendanceRecordUpdate(HRMBase):
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    break_duration: Optional[int] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class AttendanceRecordResponse(AttendanceRecordBase):
    id: UUID
    tenant_id: UUID
    employee_id: UUID
    total_hours: Optional[Decimal] = None
    overtime_hours: Optional[Decimal] = None
    created_at: datetime
    updated_at: datetime
    
    # Nested relationships
    employee: Optional[EmployeeResponse] = None

# Performance Review Schemas
class PerformanceReviewBase(HRMBase):
    review_period_start: date
    review_period_end: date
    review_date: date
    overall_rating: str
    goals_achievement: Optional[int] = None  # percentage
    strengths: Optional[str] = None
    areas_for_improvement: Optional[str] = None
    development_goals: Optional[str] = None
    manager_comments: Optional[str] = None
    employee_comments: Optional[str] = None

class PerformanceReviewCreate(PerformanceReviewBase):
    pass

class PerformanceReviewUpdate(HRMBase):
    review_date: Optional[date] = None
    overall_rating: Optional[str] = None
    goals_achievement: Optional[int] = None
    strengths: Optional[str] = None
    areas_for_improvement: Optional[str] = None
    development_goals: Optional[str] = None
    manager_comments: Optional[str] = None
    employee_comments: Optional[str] = None
    status: Optional[str] = None

class PerformanceReviewResponse(PerformanceReviewBase):
    id: UUID
    tenant_id: UUID
    employee_id: UUID
    reviewer_id: UUID
    status: str
    created_at: datetime
    updated_at: datetime
    
    # Nested relationships
    employee: Optional[EmployeeResponse] = None
    reviewer: Optional[EmployeeResponse] = None

# Training Schemas
class TrainingRecordBase(HRMBase):
    training_name: str
    training_type: str
    provider: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    duration_hours: Optional[int] = None
    cost: Optional[Decimal] = None
    status: str = "ENROLLED"
    notes: Optional[str] = None

class TrainingRecordCreate(TrainingRecordBase):
    pass

class TrainingRecordUpdate(HRMBase):
    training_name: Optional[str] = None
    training_type: Optional[str] = None
    provider: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    duration_hours: Optional[int] = None
    cost: Optional[Decimal] = None
    status: Optional[str] = None
    completion_date: Optional[date] = None
    certificate_url: Optional[str] = None
    notes: Optional[str] = None

class TrainingRecordResponse(TrainingRecordBase):
    id: UUID
    tenant_id: UUID
    employee_id: UUID
    completion_date: Optional[date] = None
    certificate_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    # Nested relationships
    employee: Optional[EmployeeResponse] = None

# Policy Schemas
class PolicyBase(HRMBase):
    title: str
    category: str
    description: Optional[str] = None
    content: str
    version: str = "1.0"
    effective_date: date
    expiry_date: Optional[date] = None
    status: str = "ACTIVE"
    approval_required: bool = False

class PolicyCreate(PolicyBase):
    pass

class PolicyUpdate(HRMBase):
    title: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    version: Optional[str] = None
    effective_date: Optional[date] = None
    expiry_date: Optional[date] = None
    status: Optional[str] = None
    approval_required: Optional[bool] = None

class PolicyResponse(PolicyBase):
    id: UUID
    tenant_id: UUID
    approved_by: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    
    # Nested relationships
    approver: Optional[EmployeeResponse] = None

# Job Opening Schemas
class JobOpeningBase(HRMBase):
    title: str
    department_id: Optional[UUID] = None
    description: str
    requirements: Optional[str] = None
    employment_type: str
    salary_min: Optional[Decimal] = None
    salary_max: Optional[Decimal] = None
    location: Optional[str] = None
    remote_allowed: bool = False
    status: str = "OPEN"
    posted_date: date
    closing_date: Optional[date] = None
    hiring_manager_id: Optional[UUID] = None

class JobOpeningCreate(JobOpeningBase):
    pass

class JobOpeningUpdate(HRMBase):
    title: Optional[str] = None
    department_id: Optional[UUID] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    employment_type: Optional[str] = None
    salary_min: Optional[Decimal] = None
    salary_max: Optional[Decimal] = None
    location: Optional[str] = None
    remote_allowed: Optional[bool] = None
    status: Optional[str] = None
    closing_date: Optional[date] = None
    hiring_manager_id: Optional[UUID] = None

class JobOpeningResponse(JobOpeningBase):
    id: UUID
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime
    
    # Nested relationships
    department: Optional[DepartmentResponse] = None
    hiring_manager: Optional[EmployeeResponse] = None

# Candidate Schemas
class CandidateBase(HRMBase):
    first_name: str
    last_name: str
    email: str
    phone_number: Optional[str] = None
    resume_url: Optional[str] = None
    cover_letter: Optional[str] = None
    status: str = "APPLIED"
    source: Optional[str] = None
    applied_date: date

class CandidateCreate(CandidateBase):
    job_opening_id: UUID

class CandidateUpdate(HRMBase):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    resume_url: Optional[str] = None
    cover_letter: Optional[str] = None
    status: Optional[str] = None
    source: Optional[str] = None

class CandidateResponse(CandidateBase):
    id: UUID
    tenant_id: UUID
    job_opening_id: UUID
    created_at: datetime
    updated_at: datetime
    
    # Nested relationships
    job_opening: Optional[JobOpeningResponse] = None

# Interview Schemas
class InterviewBase(HRMBase):
    interview_type: str
    scheduled_date: datetime
    duration_minutes: Optional[int] = None
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    status: str = "SCHEDULED"
    feedback: Optional[str] = None
    rating: Optional[int] = None
    recommendation: Optional[str] = None

class InterviewCreate(InterviewBase):
    candidate_id: UUID
    interviewer_id: UUID

class InterviewUpdate(HRMBase):
    interview_type: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    status: Optional[str] = None
    feedback: Optional[str] = None
    rating: Optional[int] = None
    recommendation: Optional[str] = None

class InterviewResponse(InterviewBase):
    id: UUID
    tenant_id: UUID
    candidate_id: UUID
    interviewer_id: UUID
    created_at: datetime
    updated_at: datetime
    
    # Nested relationships
    candidate: Optional[CandidateResponse] = None
    interviewer: Optional[EmployeeResponse] = None

# Analytics Schemas
class HRAnalytics(HRMBase):
    total_employees: int
    active_employees: int
    inactive_employees: int
    pending_leave_requests: int
    department_breakdown: List[dict]
    recent_hires: List[dict]
    average_tenure_months: float

class EmployeeDashboard(HRMBase):
    employee: EmployeeResponse
    pending_leave_requests: List[LeaveRequestResponse]
    recent_attendance: List[AttendanceRecordResponse]
    upcoming_reviews: List[PerformanceReviewResponse]
    training_progress: List[TrainingRecordResponse]
    team_members: List[EmployeeResponse]

# Update forward references
EmployeeResponse.model_rebuild()
DepartmentResponse.model_rebuild()
LeaveRequestResponse.model_rebuild()
AttendanceRecordResponse.model_rebuild()
PerformanceReviewResponse.model_rebuild()
TrainingRecordResponse.model_rebuild()
PolicyResponse.model_rebuild()
JobOpeningResponse.model_rebuild()
CandidateResponse.model_rebuild()
InterviewResponse.model_rebuild()