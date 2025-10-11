"""
Attendance tracking models
"""
from datetime import date, time, datetime
from sqlalchemy import Column, String, Date, Time, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.models.base import Base

class AttendanceRecord(Base):
    __tablename__ = "hrm_attendance_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    employee_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=False)
    date = Column(Date, nullable=False)
    check_in_time = Column(Time, nullable=True)
    check_out_time = Column(Time, nullable=True)
    hours_worked = Column(String(10), nullable=True)  # Format: "HH:MM"
    status = Column(String(20), nullable=False, default='present')
    notes = Column(Text, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    employee = relationship("Employee")