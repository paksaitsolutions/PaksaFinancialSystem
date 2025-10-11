#!/usr/bin/env python3
"""
Test script to identify model import conflicts
"""
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_model_imports():
    """Test importing all models to identify conflicts"""
    print("Testing model imports...")
    
    try:
        print("1. Testing base models...")
        from app.models.base import Base, BaseModel, AuditMixin
        print("   Base models imported successfully")
        
        print("2. Testing core unified models...")
        from app.models.core_models import (
            ChartOfAccounts, JournalEntry, JournalEntryLine,
            Vendor, Customer, APInvoice, APPayment, ARInvoice, ARPayment
        )
        print("   Core unified models imported successfully")
        
        print("3. Testing model registry...")
        from app.models import (
            ChartOfAccounts as ImportedChartOfAccounts,
            JournalEntry as ImportedJournalEntry,
            APPayment as ImportedAPPayment
        )
        print("   Models imported from __init__.py successfully")
        
        print("4. Testing SQLAlchemy registry...")
        from sqlalchemy import inspect
        from app.core.database import engine
        
        # Check if there are duplicate class names in the registry
        registry = Base.registry._class_registry
        print(f"   Total classes in registry: {len(registry)}")
        
        # Look for duplicate names
        class_names = {}
        for key, cls in registry.items():
            if hasattr(cls, '__name__'):
                name = cls.__name__
                if name in class_names:
                    print(f"   WARNING: Duplicate class name found: {name}")
                    print(f"      - {class_names[name]}")
                    print(f"      - {cls}")
                else:
                    class_names[name] = cls
        
        print("5. Testing specific problematic models...")
        # Test APPayment specifically
        print(f"   APPayment class: {APPayment}")
        print(f"   APPayment table name: {APPayment.__tablename__}")
        
        # Test JournalEntry specifically  
        print(f"   JournalEntry class: {JournalEntry}")
        print(f"   JournalEntry table name: {JournalEntry.__tablename__}")
        
        print("\nAll model imports successful!")
        return True
        
    except Exception as e:
        print(f"\nModel import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_creation():
    """Test database table creation"""
    print("\nTesting database table creation...")
    
    try:
        from app.core.database import engine
        from app.models.base import Base
        
        # Try to create all tables
        print("Creating all tables...")
        Base.metadata.create_all(bind=engine)
        print("All tables created successfully!")
        return True
        
    except Exception as e:
        print(f"Database creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Paksa Financial System - Model Testing")
    print("=" * 50)
    
    success = True
    
    # Test model imports
    if not test_model_imports():
        success = False
    
    # Test database creation
    if not test_database_creation():
        success = False
    
    if success:
        print("\nAll tests passed!")
    else:
        print("\nSome tests failed!")
        sys.exit(1)