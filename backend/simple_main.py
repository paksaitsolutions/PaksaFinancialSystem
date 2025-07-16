"""
Simple FastAPI application for debugging purposes.
This is a minimal version of the main application to help identify import issues.
"""
import logging
import sys
from fastapi import FastAPI, Depends, HTTPException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Paksa Financial System",
    description="Debugging API - Minimal Version",
    version="1.0.0"
)

# Simple endpoint to test basic functionality
@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {
        "message": "Paksa Financial System API is running",
        "status": "success",
        "version": "1.0.0"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "database": "not_connected",
        "version": "1.0.0"
    }

# Test database connection
@app.get("/test-db")
async def test_db():
    try:
        # Try to import and test database connection
        from sqlalchemy import text
        from app.db.session import SessionLocal
        
        async with SessionLocal() as db:
            result = await db.execute(text("SELECT 1"))
            await db.commit()
            row = result.scalar()
            if row == 1:
                return {"status": "success", "database": "connected"}
            else:
                raise HTTPException(
                    status_code=500,
                    detail="Database connection test failed"
                )
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Database connection error: {str(e)}"
        )

# Test settings import
@app.get("/test-settings")
async def test_settings():
    try:
        from app.core.config import settings
        return {
            "status": "success",
            "app_name": settings.PROJECT_NAME,
            "environment": settings.ENVIRONMENT,
            "debug": settings.DEBUG
        }
    except Exception as e:
        logger.error(f"Settings import error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Settings import error: {str(e)}"
        )

# This allows running with: python simple_main.py
if __name__ == "__main__":
    import uvicorn
    
    # Log startup information
    logger.info("=" * 50)
    logger.info("Starting Paksa Financial System - Debug Mode")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Running on http://0.0.0.0:8000")
    logger.info("=" * 50)
    
    try:
        # Try to import settings to verify they load correctly
        from app.core.config import settings
        logger.info("Successfully imported settings")
        
        # Log all available settings attributes
        logger.info("Available settings attributes:")
        for attr in dir(settings):
            if not attr.startswith('_') and not callable(getattr(settings, attr)):
                # Skip sensitive information like passwords
                if any(sensitive in attr.lower() for sensitive in ['password', 'secret', 'key', 'token']):
                    logger.info(f"  {attr}: [REDACTED]")
                else:
                    logger.info(f"  {attr}: {getattr(settings, attr, None)}")
                    
        logger.info(f"Successfully imported settings: {settings.PROJECT_NAME}")
        logger.info(f"Database URL: {settings.DATABASE_URI}")
    except Exception as e:
        logger.error(f"Failed to import settings: {str(e)}")
        logger.exception("Detailed error:")
    
    try:
        # Run the FastAPI application
        uvicorn.run(
            "simple_main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        sys.exit(1)
