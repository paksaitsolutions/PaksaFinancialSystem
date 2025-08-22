"""
Middleware setup for the FastAPI application.

This module contains functions to set up and configure all middleware components.
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.middleware.rate_limiter import setup_rate_limiter

logger = logging.getLogger(__name__)

def setup_middleware(app: FastAPI, is_development: bool = False) -> None:
    """Set up all middleware components for the FastAPI application.
    
    The order of middleware is important! The first middleware added will be the
    outermost layer, and the last middleware added will be the innermost layer.
    
    Args:
        app: The FastAPI application instance
        is_development: Whether the application is running in development mode
    """
    logger.info("Setting up middleware...")
    
    # 1. CORS Middleware (should be first to handle preflight requests)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 2. Rate Limiting Middleware
    if not is_development:
        setup_rate_limiter(app)
    
    # 3. Add other middleware as needed
    # ...
    
    logger.info("Middleware setup complete")