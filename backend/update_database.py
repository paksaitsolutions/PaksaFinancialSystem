"""
Safely update the existing database by adding missing tables and columns.
This script will not drop any existing tables or data.
"""
import os
import sys
from sqlalchemy import create_engine, inspect
from sqlalchemy.schema import CreateTable, AddConstraint

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import Base, engine, SessionLocal
from app.core.config import settings

def get_missing_tables():
    """Get a list of tables that exist in the models but not in the database."""
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    
    # Import all models to ensure they are registered with SQLAlchemy
    from app.models import (
        user, department, employee, attendance, leave, 
        payroll_processing, payslip, tax, company_settings
    )
    
    model_tables = set(Base.metadata.tables.keys())
    return model_tables - existing_tables

def get_missing_columns(table_name):
    """Get a list of columns that exist in the model but not in the database table."""
    inspector = inspect(engine)
    existing_columns = {col['name'] for col in inspector.get_columns(table_name)}
    
    model_columns = set(Base.metadata.tables[table_name].columns.keys())
    return model_columns - existing_columns

def update_database():
    """Update the database by adding missing tables and columns."""
    print("🔍 Checking database for updates...")
    
    # Get database connection
    connection = engine.connect()
    transaction = connection.begin()
    
    try:
        # Check for missing tables
        missing_tables = get_missing_tables()
        
        if missing_tables:
            print(f"\n➕ Found {len(missing_tables)} missing tables:")
            for table in sorted(missing_tables):
                print(f"  - {table}")
                
                # Create the missing table
                table_obj = Base.metadata.tables[table]
                create_table_sql = str(CreateTable(table_obj).compile(engine))
                connection.execute(create_table_sql)
                
                # Add any constraints
                for constraint in table_obj.constraints:
                    add_constraint_sql = str(AddConstraint(constraint).compile(engine))
                    connection.execute(add_constraint_sql)
        
        # Check for missing columns in existing tables
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        for table in existing_tables:
            if table not in Base.metadata.tables:
                continue
                
            missing_columns = get_missing_columns(table)
            if missing_columns:
                print(f"\n➕ Found {len(missing_columns)} missing columns in table '{table}':")
                for column in sorted(missing_columns):
                    print(f"  - {column}")
                    
                    # Get the column definition from the model
                    column_obj = Base.metadata.tables[table].columns[column]
                    column_type = column_obj.type.compile(engine.dialect)
                    
                    # Add the column with ALTER TABLE
                    alter_sql = f"ALTER TABLE {table} ADD COLUMN {column} {column_type}"
                    
                    # Add NULL/NOT NULL constraint if specified
                    if not column_obj.nullable:
                        alter_sql += " NOT NULL"
                    
                    # Add DEFAULT if specified
                    if column_obj.default is not None:
                        default_value = column_obj.default.arg
                        if isinstance(default_value, str):
                            default_value = f"'{default_value}'"
                        alter_sql += f" DEFAULT {default_value}"
                    
                    connection.execute(alter_sql)
        
        transaction.commit()
        print("\n✅ Database update completed successfully!")
        
    except Exception as e:
        transaction.rollback()
        print(f"\n❌ Error updating database: {str(e)}")
        return False
    finally:
        connection.close()
    
    return True

if __name__ == "__main__":
    if not os.path.exists("paksa_finance.db"):
        print("❌ Database file 'paksa_finance.db' not found!")
        sys.exit(1)
    
    print("🔧 Starting database update process...")
    if update_database():
        print("\n✨ Database is now up to date!")
    else:
        print("\n❌ Failed to update database. Please check the error messages above.")
        sys.exit(1)
