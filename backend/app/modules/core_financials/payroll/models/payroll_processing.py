"""
Payroll processing models for the Payroll module.
"""
from sqlalchemy import Column, String, Float, Date, ForeignKey, Enum, JSON, Boolean, Integer, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from app.core.database import Base

class PayrollRun(Base):
    """
    Represents a payroll run/cycle.
    """
    __tablename__ = "payroll_runs"
    
    id = Column(String(36), primary_key=True, index=True)
    pay_period_start = Column(Date, nullable=False)
    pay_period_end = Column(Date, nullable=False)
    payment_date = Column(Date, nullable=False)
    status = Column(String(20), nullable=False, default="draft")  # draft, processing, processed, paid, cancelled
    notes = Column(String(500), nullable=True)
    total_gross = Column(Float, default=0.0)
    total_deductions = Column(Float, default=0.0)
    total_net = Column(Float, default=0.0)
    currency = Column(String(3), default="USD")
    meta_data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    items = relationship("PayrollItem", back_populates="payroll_run", cascade="all, delete-orphan")


class PayrollItem(Base):
    """
    Represents an individual payroll item for an employee in a payroll run.
    """
    __tablename__ = "payroll_items"
    
    id = Column(String(36), primary_key=True, index=True)
    payroll_run_id = Column(String(36), ForeignKey("payroll_runs.id"), nullable=False)
    employee_id = Column(String(36), ForeignKey("employees.id"), nullable=False)
    
    # Earnings
    gross_pay = Column(Float, default=0.0)
    base_salary = Column(Float, default=0.0)
    overtime_pay = Column(Float, default=0.0)
    bonus_pay = Column(Float, default=0.0)
    commission_pay = Column(Float, default=0.0)
    other_earnings = Column(Float, default=0.0)
    
    # Deductions
    tax_withheld = Column(Float, default=0.0)
    benefits_deductions = Column(Float, default=0.0)
    other_deductions = Column(Float, default=0.0)
    
    # Net pay
    net_pay = Column(Float, default=0.0)
    
    # Payment info
    payment_method = Column(String(50), nullable=True)
    payment_reference = Column(String(100), nullable=True)
    
    # Status
    status = Column(String(20), default="pending")  # pending, paid, failed, cancelled
    
    # Metadata
    meta_data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    payroll_run = relationship("PayrollRun", back_populates="items")
    employee = relationship("Employee", back_populates="payroll_items")
    
    def calculate_net_pay(self):
        """Calculate net pay based on earnings and deductions."""
        total_earnings = (self.base_salary + self.overtime_pay + 
                         self.bonus_pay + self.commission_pay + self.other_earnings)
        total_deductions = (self.tax_withheld + self.benefits_deductions + 
                           self.other_deductions)
        self.net_pay = total_earnings - total_deductions
        return self.net_pay
