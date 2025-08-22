"""
Request ID middleware for FastAPI.

This middleware adds a unique request ID to each incoming request and includes it in the response headers.
It also makes the request ID available in the request state for use in logging and error handling.
"""
import uuid
from typing import Callable, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.logging import get_logger

logger = get_logger(__name__)

class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware that adds a unique request ID to each request."""
    
    def __init__(
        self,
        app: ASGIApp,
        header_name: str = "X-Request-ID",
        generate_request_id: Optional[Callable[[], str]] = None,
    ) -> None:
        """Initialize the middleware.
        
        Args:
            app: The ASGI application.
            header_name: The name of the header to use for the request ID.
            generate_request_id: A callable that generates a request ID.
        """
        super().__init__(app)
        self.header_name = header_name
        self.generate_request_id = generate_request_id or (lambda: str(uuid.uuid4()))
    
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Process the request and add a request ID."""
        # Get the request ID from the headers or generate a new one
        request_id = request.headers.get(self.header_name.lower())
        if not request_id:
            request_id = self.generate_request_id()
        
        # Add the request ID to the request state
        request.state.request_id = request_id
        
        # Process the request
        response = await call_next(request)
        
        # Add the request ID to the response headers
        response.headers[self.header_name] = request_id
        
        return response

class RequestIDLogFilter:
    """Log filter to add request ID to log records."""
    
    def __init__(self, request_id: str):
        self.request_id = request_id
    
    def __call__(self, record):
        record.request_id = self.request_id
        return True

class RequestLoggingMiddleware:
    """Middleware that logs request and response information."""
    
    def __init__(self, app: ASGIApp) -> None:
        self.app = app
    
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Process the request and log request/response information."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive=receive)
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        
        # Add request ID to the request state
        request.state.request_id = request_id
        
        # Create a filter to add the request ID to log records
        log_filter = RequestIDLogFilter(request_id)
        
        # Log the request
        logger.info(
            "Request started",
            extra={
                "request": {
                    "method": request.method,
                    "url": str(request.url),
                    "headers": dict(request.headers),
                    "query_params": dict(request.query_params),
                },
                "request_id": request_id,
            },
            extra_filters=[log_filter],
        )
        
        # Process the request
        response_body = []
        
        async def send_with_logging(message: Message) -> None:
            """Send the response and log the response information."""
            if message["type"] == "http.response.body":
                response_body.append(message.get("body", b"").decode())
            
            if message.get("more_body", False):
                await send(message)
            else:
                # Log the response
                logger.info(
                    "Request completed",
                    extra={
                        "request": {
                            "method": request.method,
                            "url": str(request.url),
                        },
                        "response": {
                            "status_code": message.get("status", 200),
                            "body": "".join(response_body) if response_body else None,
                        },
                        "request_id": request_id,
                    },
                    extra_filters=[log_filter],
                )
                await send(message)
        
        try:
            await self.app(scope, receive, send_with_logging)
        except Exception as exc:
            # Log any exceptions that occur during request processing
            logger.exception(
                "Unhandled exception during request processing",
                extra={
                    "request": {
                        "method": request.method,
                        "url": str(request.url),
                    },
                    "request_id": request_id,
                },
                extra_filters=[log_filter],
            )
            raise
