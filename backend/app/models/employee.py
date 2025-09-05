from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, Integer, Date
from sqlalchemy.types import DECIMAL as Decimal
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime

class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(String, primary_key=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    employee_number = Column(String(20), unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255))
    phone = Column(String(50))
    address = Column(Text)
    hire_date = Column(Date, nullable=False)
    termination_date = Column(Date)
    job_title = Column(String(255))
    department = Column(String(100))
    salary = Column(Decimal(15, 2))
    hourly_rate = Column(Decimal(10, 2))
    employment_type = Column(String(50))  # full-time, part-time, contract
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PayRun(Base):
    __tablename__ = "pay_runs"
    
    id = Column(String, primary_key=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    pay_period_start = Column(Date, nullable=False)
    pay_period_end = Column(Date, nullable=False)
    pay_date = Column(Date, nullable=False)
    total_gross_pay = Column(Decimal(15, 2), default=0)
    total_deductions = Column(Decimal(15, 2), default=0)
    total_net_pay = Column(Decimal(15, 2), default=0)
    status = Column(String(20), default="draft")
    processed_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

class Payslip(Base):
    __tablename__ = "payslips"
    
    id = Column(String, primary_key=True)
    pay_run_id = Column(String, ForeignKey("pay_runs.id"), nullable=False)
    employee_id = Column(String, ForeignKey("employees.id"), nullable=False)
    gross_pay = Column(Decimal(15, 2), default=0)
    total_deductions = Column(Decimal(15, 2), default=0)
    net_pay = Column(Decimal(15, 2), default=0)
    hours_worked = Column(Decimal(8, 2))
    overtime_hours = Column(Decimal(8, 2))
    created_at = Column(DateTime, default=datetime.utcnow)

class PayrollDeduction(Base):
    __tablename__ = "payroll_deductions"
    
    id = Column(String, primary_key=True)
    employee_id = Column(String, ForeignKey("employees.id"), nullable=False)
    deduction_type = Column(String(100), nullable=False)
    deduction_name = Column(String(255), nullable=False)
    amount = Column(Decimal(15, 2))
    percentage = Column(Decimal(5, 2))
    is_pre_tax = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class PayrollBenefit(Base):
    __tablename__ = "payroll_benefits"
    
    id = Column(String, primary_key=True)
    employee_id = Column(String, ForeignKey("employees.id"), nullable=False)
    benefit_type = Column(String(100), nullable=False)
    benefit_name = Column(String(255), nullable=False)
    employer_contribution = Column(Decimal(15, 2))
    employee_contribution = Column(Decimal(15, 2))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class LeaveRequest(Base):
    __tablename__ = "leave_requests"
    
    id = Column(String, primary_key=True)
    employee_id = Column(String, ForeignKey("employees.id"), nullable=False)
    leave_type = Column(String(50), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    days_requested = Column(Integer, nullable=False)
    reason = Column(Text)
    status = Column(String(20), default="pending")
    approved_by = Column(String, ForeignKey("users.id"))
    approved_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class Attendance(Base):
    __tablename__ = "attendance"
    
    id = Column(String, primary_key=True)
    employee_id = Column(String, ForeignKey("employees.id"), nullable=False)
    attendance_date = Column(Date, nullable=False)
    clock_in = Column(DateTime)
    clock_out = Column(DateTime)
    hours_worked = Column(Decimal(8, 2))
    overtime_hours = Column(Decimal(8, 2))
    status = Column(String(20), default="present")
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class Performance(Base):
    __tablename__ = "performance_reviews"
    
    id = Column(String, primary_key=True)
    employee_id = Column(String, ForeignKey("employees.id"), nullable=False)
    review_period_start = Column(Date, nullable=False)
    review_period_end = Column(Date, nullable=False)
    overall_rating = Column(Decimal(3, 2))
    goals_achieved = Column(Text)
    areas_for_improvement = Column(Text)
    reviewer_id = Column(String, ForeignKey("users.id"))
    status = Column(String(20), default="draft")
    created_at = Column(DateTime, default=datetime.utcnow)