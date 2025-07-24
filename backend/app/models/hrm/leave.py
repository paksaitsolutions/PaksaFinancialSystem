"""
Leave management models.
"""
import uuid
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import Column, String, Boolean, ForeignKey, Date, DateTime, Numeric, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base

class LeavePolicy(Base):
    """Leave policy model."""
    
    __tablename__ = "leave_policy"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    policy_name = Column(String(100), nullable=False)
    leave_type = Column(String(50), nullable=False)  # annual, sick, maternity, etc.
    days_per_year = Column(Integer, nullable=False)
    max_carry_forward = Column(Integer, default=0)
    requires_approval = Column(Boolean, default=True)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class LeaveBalance(Base):
    """Employee leave balance model."""
    
    __tablename__ = "leave_balance"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employee.id"), nullable=False)
    leave_type = Column(String(50), nullable=False)
    
    total_days = Column(Numeric(precision=5, scale=2), nullable=False)
    used_days = Column(Numeric(precision=5, scale=2), default=0)
    remaining_days = Column(Numeric(precision=5, scale=2), nullable=False)
    
    year = Column(Integer, nullable=False)
    
    # Relationships
    employee = relationship("Employee")

class LeaveRequest(Base):
    """Leave request model."""
    
    __tablename__ = "leave_request"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employee.id"), nullable=False)
    
    leave_type = Column(String(50), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    days_requested = Column(Numeric(precision=5, scale=2), nullable=False)
    
    reason = Column(Text)
    status = Column(String(20), default="pending")  # pending, approved, rejected, cancelled
    
    # Approval workflow
    approved_by = Column(UUID(as_uuid=True))
    approved_at = Column(DateTime)
    rejection_reason = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employee = relationship("Employee", back_populates="leave_requests")