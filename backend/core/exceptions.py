from fastapi import HTTPException, status
from typing import Any, Dict, Optional
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class BaseAPIException(HTTPException):
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail: str = "An unexpected error occurred"
    error_code: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def __init__(
        self,
        detail: Optional[str] = None,
        error_code: Optional[str] = None,
        status_code: Optional[int] = None,
        headers: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.detail = detail or self.detail
        self.error_code = error_code or self.error_code
        self.status_code = status_code or self.status_code
        self.headers = headers
        self.metadata = metadata
        super().__init__(
            status_code=self.status_code,
            detail=self.detail,
            headers=self.headers,
        )

class NotFoundException(BaseAPIException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "The requested resource was not found"
    error_code = "not_found"

class ValidationException(BaseAPIException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = "Validation error"
    error_code = "validation_error"

class UnauthorizedException(BaseAPIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Not authenticated"
    error_code = "unauthorized"

class ForbiddenException(BaseAPIException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Not enough permissions"
    error_code = "forbidden"

class ConflictException(BaseAPIException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Resource already exists"
    error_code = "conflict"

class RateLimitException(BaseAPIException):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    detail = "Too many requests"
    error_code = "rate_limit_exceeded"

def handle_api_exception(request, exc: BaseAPIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_code": exc.error_code,
            "metadata": exc.metadata,
        },
    )

def handle_validation_error(request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "error_code": "validation_error",
            "errors": exc.errors(),
        },
    )

def handle_http_exception(request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_code": "http_error",
        },
    )

def handle_generic_exception(request, exc: Exception):
    # In production, you might want to log this error to your monitoring system
    import logging
    logging.exception("Unhandled exception")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "error_code": "internal_server_error",
        },
    )
