"""
HRM Employee models
"""
from datetime import date, datetime
from sqlalchemy import Column, String, Date, Boolean, Numeric, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.models.base import Base

class Employee(Base):
    __tablename__ = "hrm_employees"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    employee_id = Column(String(50), unique=True, index=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    middle_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone_number = Column(String(50), nullable=False)
    
    # Employment Details
    job_title = Column(String(100), nullable=False)
    department = Column(String(100), nullable=True)
    hire_date = Column(Date, nullable=False)
    termination_date = Column(Date, nullable=True)
    employment_type = Column(String(50), nullable=False, default='FULL_TIME')
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Personal Details
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(1), nullable=True)
    marital_status = Column(String(20), nullable=True)
    national_id = Column(String(50), nullable=True)
    
    # Address
    address_line1 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)
    
    # Compensation
    base_salary = Column(Numeric(15, 2), nullable=False, default=0)
    currency = Column(String(3), default='USD', nullable=False)
    payment_method = Column(String(50), nullable=False, default='BANK_TRANSFER')
    payment_frequency = Column(String(20), nullable=False, default='MONTHLY')
    
    # Bank Details
    bank_name = Column(String(100), nullable=True)
    account_number = Column(String(50), nullable=True)
    
    # Audit Fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    leave_requests = relationship("LeaveRequest", back_populates="employee")
    attendance_records = relationship("AttendanceRecord", back_populates="employee")
    
    def __repr__(self):
        return f"<Employee {self.employee_id}: {self.first_name} {self.last_name}>"
    
    @property
    def full_name(self):
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
    
    @classmethod
    def authenticate(cls, db, email: str, password: str):
        # Simple authentication for demo - in production use proper password hashing
        employee = db.query(cls).filter(cls.email == email).first()
        return employee if employee else None