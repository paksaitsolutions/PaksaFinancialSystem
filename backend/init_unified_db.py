#!/usr/bin/env python3
"""
Initialize Database with Unified Models
Creates all tables and seed data for production deployment
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import engine, SessionLocal
from app.models.base import Base
from app.models.core_models import *
from app.models.user import User
from app.core.security import get_password_hash
import uuid
from datetime import datetime, date
from decimal import Decimal

def create_tables():
    """Create all tables from unified models"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ All tables created successfully")

def seed_basic_data():
    """Seed essential data for system operation"""
    db = SessionLocal()
    try:
        print("Seeding basic data...")
        
        # Create default company
        company = Company(
            company_code="PAKSA",
            company_name="Paksa Financial Demo",
            legal_name="Paksa Financial Systems Ltd",
            base_currency="USD",
            fiscal_year_end="12-31",
            status=CompanyStatus.ACTIVE
        )
        db.add(company)
        db.flush()
        
        # Create default currencies
        currencies = [
            Currency(currency_code="USD", currency_name="US Dollar", symbol="$"),
            Currency(currency_code="EUR", currency_name="Euro", symbol="€"),
            Currency(currency_code="GBP", currency_name="British Pound", symbol="£"),
        ]
        for currency in currencies:
            db.add(currency)
        
        # Create basic chart of accounts
        accounts = [
            # Assets
            ChartOfAccounts(company_id=company.id, account_code="1000", account_name="Cash", account_type="Asset", normal_balance="Debit"),
            ChartOfAccounts(company_id=company.id, account_code="1200", account_name="Accounts Receivable", account_type="Asset", normal_balance="Debit"),
            ChartOfAccounts(company_id=company.id, account_code="1500", account_name="Inventory", account_type="Asset", normal_balance="Debit"),
            # Liabilities
            ChartOfAccounts(company_id=company.id, account_code="2000", account_name="Accounts Payable", account_type="Liability", normal_balance="Credit"),
            ChartOfAccounts(company_id=company.id, account_code="2100", account_name="Accrued Expenses", account_type="Liability", normal_balance="Credit"),
            # Equity
            ChartOfAccounts(company_id=company.id, account_code="3000", account_name="Owner's Equity", account_type="Equity", normal_balance="Credit"),
            # Revenue
            ChartOfAccounts(company_id=company.id, account_code="4000", account_name="Sales Revenue", account_type="Revenue", normal_balance="Credit"),
            # Expenses
            ChartOfAccounts(company_id=company.id, account_code="5000", account_name="Cost of Goods Sold", account_type="Expense", normal_balance="Debit"),
            ChartOfAccounts(company_id=company.id, account_code="6000", account_name="Operating Expenses", account_type="Expense", normal_balance="Debit"),
        ]
        for account in accounts:
            db.add(account)
        
        # Create sample customers
        customers = [
            Customer(
                company_id=company.id,
                customer_code="CUST001",
                customer_name="ABC Corporation",
                email="contact@abc.com",
                phone="555-0123",
                address="123 Business St",
                credit_limit=Decimal("50000"),
                current_balance=Decimal("15000"),
                payment_terms="net30",
                status=CustomerStatus.ACTIVE
            ),
            Customer(
                company_id=company.id,
                customer_code="CUST002", 
                customer_name="XYZ Industries",
                email="info@xyz.com",
                phone="555-0456",
                address="456 Industry Ave",
                credit_limit=Decimal("75000"),
                current_balance=Decimal("-2500"),
                payment_terms="net30",
                status=CustomerStatus.ACTIVE
            )
        ]
        for customer in customers:
            db.add(customer)
        
        # Create sample vendors
        vendors = [
            Vendor(
                company_id=company.id,
                vendor_code="VEND001",
                vendor_name="ABC Supplies",
                email="sales@abcsupplies.com",
                phone="555-1000",
                address="789 Supply St",
                payment_terms="net30",
                status=VendorStatus.ACTIVE
            )
        ]
        for vendor in vendors:
            db.add(vendor)
        
        # Create sample departments
        departments = [
            Department(
                company_id=company.id,
                department_code="ADMIN",
                department_name="Administration",
                cost_center="CC001"
            ),
            Department(
                company_id=company.id,
                department_code="SALES",
                department_name="Sales",
                cost_center="CC002"
            )
        ]
        for dept in departments:
            db.add(dept)
        
        # Create sample employees
        employees = [
            Employee(
                company_id=company.id,
                employee_code="EMP001",
                first_name="John",
                last_name="Doe",
                email="john.doe@paksa.com",
                hire_date=date.today(),
                department_id=departments[0].id,
                position="Administrator",
                salary=Decimal("75000"),
                employment_type=EmploymentType.FULL_TIME
            )
        ]
        for emp in employees:
            db.add(emp)
        
        # Create admin user
        admin_user = User(
            email="admin@paksa.com",
            hashed_password=get_password_hash("admin123"),
            full_name="System Administrator",
            is_active=True,
            is_superuser=True
        )
        db.add(admin_user)
        
        db.commit()
        print("✅ Basic data seeded successfully")
        
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def main():
    """Main initialization function"""
    print("🚀 Initializing Paksa Financial System Database...")
    
    try:
        create_tables()
        seed_basic_data()
        print("✅ Database initialization completed successfully!")
        print("📊 System ready for production use")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()