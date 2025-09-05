"""
Leave management models
"""
from datetime import date, datetime
from sqlalchemy import Column, String, Date, Numeric, ForeignKey, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.models.base import Base

class LeaveRequest(Base):
    __tablename__ = "hrm_leave_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    employee_id = Column(UUID(as_uuid=True), ForeignKey('hrm_employees.id'), nullable=False)
    leave_type = Column(String(50), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    days_requested = Column(Numeric(5, 2), nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default='pending')
    
    # Approval details
    approved_by = Column(UUID(as_uuid=True), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    employee = relationship("Employee", back_populates="leave_requests")

class LeaveBalance(Base):
    __tablename__ = "hrm_leave_balances"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    employee_id = Column(UUID(as_uuid=True), ForeignKey('hrm_employees.id'), nullable=False)
    leave_type = Column(String(50), nullable=False)
    total_days = Column(Numeric(5, 2), nullable=False)
    used_days = Column(Numeric(5, 2), nullable=False, default=0)
    remaining_days = Column(Numeric(5, 2), nullable=False)
    year = Column(String(4), nullable=False)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class LeavePolicy(Base):
    __tablename__ = "hrm_leave_policies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    leave_type = Column(String(50), nullable=False)
    days_per_year = Column(Numeric(5, 2), nullable=False)
    carry_forward_days = Column(Numeric(5, 2), nullable=False, default=0)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)