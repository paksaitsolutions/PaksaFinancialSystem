"""
Custom exceptions for the application.
"""
from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class PaksaException(Exception):
    """Base exception for Paksa Financial System."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ValidationException(PaksaException):
    """Raised when validation fails."""
    pass


class NotFoundException(PaksaException):
    """Raised when a resource is not found."""
    pass


class BadRequestException(PaksaException):
    """Raised when request is invalid."""
    pass


class ForbiddenException(PaksaException):
    """Raised when access is forbidden."""
    pass


class UnauthorizedException(PaksaException):
    """Raised when user is not authenticated."""
    pass


class ConflictException(PaksaException):
    """Raised when there's a conflict with existing data."""
    pass


class InternalServerException(PaksaException):
    """Raised when there's an internal server error."""
    pass


# HTTP Exception helpers
def http_exception(
    status_code: int,
    message: str,
    details: Optional[Dict[str, Any]] = None
) -> HTTPException:
    """Create HTTP exception with consistent format."""
    return HTTPException(
        status_code=status_code,
        detail={
            "message": message,
            "details": details or {},
            "error_code": f"HTTP_{status_code}"
        }
    )


def validation_error(message: str, field: str = None) -> HTTPException:
    """Create validation error."""
    details = {"field": field} if field else {}
    return http_exception(status.HTTP_422_UNPROCESSABLE_ENTITY, message, details)


def not_found_error(resource: str, identifier: str = None) -> HTTPException:
    """Create not found error."""
    message = f"{resource} not found"
    if identifier:
        message += f" with identifier: {identifier}"
    return http_exception(status.HTTP_404_NOT_FOUND, message)


def unauthorized_error(message: str = "Authentication required") -> HTTPException:
    """Create unauthorized error."""
    return http_exception(status.HTTP_401_UNAUTHORIZED, message)


def forbidden_error(message: str = "Access forbidden") -> HTTPException:
    """Create forbidden error."""
    return http_exception(status.HTTP_403_FORBIDDEN, message)


def conflict_error(message: str, resource: str = None) -> HTTPException:
    """Create conflict error."""
    details = {"resource": resource} if resource else {}
    return http_exception(status.HTTP_409_CONFLICT, message, details)


def internal_server_error(message: str = "Internal server error") -> HTTPException:
    """Create internal server error."""
    return http_exception(status.HTTP_500_INTERNAL_SERVER_ERROR, message)