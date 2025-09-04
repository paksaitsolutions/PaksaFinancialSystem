import os
import sys
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

def test_connection():
    # Database URL - using the same as in settings
    db_url = "sqlite:///paksa_financial.db"
    print(f"Testing connection to: {db_url}")
    
    try:
        # Create engine
        engine = create_engine(db_url, echo=True)
        
        # Test connection
        with engine.connect() as conn:
            print("\nSuccessfully connected to the database!")
            
            # Get SQLite version
            result = conn.execute("SELECT sqlite_version()")
            print(f"SQLite version: {result.scalar()}")
            
            # Get list of tables
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            if not tables:
                print("\nNo tables found in the database.")
                return
                
            print("\n=== Tables in the database ===")
            for table_name in tables:
                print(f"\nTable: {table_name}")
                print("-" * (len(table_name) + 8))
                
                # Get columns
                columns = inspector.get_columns(table_name)
                print("  Columns:")
                for col in columns:
                    print(f"    {col['name']} ({col['type']})")
                
                # Get row count
                with engine.connect() as conn2:
                    result = conn2.execute(f"SELECT COUNT(*) FROM {table_name}")
                    print(f"  Rows: {result.scalar()}")
    
    except Exception as e:
        print(f"\nError: {e}")
        print("\nThis could be due to:")
        print("1. The database file doesn't exist or is corrupted")
        print("2. Insufficient permissions to access the file")
        print("3. The file is locked by another process")
        
        # Check if file exists and is accessible
        if os.path.exists('paksa_financial.db'):
            print("\nFile exists. Checking permissions...")
            try:
                with open('paksa_financial.db', 'rb') as f:
                    header = f.read(16)
                    print(f"File header: {header}")
                    if header.startswith(b'SQLite format 3\x00'):
                        print("File appears to be a valid SQLite database.")
                    else:
                        print("File does not appear to be a valid SQLite database.")
            except Exception as e:
                print(f"Error reading file: {e}")
        else:
            print("\nDatabase file does not exist.")

if __name__ == "__main__":
    print("=== SQLAlchemy Database Test ===\n")
    test_connection()
