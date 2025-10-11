# Import unified payroll models from core_models to eliminate duplicates
from app.models.core_models import (
    Employee,
    PayrollRun,
    PayrollEntry,
    LeaveRequest,
    Department
)

# Create aliases for compatibility
PayRun = PayrollRun

# All core payroll models are now unified in core_models.py
# Extended payroll functionality remains here

from app.models.base import Base
from sqlalchemy import Column, String, Boolean, ForeignKey, Date, DateTime, Numeric, Text, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from enum import Enum
import uuid
from datetime import date, datetime

class PayrollStatus(str, Enum):
    DRAFT = "draft"
    PROCESSING = "processing"
    APPROVED = "approved"
    PAID = "paid"
    CANCELLED = "cancelled"

class PayFrequency(str, Enum):
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"

class PayRunEmployee(Base):
    """Pay run employee association."""
    
    __tablename__ = "payroll_run_employees"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pay_run_id = Column(UUID(as_uuid=True), ForeignKey("payroll_runs.id"), nullable=False)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    
    # Pay calculations
    gross_pay = Column(Numeric(precision=18, scale=2), nullable=False)
    total_deductions = Column(Numeric(precision=18, scale=2), default=0)
    total_taxes = Column(Numeric(precision=18, scale=2), default=0)
    net_pay = Column(Numeric(precision=18, scale=2), nullable=False)
    
    # Hours (for hourly employees)
    regular_hours = Column(Numeric(precision=8, scale=2), default=0)
    overtime_hours = Column(Numeric(precision=8, scale=2), default=0)
    
    # Status
    is_processed = Column(Boolean, default=False)
    
    # Relationships
    pay_run = relationship("PayrollRun")
    employee = relationship("Employee")
    
    def __repr__(self):
        return f"<PayRunEmployee {self.employee.full_name}: {self.net_pay}>"

class Payslip(Base):
    """Payslip model."""
    
    __tablename__ = "payroll_slips"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payslip_number = Column(String(50), unique=True, nullable=False, index=True)
    pay_run_id = Column(UUID(as_uuid=True), ForeignKey("payroll_runs.id"), nullable=False)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    
    # Pay period
    pay_period_start = Column(Date, nullable=False)
    pay_period_end = Column(Date, nullable=False)
    pay_date = Column(Date, nullable=False)
    
    # Earnings
    base_salary = Column(Numeric(precision=18, scale=2), default=0)
    overtime_pay = Column(Numeric(precision=18, scale=2), default=0)
    bonus = Column(Numeric(precision=18, scale=2), default=0)
    commission = Column(Numeric(precision=18, scale=2), default=0)
    allowances = Column(Numeric(precision=18, scale=2), default=0)
    gross_pay = Column(Numeric(precision=18, scale=2), nullable=False)
    
    # Deductions
    federal_tax = Column(Numeric(precision=18, scale=2), default=0)
    state_tax = Column(Numeric(precision=18, scale=2), default=0)
    social_security = Column(Numeric(precision=18, scale=2), default=0)
    medicare = Column(Numeric(precision=18, scale=2), default=0)
    health_insurance = Column(Numeric(precision=18, scale=2), default=0)
    retirement_401k = Column(Numeric(precision=18, scale=2), default=0)
    other_deductions = Column(Numeric(precision=18, scale=2), default=0)
    total_deductions = Column(Numeric(precision=18, scale=2), default=0)
    
    # Net pay
    net_pay = Column(Numeric(precision=18, scale=2), nullable=False)
    
    # Hours
    regular_hours = Column(Numeric(precision=8, scale=2), default=0)
    overtime_hours = Column(Numeric(precision=8, scale=2), default=0)
    
    # Status
    is_paid = Column(Boolean, default=False)
    paid_date = Column(Date)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    pay_run = relationship("PayrollRun")
    employee = relationship("Employee")
    
    def __repr__(self):
        return f"<Payslip {self.payslip_number}: {self.net_pay}>"

class PayrollItem(Base):
    """Payroll items (earnings, deductions, taxes)."""
    
    __tablename__ = "payroll_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    item_type = Column(String(20), nullable=False)  # earning, deduction, tax
    category = Column(String(50))
    
    # Calculation
    is_taxable = Column(Boolean, default=True)
    is_pre_tax = Column(Boolean, default=False)
    calculation_method = Column(String(20), default="fixed")  # fixed, percentage, formula
    default_amount = Column(Numeric(precision=18, scale=2), default=0)
    percentage = Column(Numeric(precision=5, scale=4), default=0)
    
    # GL Integration
    expense_account = Column(String(20))
    liability_account = Column(String(20))
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<PayrollItem {self.code}: {self.name}>"

class EmployeePayrollItem(Base):
    """Employee-specific payroll items."""
    
    __tablename__ = "employee_payroll_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    payroll_item_id = Column(UUID(as_uuid=True), ForeignKey("payroll_items.id"), nullable=False)
    
    # Override values
    amount = Column(Numeric(precision=18, scale=2))
    percentage = Column(Numeric(precision=5, scale=4))
    is_active = Column(Boolean, default=True)
    
    # Effective dates
    effective_date = Column(Date, default=date.today)
    end_date = Column(Date)
    
    # Relationships
    employee = relationship("Employee")
    payroll_item = relationship("PayrollItem")
    
    def __repr__(self):
        return f"<EmployeePayrollItem {self.employee.full_name}: {self.payroll_item.name}>"