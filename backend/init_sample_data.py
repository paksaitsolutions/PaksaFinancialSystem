#!/usr/bin/env python3
"""
Initialize Paksa Financial System with sample data
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal, init_db
from app.models.core_models import *
from app.models.user import User
from app.core.security import get_password_hash
import uuid
from datetime import datetime, date

def init_sample_data():
    """Initialize database with sample data"""
    print("Initializing database...")
    init_db()
    
    db = SessionLocal()
    try:
        # Create sample company
        company = db.query(Company).first()
        if not company:
            company = Company(
                id=uuid.uuid4(),
                company_code="PAKSA001",
                company_name="Paksa Financial Demo",
                legal_name="Paksa Financial Systems Inc.",
                tax_id="12-3456789",
                address="123 Business St, Finance City, FC 12345",
                phone="(555) 123-4567",
                email="info@paksa.com",
                base_currency="USD"
            )
            db.add(company)
            db.commit()
            print("[OK] Sample company created")

        # Create chart of accounts
        if db.query(ChartOfAccounts).count() == 0:
            accounts = [
                {"code": "1000", "name": "Cash", "type": "Asset", "balance": 50000},
                {"code": "1200", "name": "Accounts Receivable", "type": "Asset", "balance": 25000},
                {"code": "1300", "name": "Inventory", "type": "Asset", "balance": 75000},
                {"code": "1500", "name": "Equipment", "type": "Asset", "balance": 100000},
                {"code": "2000", "name": "Accounts Payable", "type": "Liability", "balance": 15000},
                {"code": "2100", "name": "Notes Payable", "type": "Liability", "balance": 50000},
                {"code": "3000", "name": "Owner's Equity", "type": "Equity", "balance": 185000},
                {"code": "4000", "name": "Sales Revenue", "type": "Revenue", "balance": 0},
                {"code": "5000", "name": "Cost of Goods Sold", "type": "Expense", "balance": 0},
                {"code": "6000", "name": "Operating Expenses", "type": "Expense", "balance": 0}
            ]
            
            for acc_data in accounts:
                account = ChartOfAccounts(
                    id=uuid.uuid4(),
                    company_id=company.id,
                    account_code=acc_data["code"],
                    account_name=acc_data["name"],
                    account_type=acc_data["type"],
                    balance=acc_data["balance"],
                    is_active=True
                )
                db.add(account)
            db.commit()
            print("[OK] Chart of accounts created")

        # Create sample customers
        if db.query(Customer).count() == 0:
            customers = [
                {"name": "ABC Corporation", "email": "billing@abc-corp.com", "phone": "(555) 111-2222", "credit_limit": 50000},
                {"name": "XYZ Industries", "email": "ap@xyz-industries.com", "phone": "(555) 333-4444", "credit_limit": 75000},
                {"name": "Tech Solutions Ltd", "email": "finance@techsolutions.com", "phone": "(555) 555-6666", "credit_limit": 25000}
            ]
            
            for i, cust_data in enumerate(customers, 1):
                customer = Customer(
                    id=uuid.uuid4(),
                    company_id=company.id,
                    customer_code=f"CUST{i:04d}",
                    customer_name=cust_data["name"],
                    email=cust_data["email"],
                    phone=cust_data["phone"],
                    credit_limit=cust_data["credit_limit"],
                    current_balance=0,
                    payment_terms="net30",
                    status="active"
                )
                db.add(customer)
            db.commit()
            print("[OK] Sample customers created")

        # Create sample vendors
        if db.query(Vendor).count() == 0:
            vendors = [
                {"name": "Office Supplies Co", "email": "orders@officesupplies.com", "phone": "(555) 777-8888"},
                {"name": "Equipment Rental Inc", "email": "billing@equiprental.com", "phone": "(555) 999-0000"},
                {"name": "Professional Services LLC", "email": "invoices@proservices.com", "phone": "(555) 222-3333"}
            ]
            
            for i, vend_data in enumerate(vendors, 1):
                vendor = Vendor(
                    id=uuid.uuid4(),
                    company_id=company.id,
                    vendor_code=f"VEND{i:04d}",
                    vendor_name=vend_data["name"],
                    email=vend_data["email"],
                    phone=vend_data["phone"],
                    current_balance=0,
                    payment_terms="net30",
                    status="active"
                )
                db.add(vendor)
            db.commit()
            print("[OK] Sample vendors created")

        # Create sample employees
        if db.query(Employee).count() == 0:
            employees = [
                {"first": "John", "last": "Doe", "email": "john.doe@paksa.com", "position": "Accountant", "salary": 65000},
                {"first": "Jane", "last": "Smith", "email": "jane.smith@paksa.com", "position": "Financial Analyst", "salary": 70000},
                {"first": "Mike", "last": "Johnson", "email": "mike.johnson@paksa.com", "position": "Controller", "salary": 85000}
            ]
            
            for i, emp_data in enumerate(employees, 1):
                employee = Employee(
                    id=uuid.uuid4(),
                    company_id=company.id,
                    employee_code=f"EMP{i:04d}",
                    first_name=emp_data["first"],
                    last_name=emp_data["last"],
                    email=emp_data["email"],
                    position=emp_data["position"],
                    salary=emp_data["salary"],
                    hire_date=date.today(),
                    status="active"
                )
                db.add(employee)
            db.commit()
            print("[OK] Sample employees created")

        # Create admin user if not exists
        admin_user = db.query(User).filter(User.email == "admin@paksa.com").first()
        if not admin_user:
            admin_user = User(
                id=uuid.uuid4(),
                email="admin@paksa.com",
                hashed_password=get_password_hash("admin123"),
                first_name="System",
                last_name="Administrator",
                is_active=True,
                is_superuser=True
            )
            db.add(admin_user)
            db.commit()
            print("[OK] Admin user created")

        print("\n[SUCCESS] Sample data initialization completed successfully!")
        print("Login credentials: admin@paksa.com / admin123")
        
    except Exception as e:
        print(f"[ERROR] Error initializing sample data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_sample_data()