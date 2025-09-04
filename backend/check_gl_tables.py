from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./paksa_financial.db")

# Create a synchronous engine for table inspection
sync_engine = create_engine(DATABASE_URL.replace("aiosqlite", "sqlite"))

# Create a session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)
session = SessionLocal()

# Get table information
inspector = inspect(sync_engine)
tables = inspector.get_table_names()

print("\n=== Database Tables ===")
for table in tables:
    print(f"\nTable: {table}")
    print("Columns:")
    for column in inspector.get_columns(table):
        print(f"  - {column['name']}: {column['type']}")
    
    # Get foreign key information
    print("\nForeign Keys:")
    for fk in inspector.get_foreign_keys(table):
        print(f"  - {fk['constrained_columns']} references {fk['referred_table']}.{fk['referred_columns']}")

session.close()
