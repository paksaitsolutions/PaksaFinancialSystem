#!/usr/bin/env python3
"""
Fix missing model attributes referenced in main.py
"""
import sqlite3

def fix_missing_attributes():
    """Add missing columns to existing tables"""
    conn = sqlite3.connect('paksa_financial.db')
    cursor = conn.cursor()
    
    try:
        # Fix ChartOfAccounts - add balance column if missing
        cursor.execute("PRAGMA table_info(chart_of_accounts)")
        columns = [row[1] for row in cursor.fetchall()]
        if 'balance' not in columns:
            cursor.execute("ALTER TABLE chart_of_accounts ADD COLUMN balance DECIMAL(15,2) DEFAULT 0")
            print("Added balance column to chart_of_accounts")
        
        # Fix JournalEntry - add total_amount column if missing
        cursor.execute("PRAGMA table_info(journal_entries)")
        columns = [row[1] for row in cursor.fetchall()]
        if 'total_amount' not in columns:
            cursor.execute("ALTER TABLE journal_entries ADD COLUMN total_amount DECIMAL(15,2) DEFAULT 0")
            print("Added total_amount column to journal_entries")
        
        # Fix Employee - add department column if missing
        cursor.execute("PRAGMA table_info(employees)")
        columns = [row[1] for row in cursor.fetchall()]
        if 'department' not in columns:
            cursor.execute("ALTER TABLE employees ADD COLUMN department TEXT")
            print("Added department column to employees")
        
        # Fix Department - add manager_name and employee_count if missing
        cursor.execute("PRAGMA table_info(departments)")
        columns = [row[1] for row in cursor.fetchall()]
        if 'manager_name' not in columns:
            cursor.execute("ALTER TABLE departments ADD COLUMN manager_name TEXT")
            print("Added manager_name column to departments")
        if 'employee_count' not in columns:
            cursor.execute("ALTER TABLE departments ADD COLUMN employee_count INTEGER DEFAULT 0")
            print("Added employee_count column to departments")
        
        # Fix InventoryItem - add sku column if missing
        cursor.execute("PRAGMA table_info(inventory_items)")
        columns = [row[1] for row in cursor.fetchall()]
        if 'sku' not in columns:
            cursor.execute("ALTER TABLE inventory_items ADD COLUMN sku TEXT")
            print("Added sku column to inventory_items")
        
        # Fix PayrollRun - add missing columns
        cursor.execute("PRAGMA table_info(payroll_runs)")
        columns = [row[1] for row in cursor.fetchall()]
        if 'pay_period' not in columns:
            cursor.execute("ALTER TABLE payroll_runs ADD COLUMN pay_period TEXT")
            print("Added pay_period column to payroll_runs")
        if 'total_gross_pay' not in columns:
            cursor.execute("ALTER TABLE payroll_runs ADD COLUMN total_gross_pay DECIMAL(15,2) DEFAULT 0")
            print("Added total_gross_pay column to payroll_runs")
        if 'employee_count' not in columns:
            cursor.execute("ALTER TABLE payroll_runs ADD COLUMN employee_count INTEGER DEFAULT 0")
            print("Added employee_count column to payroll_runs")
        
        # Fix TaxRate - add rate column if missing
        cursor.execute("PRAGMA table_info(tax_rates)")
        columns = [row[1] for row in cursor.fetchall()]
        if 'rate' not in columns:
            cursor.execute("ALTER TABLE tax_rates ADD COLUMN rate DECIMAL(5,4) DEFAULT 0")
            print("Added rate column to tax_rates")
        
        # Create missing tables if they don't exist
        
        # CashTransaction table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS cash_transactions (
            id TEXT PRIMARY KEY,
            bank_account_id TEXT,
            transaction_type TEXT DEFAULT 'deposit',
            amount DECIMAL(15,2) DEFAULT 0,
            transaction_date DATE,
            description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_by TEXT,
            updated_by TEXT
        )
        """)
        print("Created/verified cash_transactions table")
        
        # InventoryLocation table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory_locations (
            id TEXT PRIMARY KEY,
            location_name TEXT,
            address TEXT,
            capacity INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_by TEXT,
            updated_by TEXT
        )
        """)
        print("Created/verified inventory_locations table")
        
        # Payslip table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS payslips (
            id TEXT PRIMARY KEY,
            employee_id TEXT,
            pay_period TEXT,
            gross_pay DECIMAL(15,2) DEFAULT 0,
            net_pay DECIMAL(15,2) DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_by TEXT,
            updated_by TEXT
        )
        """)
        print("Created/verified payslips table")
        
        # TaxReturn table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tax_returns_missing (
            id TEXT PRIMARY KEY,
            tax_period TEXT,
            return_type TEXT,
            status TEXT DEFAULT 'draft',
            amount_due DECIMAL(15,2) DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_by TEXT,
            updated_by TEXT
        )
        """)
        print("Created/verified tax_returns_missing table")
        
        conn.commit()
        print("All missing attributes and tables fixed successfully!")
        
    except Exception as e:
        print(f"Error fixing attributes: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_missing_attributes()