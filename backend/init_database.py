"""
Database initialization and verification script.
This script initializes the database and verifies its state with enhanced error handling.
"""
import asyncio
import logging
import os
import sys
import traceback
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to the Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# Set up logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.DEBUG,  # More detailed logging
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/db_init.log', mode='w')
    ]
)
logger = logging.getLogger(__name__)

# Configure SQLAlchemy logging
sqlalchemy_logger = logging.getLogger('sqlalchemy.engine')
sqlalchemy_logger.setLevel(logging.INFO)
sqlalchemy_logger.addHandler(logging.FileHandler('logs/sqlalchemy.log', mode='w'))

# Load environment variables
load_dotenv()

async def check_database_connection():
    """Check if we can connect to the database with detailed error reporting."""
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy import text
    import sqlalchemy as sa
    
    try:
        # Load environment variables explicitly
        load_dotenv(override=True)
        
        db_engine = os.getenv('DB_ENGINE', 'sqlite').lower()
        logger.info(f"Using database engine: {db_engine}")
        
        if db_engine == 'sqlite':
            db_path = os.path.abspath(os.getenv('SQLITE_DB_PATH', './instance/paksa_finance.db'))
            db_url = f'sqlite+aiosqlite:///{db_path}'
            # Ensure the instance directory exists and is writable
            db_dir = os.path.dirname(db_path)
            os.makedirs(db_dir, exist_ok=True)
            logger.info(f"SQLite database path: {db_path}")
            logger.info(f"Database directory exists: {os.path.exists(db_dir)}")
            logger.info(f"Database file exists: {os.path.exists(db_path)}")
            
            # Verify directory is writable
            test_file = os.path.join(db_dir, 'test_write.tmp')
            try:
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
                logger.info("✅ Directory is writable")
            except Exception as e:
                logger.error(f"❌ Directory is not writable: {str(e)}")
                return False
        else:
            # PostgreSQL configuration
            db_url = f"postgresql+asyncpg://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT', '5432')}/{os.getenv('POSTGRES_DB')}"
            logger.info(f"PostgreSQL connection URL: {db_url.replace(os.getenv('POSTGRES_PASSWORD', ''), '***')}")
        
        logger.info(f"Database URL: {db_url}")
        
        # Create engine with detailed logging
        engine = create_async_engine(
            db_url,
            echo=True,
            connect_args={"check_same_thread": False} if db_engine == 'sqlite' else {}
        )
        
        # Test connection
        logger.info("Attempting to connect to the database...")
        async with engine.connect() as conn:
            logger.info("✅ Successfully connected to the database")
            
            # Get database version/info
            if db_engine == 'sqlite':
                result = await conn.execute(text("SELECT sqlite_version()"))
                version = result.scalar()
                logger.info(f"SQLite version: {version}")
            else:
                result = await conn.execute(text("SELECT version()"))
                version = result.scalar()
                logger.info(f"PostgreSQL version: {version}")
            
            # List all tables (if any exist)
            if db_engine == 'sqlite':
                result = await conn.execute(
                    text("SELECT name FROM sqlite_master WHERE type='table'")
                )
            else:
                result = await conn.execute(
                    text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
                )
            
            tables = [row[0] for row in result.all()]
            logger.info(f"Found {len(tables)} tables in the database")
            if tables:
                logger.info("Tables: " + ", ".join(tables))
            
            return True
            
    except ImportError as e:
        logger.error(f"❌ Import error: {str(e)}")
        logger.error("Make sure all required packages are installed (sqlalchemy, aiosqlite, asyncpg, etc.)")
        return False
    except sa.exc.SQLAlchemyError as e:
        logger.error(f"❌ SQLAlchemy error: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error("Traceback:" + "\n".join(traceback.format_exc().splitlines()[-5:]))
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error("Traceback:" + "\n".join(traceback.format_exc().splitlines()[-5:]))
        return False
    finally:
        try:
            if 'engine' in locals():
                await engine.dispose()
                logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error disposing engine: {str(e)}")

async def initialize_database():
    """Initialize the database by creating all tables with detailed error reporting."""
    try:
        # Import inside function to avoid circular imports
        from app.db.base import Base, engine, get_db_url
        from sqlalchemy import inspect
        import sqlalchemy as sa
        
        logger.info("Starting database initialization...")
        
        # Get database URL for logging
        db_url = get_db_url()
        logger.info(f"Using database URL: {db_url}")
        
        # Create all tables
        async with engine.begin() as conn:
            logger.info("Database connection established")
            
            # Check if tables already exist
            inspector = await conn.run_sync(
                lambda sync_conn: inspect(sync_conn.engine)
            )
            
            existing_tables = await conn.run_sync(
                lambda sync_conn: inspector.get_table_names()
            )
            
            if existing_tables:
                logger.info(f"Found {len(existing_tables)} existing tables:")
                for i, table in enumerate(existing_tables, 1):
                    logger.info(f"  {i}. {table}")
            else:
                logger.info("No existing tables found in the database")
            
            # Create all tables
            logger.info("Creating database tables...")
            try:
                await conn.run_sync(Base.metadata.create_all)
                logger.info("✅ Database tables created successfully")
                
                # Verify tables were created
                updated_tables = await conn.run_sync(
                    lambda sync_conn: inspector.get_table_names()
                )
                
                if updated_tables:
                    logger.info(f"Total tables after creation: {len(updated_tables)}")
                    if len(updated_tables) > 0:
                        logger.info("First 5 tables: " + ", ".join(updated_tables[:5]))
                        if len(updated_tables) > 5:
                            logger.info(f"... and {len(updated_tables) - 5} more")
                
                return True
                
            except sa.exc.SQLAlchemyError as e:
                logger.error(f"❌ Error creating tables: {str(e)}")
                logger.error(f"Error type: {type(e).__name__}")
                logger.error("Traceback:" + "\n".join(traceback.format_exc().splitlines()[-5:]))
                return False
                
    except ImportError as e:
        logger.error(f"❌ Import error: {str(e)}")
        logger.error("Make sure all required packages are installed")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error during initialization: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error("Traceback:" + "\n".join(traceback.format_exc().splitlines()[-5:]))
        return False

async def create_admin_user():
    """Create an admin user if one doesn't exist."""
    try:
        from app.db.session import AsyncSessionLocal
        from app.modules.auth.models import User
        from app.core.security import get_password_hash
        
        logger.info("Checking for admin user...")
        
        async with AsyncSessionLocal() as db:
            # Check if admin user exists
            result = await db.execute(
                sa.select(User).where(User.email == "admin@example.com")
            )
            admin = result.scalar_one_or_none()
            
            if admin:
                logger.info("✅ Admin user already exists")
                return True
                
            # Create admin user
            admin = User(
                email="admin@example.com",
                hashed_password=get_password_hash("admin"),
                full_name="Admin User",
                is_superuser=True,
                is_active=True
            )
            
            db.add(admin)
            await db.commit()
            logger.info("✅ Created admin user (email: admin@example.com, password: admin)")
            return True
            
    except Exception as e:
        logger.error(f"❌ Error creating admin user: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        return False

async def main():
    """Main function to run database initialization."""
    # Ensure logs directory exists
    os.makedirs('logs', exist_ok=True)
    
    logger.info("=" * 80)
    logger.info("Paksa Financial System - Database Initialization")
    logger.info("=" * 80)
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Working directory: {os.getcwd()}")
    
    try:
        # Check database connection
        logger.info("\n" + "-" * 40)
        logger.info("STEP 1: Testing database connection...")
        if not await check_database_connection():
            logger.error("❌ Database connection check failed. Exiting.")
            return 1
            
        # Initialize database
        logger.info("\n" + "-" * 40)
        logger.info("STEP 2: Initializing database tables...")
        if not await initialize_database():
            logger.error("❌ Database initialization failed. Check logs for details.")
            return 1
        
        # Create admin user
        logger.info("\n" + "-" * 40)
        logger.info("STEP 3: Setting up admin user...")
        await create_admin_user()
        
        logger.info("\n" + "=" * 80)
        logger.info("✅ DATABASE INITIALIZATION COMPLETED SUCCESSFULLY!")
        logger.info("=" * 80)
        logger.info("\nNEXT STEPS:")
        logger.info("1. Start the backend server with: uvicorn app.main:app --reload")
        logger.info("2. Access the admin interface at: http://localhost:8000/admin")
        logger.info("3. Log in with: admin@example.com / admin")
        logger.info("\nCheck the logs/ directory for detailed logs.")
        
        return 0
        
    except Exception as e:
        logger.error("\n" + "!" * 80)
        logger.error("❌ CRITICAL ERROR DURING INITIALIZATION")
        logger.error("!" * 80)
        logger.error(f"Error: {str(e)}")
        logger.error(f"Type: {type(e).__name__}")
        logger.error("Traceback:")
        logger.error(traceback.format_exc())
        return 1
    return True

if __name__ == "__main__":
    # Run the main function and exit with appropriate status code
    exit_code = asyncio.run(main())
    
    # On Windows, ensure we see the output before the window closes
    if os.name == 'nt':
        input("\nPress Enter to exit...")
    
    sys.exit(exit_code)
