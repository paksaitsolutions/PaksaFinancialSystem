"""
Script to create all required database tables for Paksa Financial System modules.
"""
import os
import sys
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import all models to ensure they are registered with SQLAlchemy
from app.models import (
    user, department, employee, attendance, leave,
    payroll_processing, payslip, tax, company_settings,
    # Add other models as they are created
)

from app.core.database import Base
from app.core.config import settings

def create_tables():
    """Create all database tables defined in the models."""
    try:
        # Create engine
        engine = create_engine(
            settings.DATABASE_URL,
            connect_args={"check_same_thread": False},
            echo=True
        )
        
        print("\n🔧 Creating database tables...")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        # Verify tables were created
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if not tables:
            print("\n❌ No tables were created!")
            return False
            
        print("\n✅ Successfully created/updated tables:")
        for table in sorted(tables):
            print(f"- {table}")
            
        return True
        
    except Exception as e:
        print(f"\n❌ Error creating tables: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== Paksa Financial System - Database Setup ===\n")
    print(f"Database: {settings.DATABASE_URL}")
    
    if create_tables():
        print("\n✅ Database tables created/updated successfully!")
    else:
        print("\n❌ Failed to create/update database tables!")
        sys.exit(1)
