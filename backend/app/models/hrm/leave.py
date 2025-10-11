"""
HRM Leave Management Models
==========================
Re-exports unified leave models from core_models for HRM module compatibility.
"""

from app.models.core_models import LeaveRequest, Employee
from sqlalchemy import Column, String, Integer, Numeric, DateTime, Boolean, Text, ForeignKey, Date, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base, AuditMixin
import uuid
from enum import Enum as PyEnum

# Re-export core models for compatibility
__all__ = ['LeaveRequest', 'LeaveBalance', 'LeavePolicy']

class LeaveBalance(Base, AuditMixin):
    """Employee Leave Balance"""
    __tablename__ = "leave_balances"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    leave_type = Column(String(50), nullable=False)
    total_days = Column(Numeric(5, 2), nullable=False)
    used_days = Column(Numeric(5, 2), default=0)
    remaining_days = Column(Numeric(5, 2), nullable=False)
    year = Column(Integer, nullable=False)
    
    # Relationships
    employee = relationship("Employee")

class LeavePolicy(Base, AuditMixin):
    """Company Leave Policy"""
    __tablename__ = "leave_policies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    leave_type = Column(String(50), nullable=False)
    policy_name = Column(String(255), nullable=False)
    days_per_year = Column(Numeric(5, 2), nullable=False)
    max_carry_forward = Column(Numeric(5, 2), default=0)
    requires_approval = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)