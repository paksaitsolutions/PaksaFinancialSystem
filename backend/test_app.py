"""
Test FastAPI application to verify basic functionality.
"""
import logging
import sys
from fastapi import FastAPI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Create FastAPI instance
app = FastAPI(title="Paksa Financial System - Test App")

# Simple health check endpoint
@app.get("/")
async def read_root():
    logger.info("Root endpoint accessed")
    return {
        "message": "Hello, Paksa Financial System!",
        "status": "running",
        "version": "1.0.0"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    
    # Log startup information
    logger.info("=" * 50)
    logger.info("Starting Paksa Financial System - Test App")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Running on http://0.0.0.0:8000")
    logger.info("=" * 50)
    
    try:
        # Run the FastAPI application
        uvicorn.run(
            "test_app:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        sys.exit(1)
