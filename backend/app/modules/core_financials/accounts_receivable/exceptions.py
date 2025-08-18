"""Custom exceptions for the Accounts Receivable module."""

class AccountsReceivableException(Exception):
    """Base exception class for Accounts Receivable module."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class ValidationError(AccountsReceivableException):
    """Raised for validation errors."""
    pass

class BusinessRuleError(AccountsReceivableException):
    """Raised when a business rule is violated."""
    pass

class NotFoundError(AccountsReceivableException):
    """Raised when a resource is not found."""
    pass
