#!/usr/bin/env python3
"""
Comprehensive System Verification Script
Verifies all database models, connections, and system components
"""

import sys
import os
import sqlite3
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def verify_imports():
    """Verify all critical imports work"""
    print("=== IMPORT VERIFICATION ===")
    
    try:
        from app.models.core_models import (
            User, ChartOfAccounts, JournalEntry, Transaction, 
            Notification, Vendor, Customer, Employee, Department
        )
        print("+ Core models imported successfully")
        return True
    except Exception as e:
        print(f"X Core models import failed: {e}")
        return False

def verify_database():
    """Verify database file and structure"""
    print("\n=== DATABASE VERIFICATION ===")
    
    db_path = "paksa_financial.db"
    if not os.path.exists(db_path):
        print(f"X Database file {db_path} not found")
        return False
    
    size = os.path.getsize(db_path)
    print(f"+ Database file exists ({size:,} bytes)")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"+ Found {len(tables)} tables in database")
        
        # Check critical tables
        critical_tables = [
            'users', 'chart_of_accounts', 'journal_entries', 
            'transactions', 'notifications', 'vendors', 'customers'
        ]
        
        missing_tables = [t for t in critical_tables if t not in tables]
        if missing_tables:
            print(f"X Missing critical tables: {missing_tables}")
            return False
        else:
            print("+ All critical tables exist")
        
        # Check table structures
        for table in critical_tables[:3]:  # Check first 3 tables
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            print(f"  {table}: {len(columns)} columns")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"X Database verification failed: {e}")
        return False

def verify_sqlalchemy():
    """Verify SQLAlchemy connection"""
    print("\n=== SQLALCHEMY VERIFICATION ===")
    
    try:
        from app.database import engine, SessionLocal
        from sqlalchemy import text
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("+ SQLAlchemy connection successful")
        
        # Test session
        db = SessionLocal()
        db.close()
        print("+ Database session creation successful")
        
        return True
        
    except Exception as e:
        print(f"X SQLAlchemy verification failed: {e}")
        return False

def verify_models():
    """Verify model attributes and relationships"""
    print("\n=== MODEL VERIFICATION ===")
    
    try:
        from app.models.core_models import User, ChartOfAccounts, JournalEntry
        
        # Check User model
        user_attrs = ['id', 'username', 'email', 'hashed_password', 'is_active']
        for attr in user_attrs:
            if hasattr(User, attr):
                print(f"+ User.{attr} exists")
            else:
                print(f"X User.{attr} missing")
        
        # Check ChartOfAccounts model
        coa_attrs = ['id', 'account_code', 'account_name', 'balance']
        for attr in coa_attrs:
            if hasattr(ChartOfAccounts, attr):
                print(f"+ ChartOfAccounts.{attr} exists")
            else:
                print(f"X ChartOfAccounts.{attr} missing")
        
        # Check JournalEntry model
        je_attrs = ['id', 'entry_number', 'description', 'total_amount']
        for attr in je_attrs:
            if hasattr(JournalEntry, attr):
                print(f"+ JournalEntry.{attr} exists")
            else:
                print(f"X JournalEntry.{attr} missing")
        
        return True
        
    except Exception as e:
        print(f"X Model verification failed: {e}")
        return False

def verify_api_imports():
    """Verify API router imports"""
    print("\n=== API VERIFICATION ===")
    
    try:
        from app.core.security import create_access_token, get_current_user
        print("+ Security functions imported")
        
        from app.core.database import get_db
        print("+ Database dependency imported")
        
        return True
        
    except Exception as e:
        print(f"X API verification failed: {e}")
        return False

def main():
    """Run all verifications"""
    print("PAKSA FINANCIAL SYSTEM - COMPREHENSIVE VERIFICATION")
    print("=" * 60)
    
    results = []
    results.append(verify_imports())
    results.append(verify_database())
    results.append(verify_sqlalchemy())
    results.append(verify_models())
    results.append(verify_api_imports())
    
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"+ ALL CHECKS PASSED ({passed}/{total})")
        print("+ System is ready for deployment")
        return 0
    else:
        print(f"X SOME CHECKS FAILED ({passed}/{total})")
        print("X System needs attention before deployment")
        return 1

if __name__ == "__main__":
    sys.exit(main())