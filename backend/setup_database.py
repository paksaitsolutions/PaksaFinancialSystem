import os
import sys
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

def generate_uuid():
    return str(uuid.uuid4())

# Create a new SQLite database file
DB_PATH = 'paksa_financial_new.db'
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

# Create engine and session
engine = create_engine(f'sqlite:///{DB_PATH}', echo=True)
Session = sessionmaker(bind=engine)
session = Session()

# Base class for models
Base = declarative_base()

# Define the Department model
class Department(Base):
    __tablename__ = 'departments'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    parent_id = Column(String(36), ForeignKey('departments.id'), nullable=True)
    manager_id = Column(String(36), nullable=True)  # Would reference users table
    cost_center = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employees = relationship('Employee', back_populates='department')
    parent = relationship('Department', remote_side=[id], backref='subdepartments')

# Define the Employee model
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

# Define the PayrollRun model
class PayrollRun(Base):
    __tablename__ = 'payroll_runs'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    status = Column(String(20), default='draft')  # draft, processing, completed, paid
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = relationship('PayrollItem', back_populates='payroll_run')

# Define the PayrollItem model
class PayrollItem(Base):
    __tablename__ = 'payroll_items'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    payroll_run_id = Column(String(36), ForeignKey('payroll_runs.id'), nullable=False)
    employee_id = Column(String(36), ForeignKey('employees.id'), nullable=False)
    item_type = Column(String(50), nullable=False)  # salary, bonus, deduction, etc.
    description = Column(Text, nullable=True)
    amount = Column(Float, nullable=False)
    tax_amount = Column(Float, default=0.0)
    net_amount = Column(Float, nullable=False)
    status = Column(String(20), default='pending')  # pending, approved, paid
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    payroll_run = relationship('PayrollRun', back_populates='items')
    employee = relationship('Employee', back_populates='payroll_items')

def create_database():
    try:
        # Create all tables
        Base.metadata.create_all(engine)
        print(f"\nSuccessfully created database at: {os.path.abspath(DB_PATH)}")
        
        # Create a test department
        with session.begin():
            # Create HR department
            hr_dept = Department(
                name='Human Resources',
                code='HR',
                description='Human Resources Department',
                is_active=True
            )
            session.add(hr_dept)
            
            # Create IT department
            it_dept = Department(
                name='Information Technology',
                code='IT',
                description='IT Support and Development',
                is_active=True
            )
            session.add(it_dept)
            
            # Create a test employee
            test_employee = Employee(
                first_name='John',
                last_name='Doe',
                email='john.doe@example.com',
                phone='1234567890',
                hire_date=datetime(2023, 1, 1),
                job_title='HR Manager',
                department=hr_dept,
                salary=75000.00,
                is_active=True
            )
            session.add(test_employee)
            
            # Create a test payroll run
            payroll_run = PayrollRun(
                name='September 2023 Payroll',
                start_date=datetime(2023, 9, 1),
                end_date=datetime(2023, 9, 30),
                status='completed'
            )
            session.add(payroll_run)
            
            # Create a test payroll item
            payroll_item = PayrollItem(
                payroll_run=payroll_run,
                employee=test_employee,
                item_type='salary',
                description='Monthly Salary - September 2023',
                amount=6250.00,
                tax_amount=1250.00,
                net_amount=5000.00,
                status='paid'
            )
            session.add(payroll_item)
            
            session.commit()
            
        print("\nSuccessfully added test data to the database.")
        
        # Verify the data was added
        with session() as s:
            dept_count = s.query(Department).count()
            emp_count = s.query(Employee).count()
            run_count = s.query(PayrollRun).count()
            item_count = s.query(PayrollItem).count()
            
        print(f"\nDatabase contains:")
        print(f"- {dept_count} departments")
        print(f"- {emp_count} employees")
        print(f"- {run_count} payroll runs")
        print(f"- {item_count} payroll items")
        
        return True
        
    except Exception as e:
        print(f"\nError creating database: {e}")
        session.rollback()
        return False
    finally:
        session.close()
        engine.dispose()

if __name__ == "__main__":
    print("=== Setting Up New Database ===\n")
    if create_database():
        print("\nDatabase setup completed successfully!")
        print(f"Database file created at: {os.path.abspath(DB_PATH)}")
    else:
        print("\nFailed to set up the database.")
        sys.exit(1)
