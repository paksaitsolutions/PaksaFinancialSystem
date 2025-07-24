"""
Minimal test script to verify database connection and settings loading.
"""
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# Set environment variables before importing settings
os.environ["ENVIRONMENT"] = "development"
os.environ["DB_ENGINE"] = "sqlite"
os.environ["SQLITE_DB_PATH"] = str(project_root / "instance" / "paksa_finance.db")
os.environ["DATABASE_URI"] = f"sqlite+aiosqlite:///{project_root}/instance/paksa_finance.db"

# Ensure the instance directory exists
(project_root / "instance").mkdir(exist_ok=True)

print("=== Environment Variables ===")
print(f"ENVIRONMENT: {os.getenv('ENVIRONMENT')}")
print(f"DB_ENGINE: {os.getenv('DB_ENGINE')}")
print(f"SQLITE_DB_PATH: {os.getenv('SQLITE_DB_PATH')}")
print(f"DATABASE_URI: {os.getenv('DATABASE_URI')}")

print("\n=== Testing Settings Import ===")
try:
    from app.core.config import settings
    print("✅ Successfully imported settings!")
    print(f"Database URI from settings: {settings.DATABASE_URI}")
except Exception as e:
    print(f"❌ Error importing settings: {str(e)}")
    print(f"Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()

print("\n=== Testing Database Connection ===")
try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # Use the DATABASE_URI from environment or settings
    db_uri = os.getenv("DATABASE_URI") or str(settings.DATABASE_URI)
    print(f"Using database URI: {db_uri}")
    
    # Create engine and test connection
    engine = create_engine(db_uri)
    with engine.connect() as conn:
        print("✅ Successfully connected to the database!")
        print(f"Database version: {conn.dialect.server_version_info}")
    
except Exception as e:
    print(f"❌ Error connecting to database: {str(e)}")
    print(f"Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
