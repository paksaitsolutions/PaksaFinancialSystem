"""
Custom exceptions for the application.
"""
from fastapi import status
from fastapi.exceptions import HTTPException


class AppException(HTTPException):
    """Base exception for all application exceptions."""
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail: str = "An unexpected error occurred"
    
    def __init__(
        self, 
        detail: str = None, 
        status_code: int = None, 
        **kwargs
    ) -> None:
        if status_code is not None:
            self.status_code = status_code
        if detail is not None:
            self.detail = detail
        super().__init__(
            status_code=self.status_code, 
            detail=self.detail,
            **kwargs
        )


class BadRequestException(AppException):
    """Raised when the request is malformed or invalid."""
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Invalid request"


class UnauthorizedException(AppException):
    """Raised when authentication is required but not provided or invalid."""
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Not authenticated"


class ForbiddenException(AppException):
    """Raised when the user doesn't have permission to access a resource."""
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Permission denied"


class NotFoundException(AppException):
    """Raised when a requested resource is not found."""
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Resource not found"


class ConflictException(AppException):
    """Raised when a resource conflict occurs."""
    status_code = status.HTTP_409_CONFLICT
    detail = "Resource conflict"


class ValidationException(AppException):
    """Raised when validation fails."""
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = "Validation error"


class RateLimitException(AppException):
    """Raised when rate limit is exceeded."""
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    detail = "Rate limit exceeded"


class ServiceUnavailableException(AppException):
    """Raised when a required service is unavailable."""
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    detail = "Service unavailable"


# Authentication exceptions
class CredentialsException(UnauthorizedException):
    """Raised when authentication credentials are invalid."""
    detail = "Could not validate credentials"


class InactiveUserException(ForbiddenException):
    """Raised when a user account is inactive."""
    detail = "Inactive user"


class InsufficientPermissionsException(ForbiddenException):
    """Raised when a user doesn't have required permissions."""
    detail = "Insufficient permissions"


class InvalidTokenException(UnauthorizedException):
    """Raised when an invalid token is provided."""
    detail = "Invalid token"


class TokenExpiredException(UnauthorizedException):
    """Raised when a token has expired."""
    detail = "Token has expired"


# Business logic exceptions
class BusinessRuleException(BadRequestException):
    """Raised when a business rule is violated."""
    detail = "Business rule violation"


class DuplicateEntryException(ConflictException):
    """Raised when a duplicate entry is detected."""
    detail = "Duplicate entry"


class StateTransitionException(BadRequestException):
    """Raised when an invalid state transition is attempted."""
    detail = "Invalid state transition"


class InsufficientFundsException(BadRequestException):
    """Raised when there are insufficient funds for an operation."""
    status_code = status.HTTP_402_PAYMENT_REQUIRED
    detail = "Insufficient funds"


# External service exceptions
class ExternalServiceException(AppException):
    """Base class for external service errors."""
    status_code = status.HTTP_502_BAD_GATEWAY
    detail = "External service error"


class PaymentGatewayException(ExternalServiceException):
    """Raised when there's an error with a payment gateway."""
    detail = "Payment gateway error"


class EmailServiceException(ExternalServiceException):
    """Raised when there's an error sending an email."""
    detail = "Email service error"
