"""
Centralized Error Handling Middleware
Provides consistent error responses across all API endpoints.

Features:
- Standardized error response format
- Error logging
- Error code mapping
- User-friendly error messages
- Stack trace in development mode
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from typing import Union, Dict, Any
import logging
import traceback

from app.core.config import settings

logger = logging.getLogger(__name__)


class ErrorResponse:
    """Standardized error response structure."""
    
    def __init__(
        self,
        error_code: str,
        message: str,
        details: Union[str, Dict[str, Any], None] = None,
        status_code: int = 500
    ):
        self.error_code = error_code
        self.message = message
        self.details = details
        self.status_code = status_code
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON response."""
        response = {
            "status": "error",
            "message": self.message,
            "error": {
                "code": self.error_code,
                "message": self.message
            }
        }
        
        if self.details:
            response["error"]["details"] = self.details
        
        return response


# Error code mappings
ERROR_CODES = {
    # Authentication & Authorization (1xxx)
    "AUTH_001": "Invalid credentials",
    "AUTH_002": "Token expired",
    "AUTH_003": "Invalid token",
    "AUTH_004": "Insufficient permissions",
    "AUTH_005": "Account disabled",
    "AUTH_006": "MFA required",
    
    # Validation Errors (2xxx)
    "VAL_001": "Invalid input data",
    "VAL_002": "Missing required field",
    "VAL_003": "Invalid format",
    "VAL_004": "Value out of range",
    
    # Database Errors (3xxx)
    "DB_001": "Database connection error",
    "DB_002": "Record not found",
    "DB_003": "Duplicate record",
    "DB_004": "Foreign key constraint violation",
    "DB_005": "Database integrity error",
    
    # Business Logic Errors (4xxx)
    "BIZ_001": "Invalid operation",
    "BIZ_002": "Operation not allowed",
    "BIZ_003": "Insufficient balance",
    "BIZ_004": "Period closed",
    "BIZ_005": "Already processed",
    
    # Resource Errors (5xxx)
    "RES_001": "Resource not found",
    "RES_002": "Resource already exists",
    "RES_003": "Resource locked",
    
    # System Errors (9xxx)
    "SYS_001": "Internal server error",
    "SYS_002": "Service unavailable",
    "SYS_003": "External service error",
}


def get_error_message(error_code: str) -> str:
    """Get user-friendly error message for error code."""
    return ERROR_CODES.get(error_code, "An unexpected error occurred")


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle HTTP exceptions."""
    
    # Map HTTP status codes to error codes
    error_code_map = {
        401: "AUTH_003",
        403: "AUTH_004",
        404: "RES_001",
        409: "RES_002",
        422: "VAL_001",
        500: "SYS_001",
        503: "SYS_002",
    }
    
    error_code = error_code_map.get(exc.status_code, "SYS_001")
    
    error_response = ErrorResponse(
        error_code=error_code,
        message=str(exc.detail) if exc.detail else get_error_message(error_code),
        status_code=exc.status_code
    )
    
    # Log error
    logger.error(
        f"HTTP Exception: {error_code} - {exc.detail}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "status_code": exc.status_code
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.to_dict()
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle validation errors."""
    
    # Extract validation errors
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"][1:])  # Skip 'body'
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })
    
    error_response = ErrorResponse(
        error_code="VAL_001",
        message="Validation error",
        details={"validation_errors": errors},
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )
    
    # Log validation error
    logger.warning(
        f"Validation Error: {len(errors)} field(s)",
        extra={
            "path": request.url.path,
            "method": request.method,
            "errors": errors
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response.to_dict()
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Handle SQLAlchemy database errors."""
    
    # Determine error code based on exception type
    if isinstance(exc, IntegrityError):
        if "duplicate key" in str(exc).lower():
            error_code = "DB_003"
            status_code = status.HTTP_409_CONFLICT
        elif "foreign key" in str(exc).lower():
            error_code = "DB_004"
            status_code = status.HTTP_400_BAD_REQUEST
        else:
            error_code = "DB_005"
            status_code = status.HTTP_400_BAD_REQUEST
    else:
        error_code = "DB_001"
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    
    error_response = ErrorResponse(
        error_code=error_code,
        message=get_error_message(error_code),
        details=str(exc) if settings.DEBUG else None,
        status_code=status_code
    )
    
    # Log database error
    logger.error(
        f"Database Error: {error_code}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "exception": str(exc)
        },
        exc_info=True
    )
    
    return JSONResponse(
        status_code=status_code,
        content=error_response.to_dict()
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all other exceptions."""
    
    error_response = ErrorResponse(
        error_code="SYS_001",
        message="An unexpected error occurred",
        details={
            "type": type(exc).__name__,
            "message": str(exc),
            "traceback": traceback.format_exc() if settings.DEBUG else None
        },
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    
    # Log unexpected error
    logger.critical(
        f"Unexpected Error: {type(exc).__name__}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "exception": str(exc)
        },
        exc_info=True
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.to_dict()
    )


def setup_error_handlers(app):
    """Setup all error handlers for the FastAPI application."""
    
    # HTTP exceptions
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    
    # Validation errors
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    
    # Database errors
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    
    # General exceptions
    app.add_exception_handler(Exception, general_exception_handler)
    
    logger.info("Error handlers configured successfully")


# Custom exception classes for business logic
class BusinessLogicError(Exception):
    """Base class for business logic errors."""
    
    def __init__(self, error_code: str, message: str = None, details: Any = None):
        self.error_code = error_code
        self.message = message or get_error_message(error_code)
        self.details = details
        super().__init__(self.message)


class InsufficientBalanceError(BusinessLogicError):
    """Raised when account has insufficient balance."""
    
    def __init__(self, account: str, required: float, available: float):
        super().__init__(
            error_code="BIZ_003",
            message=f"Insufficient balance in account {account}",
            details={
                "account": account,
                "required": required,
                "available": available
            }
        )


class PeriodClosedError(BusinessLogicError):
    """Raised when trying to post to a closed period."""
    
    def __init__(self, period: str):
        super().__init__(
            error_code="BIZ_004",
            message=f"Period {period} is closed",
            details={"period": period}
        )


class AlreadyProcessedError(BusinessLogicError):
    """Raised when trying to process an already processed transaction."""
    
    def __init__(self, transaction_id: str):
        super().__init__(
            error_code="BIZ_005",
            message=f"Transaction {transaction_id} has already been processed",
            details={"transaction_id": transaction_id}
        )


# Business logic exception handler
async def business_logic_exception_handler(request: Request, exc: BusinessLogicError) -> JSONResponse:
    """Handle business logic errors."""
    
    error_response = ErrorResponse(
        error_code=exc.error_code,
        message=exc.message,
        details=exc.details,
        status_code=status.HTTP_400_BAD_REQUEST
    )
    
    logger.warning(
        f"Business Logic Error: {exc.error_code}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "details": exc.details
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=error_response.to_dict()
    )
