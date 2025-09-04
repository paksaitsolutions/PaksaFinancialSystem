import os
import sys
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

# Database configuration
DB_PATH = 'paksa_finance_new.db'
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

# Create SQLAlchemy engine and session
engine = create_engine(f'sqlite:///{DB_PATH}', echo=True)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

# Department Model
class Department(Base):
    __tablename__ = 'departments'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    parent_id = Column(String(36), ForeignKey('departments.id'), nullable=True)
    manager_id = Column(String(36), nullable=True)
    cost_center = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employees = relationship('Employee', back_populates='department')
    parent = relationship('Department', remote_side=[id], backref='subdepartments')

# Employee Model
class Employee(Base):
    __tablename__ = 'employees'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20), nullable=True)
    hire_date = Column(DateTime, nullable=False)
    job_title = Column(String(100), nullable=False)
    department_id = Column(String(36), ForeignKey('departments.id'), nullable=False)
    salary = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    department = relationship('Department', back_populates='employees')
    payroll_items = relationship('PayrollItem', back_populates='employee')

# PayrollRun Model
class PayrollRun(Base):
    __tablename__ = 'payroll_runs'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    status = Column(String(20), default='draft')
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = relationship('PayrollItem', back_populates='payroll_run')

# PayrollItem Model
class PayrollItem(Base):
    __tablename__ = 'payroll_items'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    payroll_run_id = Column(String(36), ForeignKey('payroll_runs.id'), nullable=False)
    employee_id = Column(String(36), ForeignKey('employees.id'), nullable=False)
    item_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    amount = Column(Float, nullable=False)
    tax_amount = Column(Float, default=0.0)
    net_amount = Column(Float, nullable=False)
    status = Column(String(20), default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    payroll_run = relationship('PayrollRun', back_populates='items')
    employee = relationship('Employee', back_populates='payroll_items')

def create_database():
    try:
        # Create all tables
        Base.metadata.create_all(engine)
        
        # Create test data
        with session.begin():
            # Create departments
            hr_dept = Department(
                name='Human Resources',
                code='HR',
                description='HR Department',
                is_active=True
            )
            it_dept = Department(
                name='Information Technology',
                code='IT',
                description='IT Department',
                is_active=True
            )
            session.add_all([hr_dept, it_dept])
            
            # Create employees
            emp1 = Employee(
                first_name='John',
                last_name='Doe',
                email='john.doe@example.com',
                hire_date=datetime(2023, 1, 1),
                job_title='HR Manager',
                department=hr_dept,
                salary=80000.00
            )
            emp2 = Employee(
                first_name='Jane',
                last_name='Smith',
                email='jane.smith@example.com',
                hire_date=datetime(2023, 2, 1),
                job_title='Software Developer',
                department=it_dept,
                salary=90000.00
            )
            session.add_all([emp1, emp2])
            
            # Create payroll run
            payroll_run = PayrollRun(
                name='September 2023 Payroll',
                start_date=datetime(2023, 9, 1),
                end_date=datetime(2023, 9, 30),
                status='completed'
            )
            session.add(payroll_run)
            
            # Create payroll items
            item1 = PayrollItem(
                payroll_run=payroll_run,
                employee=emp1,
                item_type='salary',
                description='Monthly Salary',
                amount=6666.67,
                tax_amount=1333.33,
                net_amount=5333.34,
                status='paid'
            )
            item2 = PayrollItem(
                payroll_run=payroll_run,
                employee=emp2,
                item_type='salary',
                description='Monthly Salary',
                amount=7500.00,
                tax_amount=1500.00,
                net_amount=6000.00,
                status='paid'
            )
            session.add_all([item1, item2])
            
            session.commit()
        
        print(f"\nSuccessfully created database at: {os.path.abspath(DB_PATH)}")
        return True
        
    except Exception as e:
        print(f"\nError creating database: {e}")
        session.rollback()
        return False
    finally:
        session.close()
        engine.dispose()

if __name__ == "__main__":
    print("=== Creating New Database ===\n")
    if create_database():
        print("\nDatabase created successfully!")
        print(f"Location: {os.path.abspath(DB_PATH)}")
    else:
        print("\nFailed to create database.")
        sys.exit(1)
