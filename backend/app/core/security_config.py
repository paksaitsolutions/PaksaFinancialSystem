"""Security configuration for production deployment"""

from typing import List

class SecurityConfig:
    """Security configuration settings"""
    
    # CSRF Protection Settings
    CSRF_EXEMPT_PATHS: List[str] = [
        "/auth/login",
        "/auth/register", 
        "/auth/token",
        "/auth/refresh-token",
        "/docs",
        "/openapi.json",
        "/health",
        "/",
        # API endpoints exempt for development
        "/api/v1/",
        "/api/",
        "/currency"
    ]
    
    # Rate Limiting Settings
    RATE_LIMIT_REQUESTS = 100
    RATE_LIMIT_WINDOW = 60  # seconds
    
    # Security Headers
    SECURITY_HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY", 
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
    }
    
    # CORS Settings
    ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:3003", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3003"
    ]
    
    # Content Security Policy (relaxed for development)
    CSP_POLICY = "default-src 'self' 'unsafe-inline' 'unsafe-eval'; img-src 'self' data: https:; font-src 'self' https:"
    
    @classmethod
    def is_development(cls) -> bool:
        """Check if running in development mode"""
        import os
        return os.getenv("ENVIRONMENT", "development") == "development"
    
    @classmethod
    def get_csrf_exempt_paths(cls) -> List[str]:
        """Get CSRF exempt paths based on environment"""
        if cls.is_development():
            # In development, exempt all API paths
            return cls.CSRF_EXEMPT_PATHS + ["/api/"]
        else:
            # In production, only exempt auth paths
            return [
                "/auth/login",
                "/auth/register",
                "/auth/token", 
                "/docs",
                "/openapi.json",
                "/health"
            ]