from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, Decimal, Text, Boolean
from sqlalchemy.orm import relationship
from app.models.base import BaseModel, AuditModel

class Employee(AuditModel):
    __tablename__ = 'employees'
    
    employee_id = Column(String(20), unique=True, nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True)
    department = Column(String(50))
    position = Column(String(100))
    hire_date = Column(Date, nullable=False)
    salary = Column(Decimal(15, 2), nullable=False)
    pay_frequency = Column(String(20), default='monthly')
    
    payroll_records = relationship("PayrollRecord", back_populates="employee")

class PayrollRecord(AuditModel):
    __tablename__ = 'payroll_records'
    
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    pay_period_start = Column(Date, nullable=False)
    pay_period_end = Column(Date, nullable=False)
    pay_date = Column(Date, nullable=False)
    gross_pay = Column(Decimal(15, 2), nullable=False)
    total_deductions = Column(Decimal(15, 2), default=0)
    net_pay = Column(Decimal(15, 2), nullable=False)
    status = Column(String(20), default='draft')
    
    employee = relationship("Employee", back_populates="payroll_records")
    deductions = relationship("PayrollDeduction", back_populates="payroll_record")

class PayrollDeduction(BaseModel):
    __tablename__ = 'payroll_deductions'
    
    payroll_record_id = Column(Integer, ForeignKey('payroll_records.id'), nullable=False)
    deduction_type = Column(String(50), nullable=False)
    amount = Column(Decimal(15, 2), nullable=False)
    description = Column(Text)
    
    payroll_record = relationship("PayrollRecord", back_populates="deductions")
