"""
Rate limiting middleware for FastAPI.

This middleware implements rate limiting to protect the API from abuse.
It supports different rate limiting strategies and can be configured per endpoint.
"""
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Callable, Dict, List, Optional, Set, Tuple, Union

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.concurrency import run_in_threadpool
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.config import settings
from app.core.logging import get_logger
from app.core.redis import get_redis

logger = get_logger(__name__)

class RateLimitExceeded(HTTPException):
    """Exception raised when a rate limit is exceeded."""
    
    def __init__(
        self,
        detail: str = "Rate limit exceeded",
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        """Initialize the exception."""
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            headers=headers or {},
        )

class RateLimitConfig:
    """Configuration for rate limiting."""
    
    def __init__(
        self,
        key_prefix: str = "rate_limit",
        default_limit: int = 100,
        default_window: int = 60,  # in seconds
        default_identifier: Optional[Callable[[Request], str]] = None,
        enabled: bool = True,
    ) -> None:
        """Initialize the rate limit configuration."""
        self.key_prefix = key_prefix
        self.default_limit = default_limit
        self.default_window = default_window
        self.default_identifier = default_identifier or self._default_identifier
        self.enabled = enabled
        self.limits: Dict[str, Dict[str, Tuple[int, int]]] = defaultdict(dict)
    
    def _default_identifier(self, request: Request) -> str:
        """Default identifier function that uses the client's IP address."""
        # Get the client's IP address
        if request.client is None:
            return "unknown"
        
        # Check for X-Forwarded-For header (common when behind a proxy)
        if "x-forwarded-for" in request.headers:
            # Get the first IP in the X-Forwarded-For list
            return request.headers["x-forwarded-for"].split(",")[0].strip()
        
        # Fall back to the client's IP address
        return request.client.host or "unknown"
    
    def limit(
        self,
        limit: int,
        window: int,
        key: Optional[str] = None,
        identifier: Optional[Callable[[Request], str]] = None,
    ) -> Callable:
        """Decorator to apply rate limiting to a specific endpoint."""
        def decorator(func: Callable) -> Callable:
            # Use the function's module and name as the key if not provided
            endpoint_key = key or f"{func.__module__}.{func.__name__}"
            self.limits[endpoint_key]["default"] = (limit, window)
            
            # Store the identifier function if provided
            if identifier is not None:
                self.limits[endpoint_key]["identifier"] = identifier
            
            return func
        return decorator

class RateLimiterMiddleware(BaseHTTPMiddleware):
    """Middleware that enforces rate limiting."""
    
    def __init__(
        self,
        app: ASGIApp,
        config: Optional[RateLimitConfig] = None,
        redis_url: Optional[str] = None,
    ) -> None:
        """Initialize the rate limiter middleware."""
        super().__init__(app)
        self.config = config or RateLimitConfig()
        self.redis_url = redis_url
        self.redis = None
        self.windows: Dict[str, Dict[str, deque]] = defaultdict(lambda: defaultdict(deque))
    
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Process the request and enforce rate limits."""
        # Skip rate limiting if disabled
        if not self.config.enabled:
            return await call_next(request)
        
        # Get the endpoint key
        endpoint_key = f"{request.url.path}:{request.method}"
        
        # Get the rate limit configuration for this endpoint
        limit_info = self.config.limits.get(endpoint_key, {})
        limit, window = limit_info.get("default", (self.config.default_limit, self.config.default_window))
        identifier_func = limit_info.get("identifier", self.config.default_identifier)
        
        # Get the identifier for this request
        identifier = identifier_func(request)
        
        # Generate a unique key for this rate limit window
        now = int(time.time())
        window_start = now // window * window
        key = f"{self.config.key_prefix}:{endpoint_key}:{identifier}:{window_start}"
        
        try:
            # Check if we're using Redis
            if self.redis_url:
                await self._check_redis_rate_limit(key, limit, window)
            else:
                await self._check_in_memory_rate_limit(key, limit, window, now)
            
            # Process the request
            response = await call_next(request)
            
            # Add rate limit headers to the response
            self._add_rate_limit_headers(response, limit, window, key, now)
            
            return response
            
        except RateLimitExceeded as exc:
            # Add rate limit headers to the error response
            response = Response(
                content=exc.detail,
                status_code=exc.status_code,
                headers=exc.headers,
            )
            self._add_rate_limit_headers(response, limit, window, key, now, exceeded=True)
            return response
    
    async def _check_redis_rate_limit(
        self, key: str, limit: int, window: int
    ) -> None:
        """Check the rate limit using Redis."""
        if self.redis is None:
            self.redis = await get_redis()
        
        # Use a pipeline for atomic operations
        async with self.redis.pipeline() as pipe:
            try:
                # Increment the counter and set expiration
                pipe.incr(key)
                pipe.expire(key, window)
                results = await pipe.execute()
                
                # Check if the limit has been exceeded
                count = results[0]
                if count > limit:
                    raise RateLimitExceeded(
                        detail=f"Rate limit exceeded: {count}/{limit} requests per {window} seconds",
                        headers={
                            "Retry-After": str(window),
                            "X-RateLimit-Limit": str(limit),
                            "X-RateLimit-Remaining": "0",
                            "X-RateLimit-Reset": str(int(time.time()) + window),
                        },
                    )
            except Exception as e:
                logger.error(f"Redis error in rate limiter: {str(e)}")
                # Fail open - don't block requests if Redis is down
                pass
    
    async def _check_in_memory_rate_limit(
        self, key: str, limit: int, window: int, current_time: int
    ) -> None:
        """Check the rate limit using in-memory storage."""
        # Get the window for this key
        timestamps = self.windows[key]
        
        # Remove timestamps that are outside the current window
        while timestamps and timestamps[0] <= current_time - window:
            timestamps.popleft()
        
        # Check if the limit has been exceeded
        if len(timestamps) >= limit:
            retry_after = window - (current_time - timestamps[0])
            raise RateLimitExceeded(
                detail=f"Rate limit exceeded: {len(timestamps)}/{limit} requests per {window} seconds",
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time()) + retry_after),
                },
            )
        
        # Add the current timestamp
        timestamps.append(current_time)
    
    def _add_rate_limit_headers(
        self,
        response: Response,
        limit: int,
        window: int,
        key: str,
        current_time: int,
        exceeded: bool = False,
    ) -> None:
        """Add rate limit headers to the response."""
        remaining = 0
        reset_time = current_time + window
        
        if self.redis_url and self.redis:
            # Get the current count from Redis
            count = self.redis.get(key)
            if count is not None:
                remaining = max(0, limit - int(count))
        else:
            # Get the current count from in-memory storage
            timestamps = self.windows.get(key, [])
            remaining = max(0, limit - len(timestamps))
            if timestamps:
                reset_time = timestamps[0] + window
        
        # Add the rate limit headers
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_time)
        
        if exceeded:
            response.headers["Retry-After"] = str(window)

# Global rate limit configuration
rate_limit_config = RateLimitConfig(
    key_prefix="paksa:rate_limit",
    default_limit=settings.RATE_LIMIT_DEFAULT,
    default_window=settings.RATE_LIMIT_WINDOW,
    enabled=settings.RATE_LIMIT_ENABLED,
)

# Rate limit decorator for endpoints
rate_limit = rate_limit_config.limit

def setup_rate_limiter(app: FastAPI) -> None:
    """Set up the rate limiter middleware."""
    if settings.RATE_LIMIT_ENABLED:
        app.add_middleware(
            RateLimiterMiddleware,
            config=rate_limit_config,
            redis_url=settings.REDIS_URL if settings.USE_REDIS else None,
        )
