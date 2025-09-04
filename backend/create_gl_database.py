import os
import sys
import logging
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import all models to ensure they are registered with SQLAlchemy
from app.models.base import Base
from app.models.gl_models import *
from app.models.gl_account import *
from app.models.gl_period import *
from app.models.gl_recurring_models import *

def get_database_url():
    """Get the database URL from environment or use default SQLite."""
    return os.getenv("DATABASE_URL", f"sqlite:///{project_root}/paksa_financial.db")

def create_database_engine():
    """Create and return a database engine with appropriate settings."""
    db_url = get_database_url()
    logger.info(f"Connecting to database: {db_url}")
    
    # SQLite specific settings
    connect_args = {}
    if "sqlite" in db_url:
        connect_args = {"check_same_thread": False}
        
    return create_engine(
        db_url,
        connect_args=connect_args,
        echo=True  # Enable SQL query logging
    )

def check_database_connection(engine):
    """Verify database connection is working."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

def create_tables(engine):
    """Create all database tables."""
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        return False

def verify_tables(engine):
    """Verify that tables were created successfully."""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    if not tables:
        logger.warning("No tables found in the database")
        return False
        
    logger.info("\n=== Database Tables ===")
    for table in tables:
        logger.info(f"\nTable: {table}")
        logger.info("Columns:")
        for column in inspector.get_columns(table):
            logger.info(f"  - {column['name']}: {column['type']}")
    
    return True

def main():
    """Main function to set up the database."""
    try:
        # Create engine
        engine = create_database_engine()
        
        # Check connection
        if not check_database_connection(engine):
            return False
            
        # Create tables
        if not create_tables(engine):
            return False
            
        # Verify tables
        if not verify_tables(engine):
            return False
            
        logger.info("\n✅ Database setup completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"An error occurred during database setup: {e}", exc_info=True)
        return False
    finally:
        if 'engine' in locals():
            engine.dispose()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
