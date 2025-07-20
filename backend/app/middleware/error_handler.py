"""
Global error handling middleware for the FastAPI application.

This module provides a centralized way to handle and format exceptions
that occur during request processing.
"""
import logging
from typing import Callable, Dict, Any, Optional, Union

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException as FastAPIHTTPException
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.logging import get_logger

logger = get_logger(__name__)

class ErrorResponse(BaseModel):
    """Standard error response model."""
    success: bool = False
    error: str
    code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class APIError(Exception):
    """Base exception for API errors."""
    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        message: str = "An error occurred",
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.status_code = status_code
        self.message = message
        self.code = code or self.__class__.__name__
        self.details = details
        super().__init__(message)

class NotFoundError(APIError):
    """Raised when a resource is not found."""
    def __init__(self, resource: str = "Resource", **kwargs):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=f"{resource} not found",
            **kwargs
        )

class UnauthorizedError(APIError):
    """Raised when authentication is required but not provided or invalid."""
    def __init__(self, message: str = "Not authenticated", **kwargs):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message=message,
            **kwargs
        )

class ForbiddenError(APIError):
    """Raised when the user doesn't have permission to access a resource."""
    def __init__(self, message: str = "Insufficient permissions", **kwargs):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            message=message,
            **kwargs
        )

class ValidationError(APIError):
    """Raised when request validation fails."""
    def __init__(self, errors: Dict[str, Any], **kwargs):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Validation error",
            details={"fields": errors},
            **kwargs
        )

class ConflictError(APIError):
    """Raised when there's a conflict with the current state of the resource."""
    def __init__(self, message: str = "Resource conflict", **kwargs):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            message=message,
            **kwargs
        )

def setup_error_handlers(app: FastAPI) -> None:
    """Register global exception handlers for the FastAPI application.
    
    Args:
        app: The FastAPI application instance.
    """
    @app.exception_handler(APIError)
    async def handle_api_error(request: Request, exc: APIError) -> JSONResponse:
        """Handle custom API errors."""
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=exc.message,
                code=exc.code,
                details=exc.details,
            ).model_dump(),
        )
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        """Handle HTTP exceptions."""
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=exc.detail,
                code=exc.__class__.__name__,
            ).model_dump(),
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle request validation errors."""
        errors = {}
        for error in exc.errors():
            field = ".".join([str(loc) for loc in error["loc"][1:]])
            errors[field] = error["msg"]
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ErrorResponse(
                error="Validation error",
                code="VALIDATION_ERROR",
                details={"fields": errors},
            ).model_dump(),
        )
    
    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(
        request: Request, exc: ValidationError
    ) -> JSONResponse:
        """Handle Pydantic validation errors."""
        errors = {}
        for error in exc.errors():
            field = ".".join([str(loc) for loc in error["loc"][1:]])
            errors[field] = error["msg"]
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ErrorResponse(
                error="Validation error",
                code="VALIDATION_ERROR",
                details={"fields": errors},
            ).model_dump(),
        )
    
    @app.exception_handler(Exception)
    async def global_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Handle all other exceptions."""
        logger.exception(
            "Unhandled exception",
            exc_info=exc,
            extra={
                "request": {
                    "method": request.method,
                    "url": str(request.url),
                    "headers": dict(request.headers),
                    "query_params": dict(request.query_params),
                },
            },
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error="Internal server error",
                code="INTERNAL_SERVER_ERROR",
            ).model_dump(),
        )

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware to catch and handle exceptions globally."""
    
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
    
    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> JSONResponse:
        """Process the request and handle any exceptions."""
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            # Log the error
            logger.exception(
                "Unhandled exception in middleware",
                exc_info=exc,
                extra={
                    "request": {
                        "method": request.method,
                        "url": str(request.url),
                        "headers": dict(request.headers),
                        "query_params": dict(request.query_params),
                    },
                },
            )
            
            # Handle known exceptions
            if isinstance(exc, APIError):
                return JSONResponse(
                    status_code=exc.status_code,
                    content=ErrorResponse(
                        error=exc.message,
                        code=exc.code,
                        details=exc.details,
                    ).model_dump(),
                )
            elif isinstance(exc, StarletteHTTPException):
                return JSONResponse(
                    status_code=exc.status_code,
                    content=ErrorResponse(
                        error=str(exc.detail),
                        code=exc.__class__.__name__,
                    ).model_dump(),
                )
            
            # Default error response
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Internal server error",
                    code="INTERNAL_SERVER_ERROR",
                ).model_dump(),
            )

def setup_middleware(app: FastAPI) -> None:
    """Set up all middleware for the FastAPI application."""
    # Add error handling middleware
    app.add_middleware(ErrorHandlerMiddleware)
    
    # Register exception handlers
    setup_error_handlers(app)
