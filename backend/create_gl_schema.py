import os
import sqlite3
from pathlib import Path

# Set up paths
project_root = Path(__file__).parent.parent
db_path = project_root / "paksa_financial.db"

# SQL statements for creating GL tables
SQL_CREATE_GL_ACCOUNTS = """
CREATE TABLE IF NOT EXISTS gl_accounts (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    account_code TEXT NOT NULL,
    account_name TEXT NOT NULL,
    account_type TEXT NOT NULL,
    parent_account_id TEXT,
    balance DECIMAL(15, 2) DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_account_id) REFERENCES gl_accounts (id)
);
"""

SQL_CREATE_JOURNAL_ENTRIES = """
CREATE TABLE IF NOT EXISTS journal_entries (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    entry_number TEXT NOT NULL,
    entry_date DATE NOT NULL,
    reference TEXT,
    description TEXT,
    status TEXT DEFAULT 'DRAFT',
    created_by TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

SQL_CREATE_JOURNAL_ENTRY_LINES = """
CREATE TABLE IF NOT EXISTS journal_entry_lines (
    id TEXT PRIMARY KEY,
    journal_entry_id TEXT NOT NULL,
    account_id TEXT NOT NULL,
    line_number INTEGER NOT NULL,
    debit_amount DECIMAL(15, 2) DEFAULT 0,
    credit_amount DECIMAL(15, 2) DEFAULT 0,
    description TEXT,
    reference TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (journal_entry_id) REFERENCES journal_entries (id),
    FOREIGN KEY (account_id) REFERENCES gl_accounts (id)
);
"""

SQL_CREATE_ACCOUNTING_PERIODS = """
CREATE TABLE IF NOT EXISTS accounting_periods (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    period_name TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status TEXT DEFAULT 'OPEN',
    is_closed BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(tenant_id, period_name)
);
"""

def create_database():
    """Create the SQLite database with GL tables."""
    try:
        # Remove existing database if it exists
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"Removed existing database: {db_path}")
        
        # Create database and tables
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        # Create tables
        cursor.executescript(SQL_CREATE_GL_ACCOUNTS)
        cursor.executescript(SQL_CREATE_JOURNAL_ENTRIES)
        cursor.executescript(SQL_CREATE_JOURNAL_ENTRY_LINES)
        cursor.executescript(SQL_CREATE_ACCOUNTING_PERIODS)
        
        # Commit changes and close connection
        conn.commit()
        conn.close()
        
        print(f"\n✅ Successfully created database: {db_path}")
        print("\nCreated tables:")
        print("- gl_accounts")
        print("- journal_entries")
        print("- journal_entry_lines")
        print("- accounting_periods")
        
    except Exception as e:
        print(f"\n❌ Error creating database: {e}")
        if 'conn' in locals():
            conn.close()
        raise

if __name__ == "__main__":
    print("Creating General Ledger database...")
    create_database()
