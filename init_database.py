"""
Initialize the SQLAlchemy database with proper configuration.
"""
import os
import sys
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Define database URL
db_path = os.path.join(os.path.dirname(__file__), "paksa_financial.db")
db_url = f"sqlite:///{db_path}"

print(f"Initializing database at: {db_path}")

def setup_database():
    try:
        # Create engine
        engine = create_engine(
            db_url,
            connect_args={"check_same_thread": False},
            echo=True
        )
        
        # Import models
        print("\nImporting models...")
        from backend.app.models import (
            user, department, employee, attendance, leave,
            payroll_processing, payslip, tax, company_settings
        )
        
        # Create tables
        print("\nCreating database tables...")
        from backend.app.core.database import Base
        Base.metadata.create_all(bind=engine)
        
        # Verify tables
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if not tables:
            print("\n❌ No tables were created!")
            return False
            
        print("\n✅ Successfully created tables:")
        for table in tables:
            print(f"- {table}")
        
        # Create test user
        print("\nCreating test user...")
        from backend.app.models.user import User
        from backend.app.core.security import get_password_hash
        
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
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
    if setup_database():
        print("\n✅ Database setup completed successfully!")
        print(f"Database location: {os.path.abspath(db_path)}")
    else:
        print("\n❌ Database setup failed!")
        sys.exit(1)
