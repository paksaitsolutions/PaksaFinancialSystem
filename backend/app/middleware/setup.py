"""
Middleware setup for the FastAPI application.

This module contains functions to set up and configure all middleware components.
"""
from fastapi import FastAPI

from . import (
    RequestIDMiddleware,
    RequestLoggingMiddleware,
    RateLimiterMiddleware,
    SecurityHeadersMiddleware,
    SecureHostMiddleware,
    CORSMiddleware,
    setup_security_middleware,
    setup_cors_middleware,
)
from ..core.middleware_config import middleware_settings
from ..core.logging import get_logger

logger = get_logger(__name__)

def setup_middleware(app: FastAPI) -> None:
    """Set up all middleware components for the FastAPI application.
    
    The order of middleware is important! The first middleware added will be the
    outermost layer, and the last middleware added will be the innermost layer.
    """
    logger.info("Setting up middleware...")
    
    # 1. Request ID Middleware (should be first to ensure request ID is available)
    app.add_middleware(
        RequestIDMiddleware,
        header_name=middleware_settings.REQUEST_ID_HEADER,
    )
    
    # 2. Request Logging Middleware (needs request ID)
    if middleware_settings.LOG_REQUESTS:
        app.add_middleware(RequestLoggingMiddleware)
    
    # 3. CORS Middleware (should be before other middleware that might block requests)
    if middleware_settings.CORS_ENABLED:
        setup_cors_middleware(app)
    
    # 4. Security Headers Middleware
    if middleware_settings.SECURITY_HEADERS_ENABLED:
        setup_security_middleware(app)
    
    # 5. Rate Limiting Middleware (after CORS and security headers)
    if middleware_settings.RATE_LIMIT_ENABLED:
        app.add_middleware(
            RateLimiterMiddleware,
            config={
                "key_prefix": "paksa:rate_limit",
                "default_limit": middleware_settings.RATE_LIMIT_DEFAULT,
                "default_window": middleware_settings.RATE_LIMIT_WINDOW,
            },
            redis_url=middleware_settings.REDIS_URL if middleware_settings.USE_REDIS else None,
        )
    
    # 6. Secure Host Middleware (should be after CORS and security headers)
    if middleware_settings.SECURE_HOSTS_ENABLED:
        app.add_middleware(
            SecureHostMiddleware,
            allowed_hosts=middleware_settings.ALLOWED_HOSTS,
            https_redirect=middleware_settings.FORCE_HTTPS,
            www_redirect=True,
        )
    
    logger.info("Middleware setup complete")
