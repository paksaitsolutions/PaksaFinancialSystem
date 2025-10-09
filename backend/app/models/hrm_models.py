"""
Complete HRM Models for Paksa Financial System
"""
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from sqlalchemy import Column, String, Date, Boolean, Numeric, ForeignKey, Text, DateTime, Integer, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.models.base import Base

# Enums
class EmploymentType(str, Enum):
    FULL_TIME = "FULL_TIME"
    PART_TIME = "PART_TIME"
    CONTRACT = "CONTRACT"
    TEMPORARY = "TEMPORARY"
    INTERN = "INTERN"

class LeaveType(str, Enum):
    ANNUAL = "ANNUAL"
    SICK = "SICK"
    MATERNITY = "MATERNITY"
    PATERNITY = "PATERNITY"
    PERSONAL = "PERSONAL"
    EMERGENCY = "EMERGENCY"
    UNPAID = "UNPAID"

class LeaveStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"

class AttendanceStatus(str, Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    LATE = "LATE"
    HALF_DAY = "HALF_DAY"
    HOLIDAY = "HOLIDAY"

class PerformanceRating(str, Enum):
    OUTSTANDING = "OUTSTANDING"
    EXCEEDS_EXPECTATIONS = "EXCEEDS_EXPECTATIONS"
    MEETS_EXPECTATIONS = "MEETS_EXPECTATIONS"
    BELOW_EXPECTATIONS = "BELOW_EXPECTATIONS"
    UNSATISFACTORY = "UNSATISFACTORY"

# Core Models
class Employee(Base):
    __tablename__ = "hrm_employees"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    employee_id = Column(String(50), unique=True, index=True, nullable=False)
    
    # Personal Information
    first_name = Column(String(100), nullable=False)
    middle_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone_number = Column(String(50), nullable=False)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(1), nullable=True)
    marital_status = Column(String(20), nullable=True)
    national_id = Column(String(50), nullable=True)
    
    # Address
    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)
    
    # Employment Details
    job_title = Column(String(100), nullable=False)
    department_id = Column(UUID(as_uuid=True), ForeignKey("hrm_departments.id"), nullable=True)
    manager_id = Column(UUID(as_uuid=True), ForeignKey("hrm_employees.id"), nullable=True)
    hire_date = Column(Date, nullable=False)
    termination_date = Column(Date, nullable=True)
    employment_type = Column(String(50), nullable=False, default=EmploymentType.FULL_TIME)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Compensation
    base_salary = Column(Numeric(15, 2), nullable=False, default=0)
    currency = Column(String(3), default='USD', nullable=False)
    payment_method = Column(String(50), nullable=False, default='BANK_TRANSFER')
    payment_frequency = Column(String(20), nullable=False, default='MONTHLY')
    
    # Bank Details
    bank_name = Column(String(100), nullable=True)
    account_number = Column(String(50), nullable=True)
    routing_number = Column(String(50), nullable=True)
    
    # Emergency Contact
    emergency_contact_name = Column(String(200), nullable=True)
    emergency_contact_phone = Column(String(50), nullable=True)
    emergency_contact_relationship = Column(String(50), nullable=True)
    
    # Audit Fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Relationships
    department = relationship("Department", back_populates="employees")
    manager = relationship("Employee", remote_side=[id])
    direct_reports = relationship("Employee", back_populates="manager")
    leave_requests = relationship("LeaveRequest", back_populates="employee")
    attendance_records = relationship("AttendanceRecord", back_populates="employee")
    performance_reviews = relationship("PerformanceReview", back_populates="employee")
    training_records = relationship("TrainingRecord", back_populates="employee")
    
    @property
    def full_name(self):
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"

class Department(Base):
    __tablename__ = "hrm_departments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    manager_id = Column(UUID(as_uuid=True), ForeignKey("hrm_employees.id"), nullable=True)
    parent_department_id = Column(UUID(as_uuid=True), ForeignKey("hrm_departments.id"), nullable=True)
    budget = Column(Numeric(15, 2), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Audit Fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    employees = relationship("Employee", back_populates="department")
    manager = relationship("Employee", foreign_keys=[manager_id])
    parent_department = relationship("Department", remote_side=[id])
    sub_departments = relationship("Department", back_populates="parent_department")

class LeaveRequest(Base):
    __tablename__ = "hrm_leave_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("hrm_employees.id"), nullable=False)
    leave_type = Column(String(50), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    days_requested = Column(Integer, nullable=False)
    reason = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default=LeaveStatus.PENDING)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("hrm_employees.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Audit Fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    employee = relationship("Employee", back_populates="leave_requests", foreign_keys=[employee_id])
    approver = relationship("Employee", foreign_keys=[approved_by])

class AttendanceRecord(Base):
    __tablename__ = "hrm_attendance_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("hrm_employees.id"), nullable=False)
    date = Column(Date, nullable=False)
    check_in_time = Column(DateTime, nullable=True)
    check_out_time = Column(DateTime, nullable=True)
    break_duration = Column(Integer, nullable=True)  # in minutes
    total_hours = Column(Numeric(5, 2), nullable=True)
    overtime_hours = Column(Numeric(5, 2), nullable=True, default=0)
    status = Column(String(50), nullable=False, default=AttendanceStatus.PRESENT)
    notes = Column(Text, nullable=True)
    
    # Audit Fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    employee = relationship("Employee", back_populates="attendance_records")

class PerformanceReview(Base):
    __tablename__ = "hrm_performance_reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("hrm_employees.id"), nullable=False)
    reviewer_id = Column(UUID(as_uuid=True), ForeignKey("hrm_employees.id"), nullable=False)
    review_period_start = Column(Date, nullable=False)
    review_period_end = Column(Date, nullable=False)
    review_date = Column(Date, nullable=False)
    overall_rating = Column(String(50), nullable=False)
    goals_achievement = Column(Integer, nullable=True)  # percentage
    strengths = Column(Text, nullable=True)
    areas_for_improvement = Column(Text, nullable=True)
    development_goals = Column(Text, nullable=True)
    manager_comments = Column(Text, nullable=True)
    employee_comments = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="DRAFT")
    
    # Audit Fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    employee = relationship("Employee", back_populates="performance_reviews", foreign_keys=[employee_id])
    reviewer = relationship("Employee", foreign_keys=[reviewer_id])

class TrainingRecord(Base):
    __tablename__ = "hrm_training_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("hrm_employees.id"), nullable=False)
    training_name = Column(String(200), nullable=False)
    training_type = Column(String(50), nullable=False)  # INTERNAL, EXTERNAL, ONLINE, etc.
    provider = Column(String(200), nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    duration_hours = Column(Integer, nullable=True)
    cost = Column(Numeric(10, 2), nullable=True)
    status = Column(String(50), nullable=False, default="ENROLLED")
    completion_date = Column(Date, nullable=True)
    certificate_url = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Audit Fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    employee = relationship("Employee", back_populates="training_records")

class Policy(Base):
    __tablename__ = "hrm_policies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    content = Column(Text, nullable=False)
    version = Column(String(20), nullable=False, default="1.0")
    effective_date = Column(Date, nullable=False)
    expiry_date = Column(Date, nullable=True)
    status = Column(String(50), nullable=False, default="ACTIVE")
    approval_required = Column(Boolean, default=False)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("hrm_employees.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    # Audit Fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Relationships
    approver = relationship("Employee", foreign_keys=[approved_by])

class JobOpening(Base):
    __tablename__ = "hrm_job_openings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    department_id = Column(UUID(as_uuid=True), ForeignKey("hrm_departments.id"), nullable=True)
    description = Column(Text, nullable=False)
    requirements = Column(Text, nullable=True)
    employment_type = Column(String(50), nullable=False)
    salary_min = Column(Numeric(15, 2), nullable=True)
    salary_max = Column(Numeric(15, 2), nullable=True)
    location = Column(String(200), nullable=True)
    remote_allowed = Column(Boolean, default=False)
    status = Column(String(50), nullable=False, default="OPEN")
    posted_date = Column(Date, nullable=False)
    closing_date = Column(Date, nullable=True)
    hiring_manager_id = Column(UUID(as_uuid=True), ForeignKey("hrm_employees.id"), nullable=True)
    
    # Audit Fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    department = relationship("Department")
    hiring_manager = relationship("Employee", foreign_keys=[hiring_manager_id])
    candidates = relationship("Candidate", back_populates="job_opening")

class Candidate(Base):
    __tablename__ = "hrm_candidates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    job_opening_id = Column(UUID(as_uuid=True), ForeignKey("hrm_job_openings.id"), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    phone_number = Column(String(50), nullable=True)
    resume_url = Column(String(500), nullable=True)
    cover_letter = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="APPLIED")
    source = Column(String(100), nullable=True)  # WEBSITE, REFERRAL, LINKEDIN, etc.
    applied_date = Column(Date, nullable=False)
    
    # Audit Fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    job_opening = relationship("JobOpening", back_populates="candidates")
    interviews = relationship("Interview", back_populates="candidate")

class Interview(Base):
    __tablename__ = "hrm_interviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("hrm_candidates.id"), nullable=False)
    interviewer_id = Column(UUID(as_uuid=True), ForeignKey("hrm_employees.id"), nullable=False)
    interview_type = Column(String(50), nullable=False)  # PHONE, VIDEO, IN_PERSON, TECHNICAL
    scheduled_date = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, nullable=True)
    location = Column(String(200), nullable=True)
    meeting_link = Column(String(500), nullable=True)
    status = Column(String(50), nullable=False, default="SCHEDULED")
    feedback = Column(Text, nullable=True)
    rating = Column(Integer, nullable=True)  # 1-5 scale
    recommendation = Column(String(50), nullable=True)  # HIRE, NO_HIRE, MAYBE
    
    # Audit Fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="interviews")
    interviewer = relationship("Employee", foreign_keys=[interviewer_id])