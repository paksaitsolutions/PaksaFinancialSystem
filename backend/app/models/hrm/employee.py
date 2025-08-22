"""
Employee models.
"""
import uuid
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import Column, String, Boolean, Date, DateTime, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base

class Employee(Base):
    """Employee model."""
    
    __tablename__ = "employee"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    employee_id = Column(String(50), nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, index=True)
    phone = Column(String(20))
    
    # Employment details
    department = Column(String(100))
    position = Column(String(100))
    manager_id = Column(UUID(as_uuid=True))
    hire_date = Column(Date, nullable=False)
    employment_type = Column(String(20), default="full_time")  # full_time, part_time, contract
    
    # Compensation
    salary = Column(Numeric(precision=18, scale=2))
    currency_code = Column(String(3), default="USD")
    
    # Personal info
    date_of_birth = Column(Date)
    address = Column(Text)
    emergency_contact = Column(String(200))
    emergency_phone = Column(String(20))
    
    # Status
    is_active = Column(Boolean, default=True)
    termination_date = Column(Date)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    leave_requests = relationship("LeaveRequest", back_populates="employee")
    attendance_records = relationship("AttendanceRecord", back_populates="employee")
    performance_reviews = relationship("PerformanceReview", back_populates="employee")