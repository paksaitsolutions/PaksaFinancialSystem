"""
Middleware modules for the FastAPI application.

This package contains various middleware components that can be used to add
functionality to the application, such as request/response processing,
logging, authentication, rate limiting, etc.
"""
from .request_id import RequestIDMiddleware, RequestLoggingMiddleware
from .rate_limiter import RateLimiter as RateLimiterMiddleware, setup_rate_limiter

# Create missing items for compatibility
class RateLimitExceeded(Exception):
    pass

def rate_limit(requests: int = 100, window: int = 60):
    """Rate limit decorator (placeholder)."""
    def decorator(func):
        return func
    return decorator
from .security import SecurityMiddleware as SecurityHeadersMiddleware, CSRFMiddleware as SecureHostMiddleware

def setup_security_middleware(app):
    """Setup security middleware (placeholder)."""
    pass
from .cors import CORSMiddleware, setup_cors_middleware

__all__ = [
    # Request ID
    'RequestIDMiddleware',
    'RequestLoggingMiddleware',
    
    # Rate Limiting
    'RateLimiterMiddleware',
    'rate_limit',
    'RateLimitExceeded',
    
    # Security
    'SecurityHeadersMiddleware',
    'SecureHostMiddleware',
    'setup_security_middleware',
    
    # CORS
    'CORSMiddleware',
    'setup_cors_middleware',
]
