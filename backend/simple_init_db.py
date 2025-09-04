#!/usr/bin/env python3
"""
Simple Database Initialization
"""

import sqlite3
import os

def init_simple_db():
    """Initialize database with simple SQL"""
    
    db_path = "paksa_financial.db"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Chart of Accounts
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chart_of_accounts (
                id INTEGER PRIMARY KEY,
                account_code TEXT UNIQUE NOT NULL,
                account_name TEXT NOT NULL,
                account_type TEXT NOT NULL,
                parent_id INTEGER,
                is_active BOOLEAN DEFAULT 1,
                balance DECIMAL(15,2) DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Vendors
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vendors (
                id INTEGER PRIMARY KEY,
                vendor_code TEXT UNIQUE NOT NULL,
                vendor_name TEXT NOT NULL,
                contact_person TEXT,
                email TEXT,
                phone TEXT,
                address TEXT,
                tax_id TEXT,
                payment_terms TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Customers
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY,
                customer_code TEXT UNIQUE NOT NULL,
                customer_name TEXT NOT NULL,
                contact_person TEXT,
                email TEXT,
                phone TEXT,
                address TEXT,
                credit_limit DECIMAL(15,2) DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert sample data
        cursor.execute("""
            INSERT OR IGNORE INTO chart_of_accounts (id, account_code, account_name, account_type, balance)
            VALUES 
            (1, '1000', 'Cash', 'ASSET', 50000.00),
            (2, '1200', 'Accounts Receivable', 'ASSET', 25000.00),
            (3, '2000', 'Accounts Payable', 'LIABILITY', 15000.00),
            (4, '3000', 'Owner Equity', 'EQUITY', 100000.00),
            (5, '4000', 'Sales Revenue', 'REVENUE', 45000.00),
            (6, '5000', 'Office Expenses', 'EXPENSE', 8000.00)
        """)
        
        cursor.execute("""
            INSERT OR IGNORE INTO vendors (id, vendor_code, vendor_name, email, phone)
            VALUES 
            (1, 'V001', 'Office Supplies Inc', 'contact@officesupplies.com', '555-0101'),
            (2, 'V002', 'Tech Solutions Ltd', 'info@techsolutions.com', '555-0102')
        """)
        
        cursor.execute("""
            INSERT OR IGNORE INTO customers (id, customer_code, customer_name, email, phone, credit_limit)
            VALUES 
            (1, 'C001', 'ABC Corporation', 'billing@abccorp.com', '555-0201', 50000.00),
            (2, 'C002', 'XYZ Industries', 'accounts@xyzind.com', '555-0202', 75000.00)
        """)
        
        conn.commit()
        print("Database initialized successfully")
        print(f"Database created at: {os.path.abspath(db_path)}")
        
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        conn.close()
    
    return True

if __name__ == "__main__":
    print("Initializing Simple Database...")
    success = init_simple_db()
    if success:
        print("Database initialization completed!")
    else:
        print("Database initialization failed!")