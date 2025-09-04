"""
Create a new SQLite database with all required tables.
"""
import os
import sys
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import Base, engine, SessionLocal
from app.core.config import settings

def create_database():
    """Create a new database with all tables."""
    db_path = os.path.abspath("paksa_finance.db")
    
    # Remove existing database file if it exists
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"Removed existing database: {db_path}")
        except Exception as e:
            print(f"Error removing existing database: {str(e)}")
            return False
    
    try:
        # Import all models to ensure they are registered with SQLAlchemy
        print("Importing models...")
        from app.models import (
            user, department, employee, attendance, leave, 
            payroll_processing, payslip, tax, company_settings
        )
        
        # Create all tables
        print("Creating tables...")
        Base.metadata.create_all(bind=engine)
        
        # Verify tables were created
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if not tables:
            print("❌ No tables were created!")
            return False
            
        print(f"\n✅ Successfully created {len(tables)} tables:")
        for table in tables:
            print(f"- {table}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating database: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== Creating New Database ===\n")
    if create_database():
        print("\n✅ Database created successfully!")
        print(f"Location: {os.path.abspath('paksa_finance.db')}")
    else:
        print("\n❌ Failed to create database")
        sys.exit(1)
