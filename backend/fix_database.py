"""
Script to fix database connection issues by ensuring the correct database file is used.
"""
import os
import sys
import shutil
from sqlalchemy import create_engine, inspect

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings

def check_database_files():
    """Check for existing database files and their status."""
    db_files = [
        "paksa_finance.db",
        "paksa_financial.db",
        "paksa_finance_new.db",
        "paksa_financial_new.db"
    ]
    
    print("🔍 Checking for existing database files:")
    found_files = []
    for db_file in db_files:
        if os.path.exists(db_file):
            size = os.path.getsize(db_file)
            found_files.append((db_file, size))
    
    if not found_files:
        print("❌ No database files found!")
        return []
    
    for file, size in found_files:
        print(f"✅ Found: {file} ({size} bytes)")
    
    return [f[0] for f in found_files]

def create_new_database():
    """Create a new database with the correct name."""
    target_db = "paksa_financial.db"  # This matches settings.py
    
    print(f"\n🔄 Creating new database: {target_db}")
    
    # Remove existing file if it exists
    if os.path.exists(target_db):
        try:
            os.remove(target_db)
            print(f"🗑️  Removed existing {target_db}")
        except Exception as e:
            print(f"❌ Error removing {target_db}: {str(e)}")
            return False
    
    # Create a new SQLite database
    try:
        engine = create_engine(f"sqlite:///{target_db}")
        with engine.connect() as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS version (version INTEGER);")
            conn.execute("INSERT INTO version (version) VALUES (1);")
        print(f"✅ Successfully created {target_db}")
        return True
    except Exception as e:
        print(f"❌ Error creating database: {str(e)}")
        return False

def main():
    print("=== Database Fix Tool ===\n")
    
    # Check for existing database files
    found_files = check_database_files()
    
    if not found_files:
        print("\nNo database files found. Creating a new one...")
        if create_new_database():
            print("\n✅ Database setup complete!")
            print("You can now run the application with the new database.")
        else:
            print("\n❌ Failed to create database. Please check the error messages above.")
        return
    
    # If we found database files
    print("\nTo fix the database connection, we recommend:")
    print("1. Backing up any existing database files")
    print("2. Creating a new database with the correct name (paksa_financial.db)")
    print("3. Running database migrations")
    
    # Check if the correct database file exists
    if "paksa_financial.db" not in found_files:
        print("\n⚠️  The correct database file (paksa_financial.db) was not found!")
        create_new = input("Would you like to create it now? (y/n): ")
        if create_new.lower() == 'y':
            if create_new_database():
                print("\n✅ Database setup complete!")
                print("You can now run the application with the new database.")
            else:
                print("\n❌ Failed to create database. Please check the error messages above.")
    else:
        print("\n✅ The correct database file (paksa_financial.db) was found!")
        print("You may need to run database migrations if the tables are missing.")

if __name__ == "__main__":
    main()
