"""
Debug script to start the FastAPI server with detailed logging.
"""
import uvicorn
import sys
import os
import logging
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = str(Path(__file__).parent.absolute())
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Start the FastAPI server with debug configuration."""
    try:
        logger.info("Starting FastAPI server with debug configuration...")
        logger.info(f"Working directory: {os.getcwd()}")
        logger.info(f"Python path: {sys.path}")
        
        # Try to import the FastAPI app
        try:
            # Import the app directly from the module
            from app.main import app
            logger.info("Successfully imported FastAPI app from app.main")
            
            # Start the server using the imported app directly
            uvicorn.run(
                app,
                host="0.0.0.0",
                port=8000,
                reload=True,
                log_level="debug",
                access_log=True
            )
            
        except ImportError as e:
            logger.error(f"Failed to import FastAPI app: {e}", exc_info=True)
            logger.info("Trying alternative import approach...")
            
            # Fallback to running with module string
            uvicorn.run(
                "app.main:app",
                host="0.0.0.0",
                port=8000,
                reload=True,
                log_level="debug",
                access_log=True,
                reload_dirs=["app"]
            )
            
    except Exception as e:
        logger.error(f"Error starting server: {e}", exc_info=True)
        return 1
    except Exception as e:
        logger.error(f"Error starting server: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
