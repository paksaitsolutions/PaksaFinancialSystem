"""
Router utilities for consistent error handling and imports.

This module provides standardized router configuration and error handling
to eliminate duplicate code across API endpoints.
"""
from typing import Any, Dict, Optional, Type, Union
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)

class APIError(Exception):
    """Base API error class."""
    def __init__(self, message: str, status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class NotFoundError(APIError):
    """Resource not found error."""
    def __init__(self, resource: str, identifier: Union[str, int]):
        super().__init__(
            message=f"{resource} not found",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"resource": resource, "identifier": str(identifier)}
        )

class ValidationError(APIError):
    """Validation error."""
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"field": field} if field else {}
        )

class PermissionError(APIError):
    """Permission denied error."""
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN
        )

class ConflictError(APIError):
    """Resource conflict error."""
    def __init__(self, message: str, resource: Optional[str] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            details={"resource": resource} if resource else {}
        )

def handle_database_error(error: Exception) -> HTTPException:
    """Handle database errors consistently."""
    if isinstance(error, IntegrityError):
        logger.error(f"Database integrity error: {error}")
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Resource conflict - this operation violates data constraints"
        )
    elif isinstance(error, SQLAlchemyError):
        logger.error(f"Database error: {error}")
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed"
        )
    else:
        logger.error(f"Unexpected error: {error}")
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

def create_error_response(error: APIError) -> JSONResponse:
    """Create standardized error response."""
    return JSONResponse(
        status_code=error.status_code,
        content={
            "error": True,
            "message": error.message,
            "details": error.details,
            "status_code": error.status_code
        }
    )

def create_success_response(
    data: Any = None, 
    message: str = "Success", 
    status_code: int = 200
) -> Dict[str, Any]:
    """Create standardized success response."""
    response = {
        "error": False,
        "message": message,
        "status_code": status_code
    }
    
    if data is not None:
        response["data"] = data
    
    return response

def validate_company_access(user_company_id: str, resource_company_id: str) -> None:
    """Validate user has access to company resource."""
    if user_company_id != resource_company_id:
        raise PermissionError("Access denied to this company's resources")

def require_permission(user_permissions: list, required_permission: str) -> None:
    """Require specific permission."""
    if required_permission not in user_permissions:
        raise PermissionError(f"Permission required: {required_permission}")

# Common HTTP status responses
HTTP_200_OK = {"status_code": 200, "description": "Success"}
HTTP_201_CREATED = {"status_code": 201, "description": "Created"}
HTTP_204_NO_CONTENT = {"status_code": 204, "description": "No Content"}
HTTP_400_BAD_REQUEST = {"status_code": 400, "description": "Bad Request"}
HTTP_401_UNAUTHORIZED = {"status_code": 401, "description": "Unauthorized"}
HTTP_403_FORBIDDEN = {"status_code": 403, "description": "Forbidden"}
HTTP_404_NOT_FOUND = {"status_code": 404, "description": "Not Found"}
HTTP_409_CONFLICT = {"status_code": 409, "description": "Conflict"}
HTTP_422_UNPROCESSABLE_ENTITY = {"status_code": 422, "description": "Validation Error"}
HTTP_500_INTERNAL_SERVER_ERROR = {"status_code": 500, "description": "Internal Server Error"}

# Standard response schemas
STANDARD_RESPONSES = {
    400: HTTP_400_BAD_REQUEST,
    401: HTTP_401_UNAUTHORIZED,
    403: HTTP_403_FORBIDDEN,
    404: HTTP_404_NOT_FOUND,
    409: HTTP_409_CONFLICT,
    422: HTTP_422_UNPROCESSABLE_ENTITY,
    500: HTTP_500_INTERNAL_SERVER_ERROR
}