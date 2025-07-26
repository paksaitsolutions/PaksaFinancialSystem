"""
Succession planning models.
"""
import uuid
from datetime import date, datetime
from sqlalchemy import Column, String, Boolean, ForeignKey, Date, DateTime, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base

class SuccessionPlan(Base):
    """Succession plan model."""
    
    __tablename__ = "succession_plan"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    position_title = Column(String(200), nullable=False)
    department = Column(String(100), nullable=False)
    current_incumbent_id = Column(UUID(as_uuid=True), ForeignKey("employee.id"))
    
    # Risk assessment
    risk_level = Column(String(20), default="medium")  # low, medium, high, critical
    retirement_risk = Column(Boolean, default=False)
    turnover_risk = Column(Boolean, default=False)
    
    # Planning details
    succession_timeline = Column(String(50))  # immediate, 1-2_years, 3-5_years
    development_needs = Column(Text)
    key_competencies = Column(Text)
    
    status = Column(String(20), default="active")  # active, completed, on_hold
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    current_incumbent = relationship("Employee", foreign_keys=[current_incumbent_id])
    candidates = relationship("SuccessionCandidate", back_populates="succession_plan")

class SuccessionCandidate(Base):
    """Succession candidate model."""
    
    __tablename__ = "succession_candidate"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    succession_plan_id = Column(UUID(as_uuid=True), ForeignKey("succession_plan.id"), nullable=False)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employee.id"), nullable=False)
    
    readiness_level = Column(String(20), default="developing")  # ready_now, 1-2_years, 3-5_years, developing
    potential_rating = Column(String(20), default="medium")  # high, medium, low
    
    # Assessment
    strengths = Column(Text)
    development_areas = Column(Text)
    development_plan = Column(Text)
    
    # Progress tracking
    progress_percentage = Column(Integer, default=0)
    last_assessment_date = Column(Date)
    next_review_date = Column(Date)
    
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    succession_plan = relationship("SuccessionPlan", back_populates="candidates")
    employee = relationship("Employee")

class DevelopmentPlan(Base):
    """Employee development plan model."""
    
    __tablename__ = "development_plan"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employee.id"), nullable=False)
    
    plan_name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Timeline
    start_date = Column(Date, nullable=False)
    target_completion_date = Column(Date)
    
    # Categories
    development_type = Column(String(50))  # leadership, technical, soft_skills, certification
    priority = Column(String(20), default="medium")  # high, medium, low
    
    # Progress
    status = Column(String(20), default="active")  # active, completed, on_hold, cancelled
    completion_percentage = Column(Integer, default=0)
    
    # Tracking
    mentor_id = Column(UUID(as_uuid=True), ForeignKey("employee.id"))
    budget_allocated = Column(Integer, default=0)
    budget_used = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id])
    mentor = relationship("Employee", foreign_keys=[mentor_id])
    activities = relationship("DevelopmentActivity", back_populates="development_plan")

class DevelopmentActivity(Base):
    """Development activity model."""
    
    __tablename__ = "development_activity"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    development_plan_id = Column(UUID(as_uuid=True), ForeignKey("development_plan.id"), nullable=False)
    
    activity_name = Column(String(200), nullable=False)
    activity_type = Column(String(50))  # training, mentoring, project, certification, conference
    description = Column(Text)
    
    # Timeline
    planned_start_date = Column(Date)
    planned_end_date = Column(Date)
    actual_start_date = Column(Date)
    actual_end_date = Column(Date)
    
    # Status and progress
    status = Column(String(20), default="planned")  # planned, in_progress, completed, cancelled
    completion_percentage = Column(Integer, default=0)
    
    # Cost tracking
    estimated_cost = Column(Integer, default=0)
    actual_cost = Column(Integer, default=0)
    
    # Results
    outcome_notes = Column(Text)
    effectiveness_rating = Column(Integer)  # 1-5 scale
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    development_plan = relationship("DevelopmentPlan", back_populates="activities")