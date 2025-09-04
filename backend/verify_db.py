"""
Verify and initialize the database if needed.
"""
import os
import sys
from sqlalchemy import inspect, create_engine
from sqlalchemy.orm import sessionmaker

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine, Base, SessionLocal
from app.core.config import settings

def check_database():
    """Check if database exists and is accessible."""
    print("🔍 Checking database...")
    
    # Check if database file exists
    db_path = os.path.abspath("paksa_finance.db")
    if not os.path.exists(db_path):
        print(f"⚠️  Database file not found at: {db_path}")
        return False
    
    print(f"✅ Database file exists at: {db_path}")
    
    # Check if we can connect to the database
    try:
        with SessionLocal() as db:
            # Try to execute a simple query
            result = db.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in result.fetchall()]
            
            if not tables:
                print("⚠️  Database is empty (no tables found)")
                return False
                
            print(f"✅ Database is accessible. Found {len(tables)} tables.")
            return True
            
    except Exception as e:
        print(f"❌ Error accessing database: {str(e)}")
        return False

def initialize_database():
    """Initialize the database by creating all tables."""
    print("\n🔄 Initializing database...")
    
    try:
        # Import all models to ensure they are registered with SQLAlchemy
        from app.models import user, department, employee
        from app.modules.core_financials.payroll import models as payroll_models
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        
        # Create default data if needed
        create_default_data()
        
        return True
        
    except Exception as e:
        print(f"❌ Error initializing database: {str(e)}")
        return False

def create_default_data():
    """Create default data in the database."""
    print("\n📝 Creating default data...")
    
    db = SessionLocal()
    try:
        from app.models.user import User
        from app.core.security import get_password_hash
        
        # Check if superuser exists
        existing_user = db.query(User).filter(
            User.email == settings.FIRST_SUPERUSER_EMAIL
        ).first()
        
        if not existing_user:
            # Create superuser
            hashed_password = get_password_hash(settings.FIRST_SUPERUSER_PASSWORD)
            superuser = User(
                email=settings.FIRST_SUPERUSER_EMAIL,
                hashed_password=hashed_password,
                first_name="System",
                last_name="Administrator",
                is_active=True,
                is_superuser=True
            )
            db.add(superuser)
            db.commit()
            print(f"✅ Created superuser: {settings.FIRST_SUPERUSER_EMAIL}")
        else:
            print("ℹ️  Superuser already exists")
            
    except Exception as e:
        print(f"❌ Error creating default data: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    if not check_database():
        print("\n🔄 Database needs initialization...")
        if initialize_database():
            print("\n🎉 Database setup completed successfully!")
        else:
            print("\n❌ Failed to initialize database")
            sys.exit(1)
    else:
        print("\n✅ Database is already set up and accessible")
