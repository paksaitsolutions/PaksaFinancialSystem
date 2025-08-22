"""
Incremental FastAPI application to identify the issue.
"""
import logging
import sys
import traceback
from pathlib import Path
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import os

# Set environment variables for debugging
os.environ["ENV"] = "development"
os.environ["DEBUG"] = "True"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./paksa_finance.db"

# Add the current directory to Python path
current_dir = str(Path(__file__).parent)
sys.path.insert(0, current_dir)

# Set up basic logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('debug.log')
    ]
)
logger = logging.getLogger(__name__)

def log_step(step_name: str, success: bool, details: str = ""):
    """Log a step with its status and details."""
    status = "SUCCESS" if success else "FAILED"
    logger.info(f"{step_name}: {status}")
    if details:
        logger.debug(f"Details: {details}")
    return {"step": step_name, "status": status, "details": details}

async def test_import(module_path: str):
    """Test importing a module and return the result."""
    try:
        module = __import__(module_path, fromlist=[''])
        return {"status": "success", "module": module_path}
    except ImportError as e:
        return {"status": "error", "error": str(e), "traceback": traceback.format_exc()}
    except Exception as e:
        return {"status": "error", "error": str(e), "traceback": traceback.format_exc()}

def create_app():
    """Create and configure the FastAPI application."""
    # Initialize FastAPI app with basic settings
    app = FastAPI(
        title="Paksa Financial System - Debug",
        description="Debugging tool to identify issues",
        version="1.0.0"
    )
    
    # Store test results
    test_results = []
    
    # Basic health check endpoint
    @app.get("/")
    async def root():
        return {
            "message": "Paksa Financial System Debug Tool",
            "endpoints": [
                "/health - Basic health check",
                "/test-imports - Test module imports",
                "/test-config - Test configuration loading",
                "/test-db - Test database connection",
                "/test-models - Test database models"
            ]
        }
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {"status": "ok", "python_version": sys.version}
    
    # Test imports
    @app.get("/test-imports")
    async def test_imports():
        results = []
        
        # Test core imports
        core_imports = [
            "app.core.config",
            "app.core.logging",
            "app.core.middleware_config"
        ]
        
        for imp in core_imports:
            result = await test_import(imp)
            results.append({"module": imp, "status": result["status"]})
            if "error" in result:
                results[-1]["error"] = result["error"]
        
        return {"import_tests": results}
    
    # Test configuration
    @app.get("/test-config")
    async def test_config():
        try:
            from app.core.config import settings
            return {
                "status": "success",
                "config": {
                    "PROJECT_NAME": settings.PROJECT_NAME,
                    "ENVIRONMENT": settings.ENVIRONMENT,
                    "DEBUG": settings.DEBUG,
                    "DATABASE_URL": settings.SQLALCHEMY_DATABASE_URI if hasattr(settings, 'SQLALCHEMY_DATABASE_URI') else "Not set",
                    "IS_SQLITE": settings.IS_SQLITE if hasattr(settings, 'IS_SQLITE') else "Not set"
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "traceback": traceback.format_exc()
            }
    
    # Test database connection
    @app.get("/test-db")
    async def test_db():
        try:
            from app.core.config import settings
            from sqlalchemy.ext.asyncio import create_async_engine
            import asyncio
            
            # Create engine
            engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI)
            
            # Test connection
            async with engine.connect() as conn:
                result = await conn.execute("SELECT 1")
                value = result.scalar()
                
                if value == 1:
                    return {"status": "success", "message": "Database connection successful"}
                else:
                    return {"status": "error", "message": "Unexpected database response"}
                    
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "traceback": traceback.format_exc()
            }
    
    # Test database models
    @app.get("/test-models")
    async def test_models():
        try:
            from app.core.db.base import Base
            from sqlalchemy import inspect
            from sqlalchemy.ext.asyncio import create_async_engine
            from app.core.config import settings
            
            engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI)
            inspector = inspect(engine.sync_engine)
            tables = inspector.get_table_names()
            
            return {
                "status": "success",
                "tables": tables,
                "metadata_tables": list(Base.metadata.tables.keys())
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "traceback": traceback.format_exc()
            }
    
    return app

if __name__ == "__main__":
    logger.info("Starting debug FastAPI application...")
    logger.info(f"Python path: {sys.path}")
    logger.info(f"Current directory: {os.getcwd()}")
    
    app = create_app()
    uvicorn.run(
        "incremental_app:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="debug"
    )
