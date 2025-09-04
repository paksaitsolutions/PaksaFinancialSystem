import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import all models to ensure they are registered with SQLAlchemy
from app.models.gl_models import Base as GLBase
from app.models.gl_account import GLAccount
from app.models.gl_period import *
from app.models.gl_recurring_models import *

# Load environment variables
load_dotenv()

# Database URL - using aiosqlite for async operations
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./paksa_financial.db")

# Create a synchronous engine for table creation
sync_engine = create_engine(
    DATABASE_URL.replace("aiosqlite", "sqlite"),
    connect_args={"check_same_thread": False}
)

def create_tables():
    print("Creating GL database tables...")
    try:
        # Create all tables
        GLBase.metadata.create_all(bind=sync_engine)
        print("Successfully created GL tables!")
        
        # Verify tables were created
        inspector = inspect(sync_engine)
        tables = inspector.get_table_names()
        print("\nTables created:")
        for table in tables:
            print(f"- {table}")
            
    except Exception as e:
        print(f"Error creating tables: {e}")
        raise

if __name__ == "__main__":
    from sqlalchemy import inspect
    create_tables()
