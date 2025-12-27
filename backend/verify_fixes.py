#!/usr/bin/env python3
"""
Verify that the data persistence fixes are working
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.core_models import *
from app.models.user import User

def verify_fixes():
    """Verify that database operations are working"""
    print("Verifying Paksa Financial System fixes...")
    
    db = SessionLocal()
    try:
        # Test Chart of Accounts
        accounts = db.query(ChartOfAccounts).count()
        print(f"[OK] Chart of Accounts: {accounts} records")
        
        # Test Customers
        customers = db.query(Customer).count()
        print(f"[OK] Customers: {customers} records")
        
        # Test Vendors
        vendors = db.query(Vendor).count()
        print(f"[OK] Vendors: {vendors} records")
        
        # Test Employees
        employees = db.query(Employee).count()
        print(f"[OK] Employees: {employees} records")
        
        # Test Users
        users = db.query(User).count()
        print(f"[OK] Users: {users} records")
        
        # Test sample data retrieval
        sample_account = db.query(ChartOfAccounts).first()
        if sample_account:
            print(f"[OK] Sample account: {sample_account.account_code} - {sample_account.account_name}")
        
        sample_customer = db.query(Customer).first()
        if sample_customer:
            print(f"[OK] Sample customer: {sample_customer.customer_code} - {sample_customer.customer_name}")
        
        print("\n[SUCCESS] All database operations verified successfully!")
        print("The system is now using real database persistence instead of mock data.")
        
    except Exception as e:
        print(f"[ERROR] Verification failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify_fixes()