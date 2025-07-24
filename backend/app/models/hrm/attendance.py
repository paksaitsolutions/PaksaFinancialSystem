"""
Attendance tracking models.
"""
import uuid
from datetime import date, datetime, time
from sqlalchemy import Column, String, Boolean, ForeignKey, Date, DateTime, Time, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base

class AttendanceRecord(Base):
    """Attendance record model."""
    
    __tablename__ = "attendance_record"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employee.id"), nullable=False)
    
    date = Column(Date, nullable=False, index=True)
    check_in_time = Column(DateTime)
    check_out_time = Column(DateTime)
    
    # Break times
    break_start = Column(DateTime)
    break_end = Column(DateTime)
    
    # Calculated fields
    hours_worked = Column(String(10))  # HH:MM format
    overtime_hours = Column(String(10))
    
    status = Column(String(20), default="present")  # present, absent, late, half_day
    notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employee = relationship("Employee", back_populates="attendance_records")

class WorkSchedule(Base):
    """Work schedule model."""
    
    __tablename__ = "work_schedule"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    schedule_name = Column(String(100), nullable=False)
    
    # Weekly schedule
    monday_start = Column(Time)
    monday_end = Column(Time)
    tuesday_start = Column(Time)
    tuesday_end = Column(Time)
    wednesday_start = Column(Time)
    wednesday_end = Column(Time)
    thursday_start = Column(Time)
    thursday_end = Column(Time)
    friday_start = Column(Time)
    friday_end = Column(Time)
    saturday_start = Column(Time)
    saturday_end = Column(Time)
    sunday_start = Column(Time)
    sunday_end = Column(Time)
    
    # Break duration in minutes
    break_duration = Column(String(10), default="60")
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)