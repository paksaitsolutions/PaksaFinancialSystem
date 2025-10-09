"""
Complete payroll models for the financial system.
"""
import uuid
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import Column, String, Boolean, ForeignKey, Date, DateTime, Numeric, Text, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from enum import Enum

from app.models.base import Base

class EmploymentType(str, Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    TEMPORARY = "temporary"
    INTERN = "intern"

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

class Employee(Base):
    """Employee model for payroll."""
    
    __tablename__ = "payroll_employees"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(String(50), unique=True, nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone_number = Column(String(20))
    
    # Employment details
    department = Column(String(100), nullable=False)
    job_title = Column(String(100), nullable=False)
    employment_type = Column(String(20), default=EmploymentType.FULL_TIME)
    hire_date = Column(Date, nullable=False, default=date.today)
    termination_date = Column(Date)
    
    # Compensation
    base_salary = Column(Numeric(precision=18, scale=2), nullable=False)
    pay_frequency = Column(String(20), default=PayFrequency.MONTHLY)
    
    # Tax information
    tax_id = Column(String(50))
    tax_exemptions = Column(Integer, default=0)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    pay_runs = relationship("PayRunEmployee", back_populates="employee")
    payslips = relationship("Payslip", back_populates="employee")
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f"<Employee {self.employee_id}: {self.full_name}>"

class PayRun(Base):
    """Pay run model."""
    
    __tablename__ = "pay_runs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_number = Column(String(50), unique=True, nullable=False, index=True)
    pay_period_start = Column(Date, nullable=False)
    pay_period_end = Column(Date, nullable=False)
    pay_date = Column(Date, nullable=False)
    
    # Status and processing
    status = Column(String(20), default=PayrollStatus.DRAFT)
    processed_at = Column(DateTime)
    approved_at = Column(DateTime)
    approved_by = Column(UUID(as_uuid=True))
    
    # Totals
    total_gross_pay = Column(Numeric(precision=18, scale=2), default=0)
    total_deductions = Column(Numeric(precision=18, scale=2), default=0)
    total_net_pay = Column(Numeric(precision=18, scale=2), default=0)
    total_taxes = Column(Numeric(precision=18, scale=2), default=0)
    
    # Metadata
    notes = Column(Text)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True))
    
    # Relationships
    employees = relationship("PayRunEmployee", back_populates="pay_run", cascade="all, delete-orphan")
    payslips = relationship("Payslip", back_populates="pay_run")
    
    def __repr__(self):
        return f"<PayRun {self.run_number}: {self.status}>"

class PayRunEmployee(Base):
    """Pay run employee association."""
    
    __tablename__ = "pay_run_employees"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pay_run_id = Column(UUID(as_uuid=True), ForeignKey("pay_runs.id"), nullable=False)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("payroll_employees.id"), nullable=False)
    
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
    pay_run = relationship("PayRun", back_populates="employees")
    employee = relationship("Employee", back_populates="pay_runs")
    
    def __repr__(self):
        return f"<PayRunEmployee {self.employee.full_name}: {self.net_pay}>"

class Payslip(Base):
    """Payslip model."""
    
    __tablename__ = "payslips"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payslip_number = Column(String(50), unique=True, nullable=False, index=True)
    pay_run_id = Column(UUID(as_uuid=True), ForeignKey("pay_runs.id"), nullable=False)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("payroll_employees.id"), nullable=False)
    
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
    pay_run = relationship("PayRun", back_populates="payslips")
    employee = relationship("Employee", back_populates="payslips")
    
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
    employee_id = Column(UUID(as_uuid=True), ForeignKey("payroll_employees.id"), nullable=False)
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