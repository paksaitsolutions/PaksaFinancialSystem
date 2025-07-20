"""
Middleware modules for the FastAPI application.

This package contains various middleware components that can be used to add
functionality to the application, such as request/response processing,
logging, authentication, rate limiting, etc.
"""
from .request_id import RequestIDMiddleware, RequestLoggingMiddleware
from .rate_limiter import RateLimiterMiddleware, rate_limit, RateLimitExceeded
from .security import SecurityHeadersMiddleware, SecureHostMiddleware, setup_security_middleware
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
