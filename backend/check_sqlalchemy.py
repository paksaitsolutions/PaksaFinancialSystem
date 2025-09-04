"""
Check SQLAlchemy database connection and configuration.
"""
import os
import sys
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings

def check_database():
    """Check database connection and list tables."""
    print("=== SQLAlchemy Database Check ===\n")
    
    # Print database URL
    print(f"Database URL: {settings.DATABASE_URL}")
    
    # Create engine with echo=True to see SQL statements
    try:
        engine = create_engine(
            settings.DATABASE_URL,
            connect_args={"check_same_thread": False},  # SQLite specific
            echo=True
        )
        
        # Test connection
        print("\n🔌 Testing database connection...")
        with engine.connect() as conn:
            print("✅ Successfully connected to the database!")
            
            # Check if the database file exists
            db_path = settings.DATABASE_URL.replace("sqlite:///", "")
            if os.path.exists(db_path):
                print(f"\n📂 Database file exists at: {os.path.abspath(db_path)}")
                print(f"📊 File size: {os.path.getsize(db_path)} bytes")
            else:
                print("\n❌ Database file does not exist!")
                return False
            
            # List tables
            print("\n📋 Checking for tables...")
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            if not tables:
                print("❌ No tables found in the database!")
            else:
                print(f"✅ Found {len(tables)} tables:")
                for table in tables:
                    print(f"- {table}")
                    
                    # List columns for each table
                    columns = inspector.get_columns(table)
                    print(f"  Columns: {', '.join([col['name'] for col in columns])}")
            
            return True
            
    except Exception as e:
        print(f"\n❌ Error connecting to database: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    check_database()
