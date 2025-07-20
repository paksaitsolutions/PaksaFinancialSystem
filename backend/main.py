"""
Paksa Financial System - Main Application
Version: 1.0.0
Copyright (c) 2025 Paksa IT Solutions. All rights reserved.

This software is the proprietary information of Paksa IT Solutions.
Use is subject to license terms and restrictions.

Main FastAPI application entry point.
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
from app.api.v1.api import api_router
from app.middleware.setup import setup_middleware

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    # Startup
    logger.info("=" * 50)
    logger.info(f"Starting {settings.APP_NAME}...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Database URL: {settings.SQLALCHEMY_DATABASE_URI}")
    logger.info("=" * 50)
    
    # Initialize services, database connections, etc.
    try:
        # Initialize database
        from app.db.init_db import init_db
        await init_db()
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
    title=settings.APP_NAME,
    description="Comprehensive Financial Management System",
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
            "code": exc.__class__.__name__,
            "message": str(exc.detail),
            "status": "error",
        },
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError) -> JSONResponse:
    """Handle request validation errors with detailed error messages."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": "validation_error",
            "message": "Validation Error",
            "status": "error",
            "details": exc.errors(),
        },
    )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception) -> JSONResponse:
    """Global exception handler for uncaught exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": "internal_server_error",
            "message": "An unexpected error occurred",
            "status": "error",
        },
    )

# Root endpoint
@app.get("/", include_in_schema=False)
async def root(request: Request) -> Dict[str, Any]:
    """Root endpoint with basic API information."""
    return {
        "application": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "documentation": "/api/docs" if settings.ENVIRONMENT != "production" else None,
        "status": "operational",
        "request_id": request.state.request_id if hasattr(request.state, 'request_id') else None,
    }

# Health check endpoint
@app.get("/health", include_in_schema=False)
async def health_check() -> Dict[str, str]:
    """Health check endpoint for load balancers and monitoring."""
    # Add more sophisticated health checks here (database, cache, etc.)
    return {"status": "healthy"}
