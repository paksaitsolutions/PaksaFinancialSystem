import sqlite3
import os
from datetime import datetime

def create_gl_database():
    # Remove existing database if it exists
    if os.path.exists('gl_database.db'):
        os.remove('gl_database.db')
    
    # Connect to SQLite database (creates it if it doesn't exist)
    conn = sqlite3.connect('gl_database.db')
    cursor = conn.cursor()
    
    # Enable foreign key constraints
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # Create GL Accounts table
    cursor.execute('''
    CREATE TABLE gl_accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_code TEXT NOT NULL UNIQUE,
        account_name TEXT NOT NULL,
        account_type TEXT NOT NULL,
        parent_id INTEGER,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (parent_id) REFERENCES gl_accounts(id)
    )
    ''')
    
    # Create Journal Entries table
    cursor.execute('''
    CREATE TABLE journal_entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entry_number TEXT NOT NULL UNIQUE,
        entry_date DATE NOT NULL,
        reference TEXT,
        description TEXT,
        status TEXT DEFAULT 'DRAFT',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create Journal Entry Lines table
    cursor.execute('''
    CREATE TABLE journal_entry_lines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        journal_entry_id INTEGER NOT NULL,
        account_id INTEGER NOT NULL,
        line_number INTEGER NOT NULL,
        debit_amount DECIMAL(15, 2) DEFAULT 0,
        credit_amount DECIMAL(15, 2) DEFAULT 0,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (journal_entry_id) REFERENCES journal_entries(id),
        FOREIGN KEY (account_id) REFERENCES gl_accounts(id)
    )
    ''')
    
    # Create Accounting Periods table
    cursor.execute('''
    CREATE TABLE accounting_periods (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        period_name TEXT NOT NULL UNIQUE,
        start_date DATE NOT NULL,
        end_date DATE NOT NULL,
        is_closed BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Insert sample chart of accounts
    chart_of_accounts = [
        ('1000', 'Current Assets', 'ASSET', None),
        ('1100', 'Cash and Cash Equivalents', 'ASSET', 1),
        ('1200', 'Accounts Receivable', 'ASSET', 1),
        ('2000', 'Liabilities', 'LIABILITY', None),
        ('2100', 'Accounts Payable', 'LIABILITY', 4),
        ('3000', 'Equity', 'EQUITY', None),
        ('4000', 'Revenue', 'REVENUE', None),
        ('5000', 'Expenses', 'EXPENSE', None)
    ]
    
    cursor.executemany('''
    INSERT INTO gl_accounts (account_code, account_name, account_type, parent_id)
    VALUES (?, ?, ?, ?)
    ''', [(code, name, acc_type, parent) for code, name, acc_type, parent in chart_of_accounts])
    
    # Insert sample accounting period
    cursor.execute('''
    INSERT INTO accounting_periods (period_name, start_date, end_date)
    VALUES (?, ?, ?)
    ''', ('JAN-2024', '2024-01-01', '2024-01-31'))
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("✅ Successfully created GL database with sample data!")
    print("\nTables created:")
    print("- gl_accounts (with sample chart of accounts)")
    print("- journal_entries")
    print("- journal_entry_lines")
    print("- accounting_periods (with sample period)")
    print("\nDatabase file: gl_database.db")

if __name__ == "__main__":
    print("Creating General Ledger database...")
    create_gl_database()
