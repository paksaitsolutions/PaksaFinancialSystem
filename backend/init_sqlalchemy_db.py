"""
Initialize a new SQLAlchemy database with all required tables.
"""
import os
import sys
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, Session

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import Base
from app.core.config import settings

def init_db():
    """Initialize the database with all tables."""
    # Create the database directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(settings.DATABASE_URL.replace("sqlite:///", ""))), exist_ok=True)
    
    # Create engine with echo=True to see SQL statements
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},  # SQLite specific
        echo=True  # Show SQL statements
    )
    
    print(f"\n🔧 Initializing database at: {settings.DATABASE_URL}")
    
    try:
        # Import all models to ensure they are registered with SQLAlchemy
        print("\n📋 Registering models...")
        from app.models import (
            user, department, employee, attendance, leave,
            payroll_processing, payslip, tax, company_settings
        )
        
        # Drop all existing tables
        print("\n🗑️  Dropping existing tables...")
        Base.metadata.drop_all(bind=engine)
        
        # Create all tables
        print("\n🔄 Creating tables...")
        Base.metadata.create_all(bind=engine)
        
        # Verify tables were created
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if not tables:
            print("\n❌ No tables were created!")
            return False
            
        print("\n✅ Successfully created tables:")
        for table in tables:
            print(f"- {table}")
        
        # Create a test user
        print("\n👤 Creating test user...")
        from app.models.user import User
        from app.core.security import get_password_hash
        
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            test_user = User(
                email="admin@example.com",
                hashed_password=get_password_hash("admin123"),
                full_name="Admin User",
                is_superuser=True,
                is_active=True
            )
            db.add(test_user)
            db.commit()
            print("✅ Created test user: admin@example.com / admin123")
        except Exception as e:
            db.rollback()
            print(f"⚠️  Could not create test user: {str(e)}")
        finally:
            db.close()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error initializing database: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== SQLAlchemy Database Initialization ===\n")
    if init_db():
        print("\n✅ Database initialization completed successfully!")
        print(f"Database location: {os.path.abspath(settings.DATABASE_URL.replace('sqlite:///', ''))}")
    else:
        print("\n❌ Database initialization failed!")
        sys.exit(1)
