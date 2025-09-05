#!/usr/bin/env python3
"""
Initialize Complete Accounting Database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.core.database import engine
from app.models.base import Base
from app.models.accounting import *

def init_accounting_tables():
    """Initialize all accounting tables"""
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ All accounting tables created successfully")
        
        with engine.connect() as conn:
            # Chart of Accounts
            conn.execute(text("""
                INSERT OR IGNORE INTO chart_of_accounts (id, account_code, account_name, account_type, balance, created_at, updated_at)
                VALUES 
                (1, '1000', 'Cash', 'ASSET', 50000.00, datetime('now'), datetime('now')),
                (2, '1200', 'Accounts Receivable', 'ASSET', 25000.00, datetime('now'), datetime('now')),
                (3, '2000', 'Accounts Payable', 'LIABILITY', 15000.00, datetime('now'), datetime('now')),
                (4, '3000', 'Owner Equity', 'EQUITY', 100000.00, datetime('now'), datetime('now')),
                (5, '4000', 'Sales Revenue', 'REVENUE', 45000.00, datetime('now'), datetime('now')),
                (6, '5000', 'Office Expenses', 'EXPENSE', 8000.00, datetime('now'), datetime('now'))
            """))
            
            # Vendors
            conn.execute(text("""
                INSERT OR IGNORE INTO vendors (id, vendor_code, vendor_name, email, phone, is_active, created_at, updated_at)
                VALUES 
                (1, 'V001', 'Office Supplies Inc', 'contact@officesupplies.com', '555-0101', 1, datetime('now'), datetime('now')),
                (2, 'V002', 'Tech Solutions Ltd', 'info@techsolutions.com', '555-0102', 1, datetime('now'), datetime('now'))
            """))
            
            # Customers
            conn.execute(text("""
                INSERT OR IGNORE INTO customers (id, customer_code, customer_name, email, phone, credit_limit, is_active, created_at, updated_at)
                VALUES 
                (1, 'C001', 'ABC Corporation', 'billing@abccorp.com', '555-0201', 50000.00, 1, datetime('now'), datetime('now')),
                (2, 'C002', 'XYZ Industries', 'accounts@xyzind.com', '555-0202', 75000.00, 1, datetime('now'), datetime('now'))
            """))
            
            # Tax Codes
            conn.execute(text("""
                INSERT OR IGNORE INTO tax_codes (id, code, name, rate, tax_type, is_active, created_at, updated_at)
                VALUES 
                (1, 'ST', 'Sales Tax', 0.0825, 'SALES', 1, datetime('now'), datetime('now')),
                (2, 'VAT', 'Value Added Tax', 0.10, 'VAT', 1, datetime('now'), datetime('now'))
            """))
            
            conn.commit()
            print("✅ Sample accounting data inserted successfully")
            
    except Exception as e:
        print(f"❌ Error creating accounting tables: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Initializing Complete Accounting Database...")
    success = init_accounting_tables()
    if success:
        print("✅ Accounting module database initialization completed!")
    else:
        print("❌ Accounting module database initialization failed!")
        sys.exit(1)