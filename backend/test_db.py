"""
Test database connection and configuration.
"""
import asyncio
import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# Set up basic logging with file output
log_dir = Path(__file__).parent / 'logs'
log_dir.mkdir(exist_ok=True)
log_file = log_dir / 'test_db.log'

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_file, mode='w')
    ]
)
logger = logging.getLogger(__name__)
logger.info(f"Logging to file: {log_file.absolute()}")

def load_environment():
    """Load and validate environment variables."""
    # Load environment variables from the .env file in the project root
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        logger.info(f"Loading environment variables from: {env_path}")
        load_dotenv(env_path, override=True)
    else:
        logger.warning(f"No .env file found at {env_path}. Using system environment variables.")
    
    # Set default DB_ENGINE if not set
    if not os.getenv("DB_ENGINE"):
        os.environ["DB_ENGINE"] = "postgresql"
        logger.info("DB_ENGINE not set, defaulting to 'postgresql'")
    
    # Log environment variables (be careful with sensitive data in production)
    logger.info("Environment variables loaded:")
    env_vars_to_log = [
        "DB_ENGINE", 
        "POSTGRES_USER", 
        "POSTGRES_SERVER", 
        "POSTGRES_PORT", 
        "POSTGRES_DB",
        "DATABASE_URI"
    ]
    
    for var in env_vars_to_log:
        value = os.getenv(var)
        if value is None:
            logger.warning(f"  {var}: Not set")
        elif any(sensitive in var.upper() for sensitive in ['PASS', 'SECRET', 'KEY', 'TOKEN', 'PASSWORD']):
            logger.info(f"  {var}: {'*' * 8 if value else 'Not set'}")
        else:
            logger.info(f"  {var}: {value}")

# Load environment variables
load_environment()

def get_database_config():
    """Get database configuration from environment variables."""
    # Default to PostgreSQL since that's what's configured in .env
    DB_ENGINE = os.getenv("DB_ENGINE", "postgresql").lower()
    
    if DB_ENGINE not in ["sqlite", "postgresql"]:
        raise ValueError(f"Unsupported database engine: {DB_ENGINE}. Supported engines: sqlite, postgresql")
    
    if DB_ENGINE == "sqlite":
        # SQLite configuration
        DB_PATH = os.getenv("SQLITE_DB_PATH", "./instance/paksa_finance.db")
        
        # Convert to absolute path
        DB_PATH = os.path.abspath(DB_PATH)
        DB_DIR = os.path.dirname(DB_PATH)
        
        # Ensure the directory exists
        try:
            os.makedirs(DB_DIR, exist_ok=True)
            logger.info(f"SQLite database directory: {DB_DIR}")
        except Exception as e:
            logger.error(f"Failed to create database directory {DB_DIR}: {e}")
            raise
        
        DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"
        logger.info(f"Using SQLite database at: {DB_PATH}")
        
    else:  # PostgreSQL
        # Use the environment variables from .env
        DB_USER = os.getenv("POSTGRES_USER")
        DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
        DB_HOST = os.getenv("POSTGRES_SERVER")  # Note: Using POSTGRES_SERVER instead of POSTGRES_HOST
        DB_PORT = os.getenv("POSTGRES_PORT")
        DB_NAME = os.getenv("POSTGRES_DB")
        
        # Log the PostgreSQL configuration
        logger.info("PostgreSQL Configuration:")
        logger.info(f"  User: {DB_USER}")
        logger.info(f"  Host: {DB_HOST}")
        logger.info(f"  Port: {DB_PORT}")
        logger.info(f"  Database: {DB_NAME}")
        
        # Validate PostgreSQL connection parameters
        if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
            missing = []
            if not DB_USER: missing.append("POSTGRES_USER")
            if not DB_PASSWORD: missing.append("POSTGRES_PASSWORD")
            if not DB_HOST: missing.append("POSTGRES_SERVER")
            if not DB_PORT: missing.append("POSTGRES_PORT")
            if not DB_NAME: missing.append("POSTGRES_DB")
            error_msg = f"Missing required PostgreSQL configuration: {', '.join(missing)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Escape special characters in password
        from urllib.parse import quote_plus
        safe_password = quote_plus(DB_PASSWORD)
        
        # Construct the DATABASE_URL
        DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{safe_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        logger.info(f"Using PostgreSQL database at: {DB_HOST}:{DB_PORT}/{DB_NAME}")
    
    # Check if DATABASE_URI is set in environment and use it if available
    if os.getenv("DATABASE_URI"):
        DATABASE_URL = os.getenv("DATABASE_URI")
        logger.info(f"Using DATABASE_URI from environment: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL}")
    
    return {
        "DB_ENGINE": DB_ENGINE,
        "DATABASE_URL": DATABASE_URL,
        "DB_PATH": DB_PATH if DB_ENGINE == "sqlite" else None
    }

# Get database configuration
try:
    db_config = get_database_config()
    DB_ENGINE = db_config["DB_ENGINE"]
    DATABASE_URL = db_config["DATABASE_URL"]
    if DB_ENGINE == "sqlite":
        DB_PATH = db_config["DB_PATH"]
except Exception as e:
    logger.error(f"Failed to configure database: {e}")
    raise

def create_database_engine():
    """Create and configure the async database engine."""
    from sqlalchemy.pool import NullPool, QueuePool
    
    # Common engine options
    engine_options = {
        "echo": True,  # Enable SQL query logging
        "future": True,
        "pool_pre_ping": True,  # Enable connection health checks
    }
    
    # Engine-specific options
    if DB_ENGINE == "sqlite":
        # SQLite specific configuration
        engine_options.update({
            "poolclass": NullPool,  # Use NullPool for SQLite in async mode
            "connect_args": {
                "check_same_thread": False,  # Required for SQLite in async mode
                "timeout": 30,  # 30 second timeout
            },
        })
    else:  # PostgreSQL
        engine_options.update({
            "pool_size": 5,
            "max_overflow": 10,
            "pool_timeout": 30,  # 30 seconds
            "pool_recycle": 300,  # Recycle connections after 5 minutes
        })
    
    logger.info(f"Creating {DB_ENGINE} database engine...")
    try:
        engine = create_async_engine(DATABASE_URL, **engine_options)
        logger.info("Database engine created successfully")
        return engine
    except Exception as e:
        logger.error(f"Failed to create database engine: {e}")
        raise

# Create async engine
try:
    engine = create_database_engine()
except Exception as e:
    logger.critical(f"Failed to initialize database engine: {e}")
    raise

def create_session_factory():
    """Create and configure the async session factory."""
    logger.info("Creating async session factory...")
    try:
        session_factory = sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False
        )
        logger.info("Session factory created successfully")
        return session_factory
    except Exception as e:
        logger.error(f"Failed to create session factory: {e}")
        raise

# Create async session factory
try:
    AsyncSessionLocal = create_session_factory()
except Exception as e:
    logger.critical(f"Failed to initialize session factory: {e}")
    raise

async def test_connection():
    """Test database connection and print database info."""
    logger.info("=" * 50)
    logger.info("Testing database connection...")
    logger.info(f"Using database engine: {DB_ENGINE}")
    logger.info(f"Database URL: {DATABASE_URL}")
    
    # Verify the database file exists for SQLite
    if DB_ENGINE == "sqlite":
        db_path = Path(DB_PATH)
        logger.info(f"SQLite database path: {db_path.absolute()}")
        if db_path.exists():
            logger.info(f"Database file exists. Size: {db_path.stat().st_size / 1024:.2f} KB")
        else:
            logger.warning("Database file does not exist. It will be created on first connection.")
            # Ensure the directory exists
            db_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Test the engine connection
        logger.info("Testing database engine connection...")
        async with engine.connect() as conn:
            logger.info("✅ Successfully connected to the database")
            
            # Test a simple query
            result = await conn.execute(text("SELECT 1"))
            value = result.scalar()
            logger.info(f"✅ Simple query test successful. Result: {value}")
            
            # Get database version
            if DB_ENGINE == "postgresql":
                result = await conn.execute(text("SELECT version()"))
                version = result.scalar()
                logger.info(f"Database version: {version}")
            else:  # SQLite
                result = await conn.execute(text("SELECT sqlite_version()"))
                version = result.scalar()
                logger.info(f"SQLite version: {version}")
                
            # List all tables (if any exist)
            if DB_ENGINE == "postgresql":
                result = await conn.execute(
                    text("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public'
                    """)
                )
            else:  # SQLite
                result = await conn.execute(
                    text("SELECT name FROM sqlite_master WHERE type='table'")
                )
                
            tables = [row[0] for row in result.fetchall() if row[0] != 'sqlite_sequence']
            logger.info(f"Found {len(tables)} tables: {', '.join(tables) if tables else 'None'}")
            
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(test_connection())
