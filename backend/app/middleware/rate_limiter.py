"""
Rate limiting middleware for API protection.
"""
import time
from typing import Dict, Tuple, Callable, Optional
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.api_response import error_response
from app.core.config import settings

class RateLimiter(BaseHTTPMiddleware):
    """
    Rate limiting middleware to protect API endpoints from abuse.
    
    Uses a simple in-memory store for rate limiting. For production,
    consider using Redis or another distributed cache.
    """
    
    def __init__(
        self, 
        app: ASGIApp, 
        requests_limit: int = 100,
        window_seconds: int = 60,
        exclude_paths: Optional[list] = None
    ):
        super().__init__(app)
        self.requests_limit = requests_limit
        self.window_seconds = window_seconds
        self.exclude_paths = exclude_paths or ["/health", "/metrics", "/api/docs", "/api/redoc"]
        # Store format: {ip: (requests_count, window_start_time)}
        self.request_store: Dict[str, Tuple[int, float]] = {}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process the request and apply rate limiting."""
        # Skip rate limiting for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Check if client is rate limited
        current_time = time.time()
        if client_ip in self.request_store:
            requests_count, window_start = self.request_store[client_ip]
            
            # Reset window if it has expired
            if current_time - window_start > self.window_seconds:
                self.request_store[client_ip] = (1, current_time)
            else:
                # Increment request count
                requests_count += 1
                self.request_store[client_ip] = (requests_count, window_start)
                
                # Check if limit exceeded
                if requests_count > self.requests_limit:
                    return error_response(
                        message="Rate limit exceeded. Please try again later.",
                        status_code=429,
                        error_code="RATE_LIMIT_EXCEEDED"
                    )
        else:
            # First request from this client
            self.request_store[client_ip] = (1, current_time)
        
        # Process the request
        response = await call_next(request)
        
        # Add rate limit headers
        if client_ip in self.request_store:
            requests_count, window_start = self.request_store[client_ip]
            response.headers["X-RateLimit-Limit"] = str(self.requests_limit)
            response.headers["X-RateLimit-Remaining"] = str(max(0, self.requests_limit - requests_count))
            response.headers["X-RateLimit-Reset"] = str(int(window_start + self.window_seconds))
        
        return response

def setup_rate_limiter(app: FastAPI) -> None:
    """Set up rate limiting middleware."""
    # Parse rate limit from settings (format: "100/minute")
    rate_limit = getattr(settings, "RATE_LIMIT", "100/minute")
    try:
        limit, period = rate_limit.split("/")
        limit = int(limit)
        
        if period.lower() in ["s", "sec", "second", "seconds"]:
            window = 1
        elif period.lower() in ["m", "min", "minute", "minutes"]:
            window = 60
        elif period.lower() in ["h", "hour", "hours"]:
            window = 3600
        elif period.lower() in ["d", "day", "days"]:
            window = 86400
        else:
            window = 60  # Default to minutes
    except (ValueError, AttributeError):
        # Default values if parsing fails
        limit = 100
        window = 60
    
    app.add_middleware(
        RateLimiter,
        requests_limit=limit,
        window_seconds=window
    )