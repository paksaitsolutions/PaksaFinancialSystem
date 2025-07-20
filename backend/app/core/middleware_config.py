"""
Middleware configuration settings.

This module contains configuration settings for various middleware components
used in the application.
"""
import os
from typing import Dict, List, Optional, Pattern, Union

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings

from .config import settings


class MiddlewareSettings(BaseSettings):
    """Middleware configuration settings."""
    
    # Request ID settings
    REQUEST_ID_HEADER: str = "X-Request-ID"
    
    # Rate limiting settings
    RATE_LIMIT_ENABLED: bool = not settings.DEBUG
    RATE_LIMIT_DEFAULT: str = "100/minute"
    RATE_LIMIT_WINDOW: int = 60  # in seconds
    RATE_LIMIT_STORAGE_URL: Optional[str] = os.getenv("REDIS_URL")
    
    # CORS settings
    CORS_ENABLED: bool = True
    CORS_ORIGINS: List[str] = settings.BACKEND_CORS_ORIGINS
    CORS_ORIGIN_REGEX: Optional[str] = None
    CORS_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
    CORS_HEADERS: List[str] = ["*"]
    CORS_CREDENTIALS: bool = True
    CORS_EXPOSE_HEADERS: List[str] = []
    CORS_MAX_AGE: int = 600  # 10 minutes
    
    # Security headers settings
    SECURITY_HEADERS_ENABLED: bool = True
    CONTENT_SECURITY_POLICY: Dict[str, Union[str, List[str]]] = {
        "default-src": ["'self'"],
        "script-src": ["'self'", "'unsafe-inline'", "'unsafe-eval'"],
        "style-src": ["'self'", "'unsafe-inline'"],
        "img-src": ["'self'", "data:", "https:"],
        "font-src": ["'self'", "data:"],
        "connect-src": ["'self'"],
        "frame-src": ["'self'"],
        "object-src": ["'none'"],
        "base-uri": ["'self'"],
        "form-action": ["'self'"],
        "frame-ancestors": ["'none'"],
        "block-all-mixed-content": [],
        "upgrade-insecure-requests": [],
    }
    
    # Security middleware settings
    SECURE_HOSTS_ENABLED: bool = settings.ENVIRONMENT == "production"
    ALLOWED_HOSTS: List[str] = [
        "localhost",
        "127.0.0.1",
        "paksa.finance",
        "api.paksa.finance",
    ]
    FORCE_HTTPS: bool = settings.ENVIRONMENT == "production"
    
    # Logging middleware settings
    LOG_REQUESTS: bool = True
    LOG_RESPONSES: bool = False  # Be careful with this in production
    
    # Redis settings for distributed rate limiting
    USE_REDIS: bool = bool(os.getenv("REDIS_URL"))
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")
    
    @field_validator("CORS_ORIGINS", mode='before')
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse CORS origins from environment variable if needed."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return []
    
    @field_validator("CORS_ORIGIN_REGEX", mode='before')
    @classmethod
    def validate_cors_regex(cls, v: Optional[str]) -> Optional[str]:
        """Validate the CORS origin regex."""
        if not v:
            return None
        try:
            import re
            re.compile(v)
            return v
        except re.error:
            raise ValueError(f"Invalid regex pattern: {v}")
    
    @model_validator(mode='after')
    def set_defaults_based_on_environment(self) -> 'MiddlewareSettings':
        """Set default values based on the environment."""
        if settings.DEBUG:
            # Allow all origins in development
            self.CORS_ORIGINS = ["*"]
            self.CORS_CREDENTIALS = False
            
            # Disable rate limiting in debug mode
            self.RATE_LIMIT_ENABLED = False
            
            # Less strict security headers in development
            self.SECURITY_HEADERS_ENABLED = True
            
            # Enable request/response logging in development
            self.LOG_REQUESTS = True
            self.LOG_RESPONSES = True
        
        return self


# Create middleware settings instance
middleware_settings = MiddlewareSettings()
