"""
Paksa Financial System - Main Application Package Entry Point

This module serves as the main entry point for the FastAPI application when run as a package.
"""
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Absolute imports
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.middleware_config import middleware_settings

# Import API router
from app.api import api_router
from app.middleware.setup import setup_middleware

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    # Startup
    logger.info("=" * 50)
    logger.info(f"Starting {settings.PROJECT_NAME}...")
    logger.info(f"Version: {settings.VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Database Engine: {settings.DB_ENGINE}")
    
    if settings.IS_SQLITE:
        logger.info(f"SQLite Database Path: {settings.SQLITE_DB_PATH}")
    else:
        logger.info(f"PostgreSQL Database: {settings.POSTGRES_USER}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}")
    
    logger.info("=" * 50)
    
    # Initialize services, database connections, etc.
    try:
        # Initialize database
        logger.info("Initializing database...")
        from app.core.db.init_db import init_db
        try:
            await init_db()
            logger.info("Database initialization completed successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}", exc_info=True)
            raise
        logger.info("Database initialization complete")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}", exc_info=True)
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Paksa Financial System...")
    # Clean up resources, close connections, etc.

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.API_VERSION,
    docs_url="/api/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/api/redoc" if settings.ENVIRONMENT != "production" else None,
    openapi_url=f"{settings.API_PREFIX}/openapi.json" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan,
    default_response_class=JSONResponse,
)

# Set up all middleware
# Setup middleware with development flag based on environment
setup_middleware(app, is_development=settings.ENVIRONMENT == "development")

# Include API router
app.include_router(api_router)

# Global exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle HTTP exceptions with consistent error format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail,
            "error": exc.detail if settings.DEBUG else None,
        },
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle request validation errors with detailed error messages."""
    errors = []
    for error in exc.errors():
        errors.append({
            "loc": error["loc"],
            "msg": error["msg"],
            "type": error["type"],
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "error",
            "message": "Validation error",
            "errors": errors if settings.DEBUG else None,
        },
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler for uncaught exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": "Internal server error",
            "error": str(exc) if settings.DEBUG else None,
        },
    )

# Root endpoint
@app.get("/", include_in_schema=False)
async def root(request: Request):
    """Root endpoint with basic API information."""
    return {
        "status": "success",
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "version": settings.API_VERSION,
        "environment": settings.ENVIRONMENT,
        "documentation": {
            "swagger": "/api/docs",
            "redoc": "/api/redoc",
            "openapi": "/api/openapi.json",
        } if settings.ENVIRONMENT != "production" else None,
    }

# Health check endpoint
@app.get("/health", include_in_schema=False)
async def health_check():
    """Health check endpoint for load balancers and monitoring."""
    return {"status": "ok"}

# This allows running the app with: python -m app.main
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
