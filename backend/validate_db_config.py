"""
Database configuration validation script.
This script validates that all required database configuration is properly set.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Set up logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def load_environment() -> bool:
    """Load and validate environment variables."""
    # Load environment variables from the .env file in the project root
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        logger.info(f"Loading environment variables from: {env_path}")
        load_dotenv(env_path, override=True)
    else:
        logger.error(f"Error: .env file not found at {env_path}")
        return False
    
    return True

def validate_database_config() -> bool:
    """Validate database configuration."""
    logger.info("Validating database configuration...")
    
    # Required environment variables
    required_vars = [
        'DB_ENGINE',
        'POSTGRES_DB' if os.getenv('DB_ENGINE') == 'postgresql' else 'SQLITE_DB_PATH',
    ]
    
    # For PostgreSQL, check additional required variables
    if os.getenv('DB_ENGINE') == 'postgresql':
        required_vars.extend([
            'POSTGRES_USER',
            'POSTGRES_PASSWORD',
            'POSTGRES_HOST',
            'POSTGRES_PORT',
        ])
    
    # Check for missing required variables
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    # Log current configuration (without sensitive data)
    db_engine = os.getenv('DB_ENGINE', 'sqlite')
    logger.info(f"Database Engine: {db_engine}")
    
    if db_engine == 'postgresql':
        logger.info(f"PostgreSQL Database: {os.getenv('POSTGRES_DB')}")
        logger.info(f"PostgreSQL Host: {os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}")
        logger.info(f"PostgreSQL User: {os.getenv('POSTGRES_USER')}")
    else:
        db_path = os.getenv('SQLITE_DB_PATH', './instance/paksa_finance.db')
        logger.info(f"SQLite Database Path: {db_path}")
        
        # Check if SQLite database file exists
        if Path(db_path).exists():
            logger.info("SQLite database file exists.")
            try:
                import sqlite3
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                logger.info(f"Found {len(tables)} tables in the database.")
                conn.close()
            except Exception as e:
                logger.error(f"Error checking SQLite database: {str(e)}")
                return False
        else:
            logger.warning("SQLite database file does not exist. It will be created on first run.")
    
    logger.info("Database configuration is valid.")
    return True

def main() -> int:
    """Main function."""
    if not load_environment():
        return 1
    
    if not validate_database_config():
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
