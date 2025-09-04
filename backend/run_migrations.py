import os
import sys
from alembic.config import Config
from alembic import command
from pathlib import Path

def run_migrations():
    print("Running database migrations...")
    
    # Set up paths
    base_dir = Path(__file__).parent
    alembic_ini_path = base_dir / "alembic.ini"
    alembic_dir = base_dir / "alembic"
    
    # Check if alembic.ini exists
    if not alembic_ini_path.exists():
        print("Error: alembic.ini not found!")
        return False
    
    # Configure Alembic
    config = Config(alembic_ini_path)
    config.set_main_option('script_location', str(alembic_dir))
    
    try:
        # Get current revision
        print("\nCurrent database revision:")
        command.current(config)
        
        # Show available migrations
        print("\nAvailable migrations:")
        command.history(config, indicate_current=True)
        
        # Run migrations
        print("\nRunning migrations...")
        command.upgrade(config, "head")
        
        print("\nMigration completed successfully!")
        return True
        
    except Exception as e:
        print(f"\nError running migrations: {e}")
        return False

def verify_database():
    print("\nVerifying database structure...")
    try:
        import sqlite3
        from sqlalchemy import create_engine, inspect
        
        db_path = "paksa_financial.db"
        if not os.path.exists(db_path):
            print(f"Database file not found: {db_path}")
            return False
            
        # Connect using SQLAlchemy
        engine = create_engine(f"sqlite:///{db_path}")
        inspector = inspect(engine)
        
        # Get list of tables
        tables = inspector.get_table_names()
        
        if not tables:
            print("No tables found in the database.")
            return False
            
        print("\n=== Database Structure ===")
        for table_name in sorted(tables):
            print(f"\nTable: {table_name}")
            print("-" * (len(table_name) + 8))
            
            # Get columns
            columns = inspector.get_columns(table_name)
            for col in columns:
                print(f"  {col['name']}: {col['type']} "
                      f"{'PRIMARY KEY' if col.get('primary_key') else ''} "
                      f"{'NULL' if col['nullable'] else 'NOT NULL'}")
            
            # Get row count
            with engine.connect() as conn:
                result = conn.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = result.scalar()
                print(f"  Rows: {count}")
                
        return True
        
    except Exception as e:
        print(f"Error verifying database: {e}")
        return False

if __name__ == "__main__":
    print("=== Paksa Financial System - Database Setup ===\n")
    
    # Run migrations
    if not run_migrations():
        print("\nFailed to run migrations.")
        sys.exit(1)
    
    # Verify database structure
    if not verify_database():
        print("\nDatabase verification failed.")
        sys.exit(1)
    
    print("\nDatabase setup completed successfully!")
