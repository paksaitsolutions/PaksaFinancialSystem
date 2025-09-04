"""
Script to set up a new database with all required tables.
"""
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import Base, engine, SessionLocal
from app.core.config import settings

def setup_database():
    """Set up the database with all required tables."""
    print("🚀 Setting up new database...")
    
    # Import all models to ensure they are registered with SQLAlchemy
    print("🔍 Importing models...")
    from app.models import (
        user, department, employee, attendance, leave, 
        payroll_processing, payslip, tax, company_settings
    )
    
    # Create all tables
    print("🔄 Creating tables...")
    Base.metadata.create_all(bind=engine)
    
    # Create default data
    print("📝 Creating default data...")
    create_default_data()
    
    print("✅ Database setup complete!")

def create_default_data():
    """Create default data in the database."""
    db = SessionLocal()
    
    try:
        # Create default company settings
        from app.models.company_settings import CompanySettings
        if not db.query(CompanySettings).first():
            company = CompanySettings(
                company_name="Paksa Financial Systems",
                base_currency="USD",
                fiscal_year_start="01-01",
                fiscal_year_end="12-31"
            )
            db.add(company)
        
        # Create default admin user
        from app.models.user import User
        from app.core.security import get_password_hash
        
        admin = db.query(User).filter(User.email == "admin@example.com").first()
        if not admin:
            admin = User(
                email="admin@example.com",
                hashed_password=get_password_hash("admin123"),
                first_name="Admin",
                last_name="User",
                is_active=True,
                is_superuser=True
            )
            db.add(admin)
        
        db.commit()
        print("✅ Created default admin user (admin@example.com / admin123)")
        
    except Exception as e:
        print(f"❌ Error creating default data: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Remove existing database file if it exists
    db_path = os.path.abspath("paksa_finance.db")
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"🗑️  Removed existing database: {db_path}")
        except Exception as e:
            print(f"❌ Error removing existing database: {str(e)}")
            sys.exit(1)
    
    # Set up new database
    setup_database()
    
    # Verify the database was created
    if os.path.exists(db_path):
        print(f"\n✅ Successfully created new database at: {db_path}")
        print("\nYou can now start the application with the new database.")
    else:
        print("\n❌ Failed to create database. Please check the error messages above.")
        sys.exit(1)
