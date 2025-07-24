"""
Employee models for the Payroll module.
"""
from datetime import date
from sqlalchemy import Column, String, Date, Enum, ForeignKey, Numeric, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.core.database import Base
from app.modules.core_financials.payroll.models.base import PayrollBase


class Employee(PayrollBase, Base):
    """Employee model for payroll processing."""
    __tablename__ = "payroll_employees"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    employee_id = Column(String(50), unique=True, index=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    middle_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(Enum('M', 'F', 'O', name='gender_enum'), nullable=False)
    marital_status = Column(
        Enum('SINGLE', 'MARRIED', 'DIVORCED', 'WIDOWED', name='marital_status_enum'),
        nullable=False
    )
    national_id = Column(String(50), unique=True, nullable=True)
    social_security_number = Column(String(50), unique=True, nullable=True)
    tax_identification_number = Column(String(50), unique=True, nullable=True)
    
    # Contact Information
    email = Column(String(255), unique=True, nullable=False)
    phone_number = Column(String(50), nullable=False)
    address_line1 = Column(String(255), nullable=False)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    postal_code = Column(String(20), nullable=False)
    country = Column(String(100), nullable=False)
    
    # Employment Details
    hire_date = Column(Date, nullable=False)
    termination_date = Column(Date, nullable=True)
    employment_type = Column(
        Enum('FULL_TIME', 'PART_TIME', 'CONTRACT', 'TEMPORARY', 'INTERN', name='employment_type_enum'),
        nullable=False
    )
    job_title = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False)
    manager_id = Column(UUID(as_uuid=True), ForeignKey('payroll_employees.id'), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Bank Details
    bank_name = Column(String(100), nullable=True)
    bank_branch = Column(String(100), nullable=True)
    account_number = Column(String(50), nullable=True)
    account_type = Column(String(50), nullable=True)  # e.g., 'savings', 'checking'
    
    # Compensation
    base_salary = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), default='USD', nullable=False)
    payment_method = Column(
        Enum('BANK_TRANSFER', 'CHECK', 'CASH', 'OTHER', name='payment_method_enum'),
        nullable=False
    )
    payment_frequency = Column(
        Enum('WEEKLY', 'BI_WEEKLY', 'SEMI_MONTHLY', 'MONTHLY', name='payment_frequency_enum'),
        nullable=False
    )
    
    # Relationships
    manager = relationship("Employee", remote_side=[id], backref="subordinates")
    payslips = relationship("Payslip", back_populates="employee")
    
    # Audit Fields
    created_at = Column(Date, default=date.today, nullable=False)
    updated_at = Column(Date, default=date.today, onupdate=date.today, nullable=False)
    
    def __repr__(self):
        return f"<Employee {self.employee_id}: {self.first_name} {self.last_name}>"
    
    @property
    def full_name(self):
        """Return the full name of the employee."""
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_currently_employed(self):
        """Check if the employee is currently employed."""
        if not self.is_active:
            return False
        if self.termination_date and self.termination_date < date.today():
            return False
        return True
