"""
Script to run the main FastAPI application with detailed debug logging.
"""
import os
import sys
import logging
import uvicorn
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app_debug.log')
    ]
)
logger = logging.getLogger(__name__)

def load_environment():
    """Load environment variables."""
    try:
        from dotenv import load_dotenv
        env_path = Path('.') / '.env'
        if env_path.exists():
            load_dotenv(dotenv_path=env_path)
            logger.info("Loaded environment variables from .env file")
        else:
            logger.warning("No .env file found, using system environment variables")
    except ImportError:
        logger.warning("python-dotenv not installed, using system environment variables")

def check_dependencies():
    """Check if all required dependencies are installed."""
    try:
        import fastapi
        import sqlalchemy
        import pydantic
        import uvicorn
        logger.info(f"FastAPI version: {fastapi.__version__}")
        logger.info(f"SQLAlchemy version: {sqlalchemy.__version__}")
        logger.info(f"Pydantic version: {pydantic.__version__}")
        logger.info(f"Uvicorn version: {uvicorn.__version__}")
    except ImportError as e:
        logger.error(f"Missing dependency: {e}")
        sys.exit(1)

def check_database_connection():
    """Check if the database is accessible."""
    try:
        from sqlalchemy.ext.asyncio import create_async_engine
        from app.core.config import settings
        
        logger.info(f"Testing database connection to: {settings.SQLALCHEMY_DATABASE_URI}")
        
        # Create a test engine
        test_engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI)
        
        # Test the connection
        import asyncio
        
        async def test_conn():
            async with test_engine.connect() as conn:
                result = await conn.execute("SELECT 1")
                return result.scalar()
        
        result = asyncio.run(test_conn())
        logger.info(f"Database connection test successful: {result == 1}")
        
    except Exception as e:
        logger.error(f"Database connection error: {e}", exc_info=True)
        sys.exit(1)

def run_server():
    """Run the FastAPI server with detailed logging."""
    try:
        # Set environment variables
        os.environ.setdefault("ENV", "development")
        os.environ.setdefault("DEBUG", "True")
        os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./paksa_finance.db")
        
        # Load environment
        load_environment()
        
        # Check dependencies
        check_dependencies()
        
        # Check database connection
        check_database_connection()
        
        # Import the FastAPI app
        logger.info("Importing FastAPI application...")
        from main import app
        
        # Run the server
        logger.info("Starting FastAPI server...")
        logger.info("Access the API at: http://127.0.0.1:8000/")
        logger.info("API documentation at: http://127.0.0.1:8000/api/docs")
        
        uvicorn.run(
            "main:app",
            host="127.0.0.1",
            port=8000,
            reload=True,
            log_level="debug",
            log_config=None,
            workers=1
        )
        
    except ImportError as e:
        logger.error(f"Error importing application: {e}", exc_info=True)
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error running server: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    run_server()
