"""
CORS (Cross-Origin Resource Sharing) middleware for FastAPI.

This middleware handles CORS preflight requests and adds the appropriate CORS headers
to responses. It's configurable to allow requests from specific origins, methods, and headers.
"""
import re
from typing import Any, Callable, Dict, List, Optional, Pattern, Set, Tuple, Union

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

class CORSMiddleware(BaseHTTPMiddleware):
    """Middleware that adds CORS headers to responses."""
    
    def __init__(
        self,
        app: ASGIApp,
        allow_origins: Optional[List[Union[Pattern, str]]] = None,
        allow_origin_regex: Optional[str] = None,
        allow_methods: Optional[List[str]] = None,
        allow_headers: Optional[List[str]] = None,
        allow_credentials: bool = False,
        expose_headers: Optional[List[str]] = None,
        max_age: int = 600,
    ) -> None:
        """Initialize the CORS middleware.
        
        Args:
            app: The ASGI application.
            allow_origins: List of allowed origins (can be strings or compiled regex patterns).
            allow_origin_regex: A regex pattern string to match against the request origin.
            allow_methods: List of allowed HTTP methods.
            allow_headers: List of allowed HTTP headers.
            allow_credentials: Whether to allow credentials in CORS requests.
            expose_headers: List of headers to expose to the browser.
            max_age: Maximum time (in seconds) to cache CORS preflight responses.
        """
        super().__init__(app)
        
        # Default allowed origins
        self.allow_origins = allow_origins or []
        
        # Compile the origin regex if provided
        self.allow_origin_regex = None
        if allow_origin_regex:
            self.allow_origin_regex = re.compile(allow_origin_regex)
        
        # Default allowed methods
        self.allow_methods = allow_methods or ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
        
        # Default allowed headers
        self.allow_headers = allow_headers or ["*"]
        
        # Other CORS settings
        self.allow_credentials = allow_credentials
        self.expose_headers = expose_headers or []
        self.max_age = max_age
        
        # Pre-compute the allowed methods and headers strings
        self.allow_methods_str = ", ".join(self.allow_methods)
        self.allow_headers_str = ", ".join(self.allow_headers)
        self.expose_headers_str = ", ".join(self.expose_headers)
    
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Process the request and add CORS headers to the response."""
        # Get the origin from the request headers
        origin = request.headers.get("origin")
        
        # If this is a CORS preflight request, handle it immediately
        if request.method == "OPTIONS" and "access-control-request-method" in request.headers:
            return await self._handle_preflight_request(request)
        
        # Process the request
        response = await call_next(request)
        
        # Add CORS headers to the response
        self._add_cors_headers(request, response, origin)
        
        return response
    
    async def _handle_preflight_request(self, request: Request) -> Response:
        """Handle a CORS preflight request."""
        # Get the origin and request method/headers
        origin = request.headers.get("origin")
        request_method = request.headers.get("access-control-request-method")
        request_headers = request.headers.get("access-control-request-headers", "")
        
        # Check if the origin is allowed
        if not self._is_origin_allowed(origin):
            return Response(
                content="Origin not allowed",
                status_code=403,
                headers={"Content-Type": "text/plain"},
            )
        
        # Create a response with the appropriate CORS headers
        headers = self._get_cors_headers(origin, request_method, request_headers)
        
        return Response(
            content="",
            status_code=204,
            headers=headers,
        )
    
    def _add_cors_headers(
        self, request: Request, response: Response, origin: Optional[str] = None
    ) -> None:
        """Add CORS headers to the response."""
        # If no origin is provided, try to get it from the request
        if origin is None:
            origin = request.headers.get("origin")
        
        # If still no origin, we can't add CORS headers
        if not origin:
            return
        
        # Check if the origin is allowed
        if not self._is_origin_allowed(origin):
            return
        
        # Add the CORS headers
        response.headers["Access-Control-Allow-Origin"] = origin
        
        if self.allow_credentials:
            response.headers["Access-Control-Allow-Credentials"] = "true"
        
        if self.expose_headers:
            response.headers["Access-Control-Expose-Headers"] = self.expose_headers_str
    
    def _get_cors_headers(
        self,
        origin: str,
        request_method: Optional[str] = None,
        request_headers: Optional[str] = None,
    ) -> Dict[str, str]:
        """Get the CORS headers for a response."""
        headers: Dict[str, str] = {}
        
        # Add the allowed origin
        headers["Access-Control-Allow-Origin"] = origin
        
        # Add credentials if allowed
        if self.allow_credentials:
            headers["Access-Control-Allow-Credentials"] = "true"
        
        # Handle preflight request
        if request_method is not None:
            headers["Access-Control-Allow-Methods"] = self.allow_methods_str
            headers["Access-Control-Max-Age"] = str(self.max_age)
            
            # Add allowed headers
            if request_headers:
                headers["Access-Control-Allow-Headers"] = request_headers
            elif self.allow_headers_str:
                headers["Access-Control-Allow-Headers"] = self.allow_headers_str
        
        # Add exposed headers if any
        if self.expose_headers:
            headers["Access-Control-Expose-Headers"] = self.expose_headers_str
        
        return headers
    
    def _is_origin_allowed(self, origin: Optional[str]) -> bool:
        """Check if the origin is allowed."""
        if not origin:
            return False
        
        # Allow all origins in development
        if settings.DEBUG:
            return True
        
        # Check against allowed origins
        for allowed_origin in self.allow_origins:
            if isinstance(allowed_origin, str):
                if origin == allowed_origin:
                    return True
            elif hasattr(allowed_origin, "match"):
                if allowed_origin.match(origin):
                    return True
        
        # Check against the origin regex if provided
        if self.allow_origin_regex and self.allow_origin_regex.match(origin):
            return True
        
        return False


def setup_cors_middleware(app: FastAPI) -> None:
    """Set up CORS middleware for the FastAPI application."""
    # Get CORS settings from the config
    allow_origins = settings.CORS_ORIGINS
    allow_origin_regex = settings.CORS_ORIGIN_REGEX
    allow_methods = settings.CORS_METHODS
    allow_headers = settings.CORS_HEADERS
    allow_credentials = settings.CORS_CREDENTIALS
    expose_headers = settings.CORS_EXPOSE_HEADERS
    max_age = settings.CORS_MAX_AGE
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_origin_regex=allow_origin_regex,
        allow_methods=allow_methods,
        allow_headers=allow_headers,
        allow_credentials=allow_credentials,
        expose_headers=expose_headers,
        max_age=max_age,
    )
