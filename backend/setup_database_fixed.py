"""
Script to set up the SQLAlchemy database with correct configuration.
"""
import os
import sys
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import settings directly to avoid any import issues
from app.core.config.settings import settings

# Define the database URL explicitly
db_url = "sqlite:///paksa_financial.db"
print(f"Using database: {os.path.abspath(db_url.replace('sqlite:///', ''))}")

def setup_database():
    """Set up the database with all required tables."""
    try:
        # Create engine with echo=True to see SQL statements
        engine = create_engine(
            db_url,
            connect_args={"check_same_thread": False},
            echo=True
        )
        
        # Import all models to ensure they are registered with SQLAlchemy
        print("\n🔍 Importing models...")
        from app.models import (
            user, department, employee, attendance, leave,
            payroll_processing, payslip, tax, company_settings
        )
        
        # Create all tables
        print("\n🛠️  Creating tables...")
        from app.core.database import Base
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
            # Check if user already exists
            if not db.query(User).filter(User.email == "admin@example.com").first():
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
            else:
                print("ℹ️  Test user already exists")
                
            return True
            
        except Exception as e:
            db.rollback()
            print(f"❌ Error creating test user: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            db.close()
            
    except Exception as e:
        print(f"\n❌ Error setting up database: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== Database Setup ===\n")
    if setup_database():
        print("\n✅ Database setup completed successfully!")
        print(f"Database location: {os.path.abspath(db_url.replace('sqlite:///', ''))}")
    else:
        print("\n❌ Database setup failed!")
        sys.exit(1)
