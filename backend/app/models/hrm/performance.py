"""
Performance management models.
"""
import uuid
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import Column, String, Boolean, ForeignKey, Date, DateTime, Numeric, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base

class PerformanceReview(Base):
    """Performance review model."""
    
    __tablename__ = "performance_review"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    reviewer_id = Column(UUID(as_uuid=True), nullable=False)
    
    review_period_start = Column(Date, nullable=False)
    review_period_end = Column(Date, nullable=False)
    review_type = Column(String(50), default="annual")  # annual, quarterly, probation
    
    # Ratings (1-5 scale)
    overall_rating = Column(Numeric(precision=3, scale=2))
    technical_skills = Column(Numeric(precision=3, scale=2))
    communication = Column(Numeric(precision=3, scale=2))
    teamwork = Column(Numeric(precision=3, scale=2))
    leadership = Column(Numeric(precision=3, scale=2))
    
    # Comments
    strengths = Column(Text)
    areas_for_improvement = Column(Text)
    goals_next_period = Column(Text)
    manager_comments = Column(Text)
    employee_comments = Column(Text)
    
    status = Column(String(20), default="draft")  # draft, completed, acknowledged
    
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    employee = relationship("Employee")

class Goal(Base):
    """Employee goal model."""
    
    __tablename__ = "goal"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    
    title = Column(String(200), nullable=False)
    description = Column(Text)
    target_date = Column(Date)
    
    status = Column(String(20), default="active")  # active, completed, cancelled
    progress_percentage = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employee = relationship("Employee")