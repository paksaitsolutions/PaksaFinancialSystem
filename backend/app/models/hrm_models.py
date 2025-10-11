# Import unified HRM models from core_models to eliminate duplicates
from app.models.core_models import (
    Employee,
    Department,
    LeaveRequest
)

# All core HRM models are now unified in core_models.py
# Extended HRM functionality remains here

from app.models.base import Base
from sqlalchemy import Column, String, Date, Boolean, Numeric, ForeignKey, Text, DateTime, Integer, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import date, datetime
from enum import Enum
import uuid

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

class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
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
    employee = relationship("Employee")

class PerformanceReview(Base):
    __tablename__ = "performance_reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    reviewer_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
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
    employee = relationship("Employee", foreign_keys=[employee_id])
    reviewer = relationship("Employee", foreign_keys=[reviewer_id])

class TrainingRecord(Base):
    __tablename__ = "training_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
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
    employee = relationship("Employee")

class Policy(Base):
    __tablename__ = "policies"

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
    approved_by = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    # Audit Fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Relationships
    approver = relationship("Employee", foreign_keys=[approved_by])

class JobOpening(Base):
    __tablename__ = "job_openings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=True)
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
    hiring_manager_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True)
    
    # Audit Fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    department = relationship("Department")
    hiring_manager = relationship("Employee", foreign_keys=[hiring_manager_id])
    candidates = relationship("Candidate", back_populates="job_opening")

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    job_opening_id = Column(UUID(as_uuid=True), ForeignKey("job_openings.id"), nullable=False)
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
    __tablename__ = "interviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False)
    interviewer_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
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