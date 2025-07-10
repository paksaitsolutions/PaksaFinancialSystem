"""
Paksa Financial System - Error Handling Middleware
Version: 1.0.0
Copyright (c) 2025 Paksa IT Solutions. All rights reserved.

This software is the proprietary information of Paksa IT Solutions.
Use is subject to license terms and restrictions.

Middleware for consistent error handling and logging.
"""

import logging
import json
from typing import Callable, Dict, Any, Optional
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)

class PaksaErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Global error handling middleware for consistent error responses.
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            # Process the request
            response = await call_next(request)
            return response
            
        except Exception as exc:
            # Log the error
            logger.error(
                f"Unhandled exception: {str(exc)}",
                exc_info=True,
                extra={
                    "path": request.url.path,
                    "method": request.method,
                    "client": request.client.host if request.client else "unknown",
                },
            )
            
            # Return a consistent error response
            error_detail = {
                "code": "internal_server_error",
                "message": "An unexpected error occurred",
                "status": "error",
                "details": str(exc),
            }
            
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=error_detail,
            )

class PaksaRequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses.
    """
    
    def __init__(self, app: ASGIApp, *, logger: logging.Logger):
        self._logger = logger
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip logging for health checks and metrics
        if request.url.path in ["/health", "/metrics", "/docs", "/openapi.json"]:
            return await call_next(request)
        
        # Log request
        self._log_request(request)
        
        # Process the request
        response = await call_next(request)
        
        # Log response
        self._log_response(request, response)
        
        return response
    
    def _log_request(self, request: Request) -> None:
        """Log the incoming request."""
        try:
            # Get client IP
            client_host = request.client.host if request.client else "unknown"
            
            # Log basic request info
            self._logger.info(
                "Request: %s %s from %s",
                request.method,
                request.url.path,
                client_host,
                extra={
                    "type": "request",
                    "method": request.method,
                    "path": request.url.path,
                    "client": client_host,
                    "query_params": dict(request.query_params),
                    "headers": self._filter_headers(request.headers),
                },
            )
            
        except Exception as e:
            self._logger.error("Error logging request: %s", str(e), exc_info=True)
    
    def _log_response(self, request: Request, response: Response) -> None:
        """Log the outgoing response."""
        try:
            # Get response content if it's JSON
            response_body = b""
            if hasattr(response, "body"):
                response_body = getattr(response, "body", b"")
            
            # Parse response body if it's JSON
            response_content = {}
            content_type = response.headers.get("content-type", "")
            if "application/json" in content_type and response_body:
                try:
                    response_content = json.loads(response_body.decode())
                except (json.JSONDecodeError, UnicodeDecodeError):
                    response_content = {"content": "[binary data]"}
            
            # Log response info
            self._logger.info(
                "Response: %s %s - %d",
                request.method,
                request.url.path,
                response.status_code,
                extra={
                    "type": "response",
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "response_size": len(response_body) if response_body else 0,
                    "content_type": content_type,
                    "response": response_content if response.status_code >= 400 else {},
                },
            )
            
        except Exception as e:
            self._logger.error("Error logging response: %s", str(e), exc_info=True)
    
    def _filter_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Filter sensitive headers before logging."""
        sensitive_headers = {"authorization", "cookie", "set-cookie", "x-api-key"}
        return {
            k: "[REDACTED]" if k.lower() in sensitive_headers else v
            for k, v in headers.items()
        }

def setup_middleware(app: ASGIApp) -> None:
    """
    Set up all middleware for the application.
    
    Args:
        app: The FastAPI application instance.
    """
    # Add error handling middleware
    app.add_middleware(PaksaErrorHandlerMiddleware)
    
    # Add request/response logging middleware
    app.add_middleware(
        PaksaRequestLoggingMiddleware,
        logger=logging.getLogger("paksa.request")
    )
    
    # Add CORS middleware (handled in main.py)
    # Add rate limiting middleware (to be implemented)
    # Add authentication middleware (handled by FastAPI's dependency injection)
