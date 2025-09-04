"""
Test database connections for all modules.
"""
import os
import sys
from sqlalchemy import inspect, text
from sqlalchemy.orm import sessionmaker

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine, SessionLocal
from app.core.config import settings

def check_table_exists(table_name, db):
    """Check if a table exists in the database."""
    return inspect(engine).has_table(table_name)

def test_core_tables():
    """Test core database tables."""
    print("\n=== Testing Core Tables ===")
    with SessionLocal() as db:
        # Test users table (should exist in most applications)
        if check_table_exists("users", db):
            print("✅ Users table exists")
        else:
            print("❌ Users table is missing")

def test_payroll_tables():
    """Test payroll module tables."""
    print("\n=== Testing Payroll Tables ===")
    tables = [
        "payroll_employees",
        "payroll_runs",
        "payroll_items",
        "payroll_codes",
        "payslips"
    ]
    
    with SessionLocal() as db:
        for table in tables:
            if check_table_exists(table, db):
                print(f"✅ {table} exists")
            else:
                print(f"❌ {table} is missing")

def test_accounting_tables():
    """Test accounting module tables."""
    print("\n=== Testing Accounting Tables ===")
    tables = [
        "gl_accounts",
        "journal_entries",
        "accounting_periods",
        "accounting_entries"
    ]
    
    with SessionLocal() as db:
        for table in tables:
            if check_table_exists(table, db):
                print(f"✅ {table} exists")
            else:
                print(f"❌ {table} is missing")

def test_ar_ap_tables():
    """Test AR/AP module tables."""
    print("\n=== Testing AR/AP Tables ===")
    tables = [
        "customers",
        "customer_invoices",
        "customer_payments",
        "vendors",
        "vendor_bills",
        "vendor_payments"
    ]
    
    with SessionLocal() as db:
        for table in tables:
            if check_table_exists(table, db):
                print(f"✅ {table} exists")
            else:
                print(f"❌ {table} is missing")

def test_fixed_assets_tables():
    """Test fixed assets tables."""
    print("\n=== Testing Fixed Assets Tables ===")
    tables = [
        "fixed_assets",
        "asset_categories",
        "depreciation_schedules",
        "asset_disposals"
    ]
    
    with SessionLocal() as db:
        for table in tables:
            if check_table_exists(table, db):
                print(f"✅ {table} exists")
            else:
                print(f"❌ {table} is missing")

def test_taxation_tables():
    """Test taxation module tables."""
    print("\n=== Testing Taxation Tables ===")
    tables = [
        "tax_codes",
        "tax_rates",
        "tax_transactions",
        "tax_filings"
    ]
    
    with SessionLocal() as db:
        for table in tables:
            if check_table_exists(table, db):
                print(f"✅ {table} exists")
            else:
                print(f"❌ {table} is missing")

def test_database_connection():
    """Test database connection and basic operations."""
    print("=== Testing Database Connection ===")
    try:
        with SessionLocal() as db:
            # Test connection with a simple query
            result = db.execute(text("SELECT 1"))
            if result.scalar() == 1:
                print("✅ Database connection successful")
            else:
                print("❌ Database connection failed")
    except Exception as e:
        print(f"❌ Database connection error: {str(e)}")

if __name__ == "__main__":
    test_database_connection()
    test_core_tables()
    test_payroll_tables()
    test_accounting_tables()
    test_ar_ap_tables()
    test_fixed_assets_tables()
    test_taxation_tables()
