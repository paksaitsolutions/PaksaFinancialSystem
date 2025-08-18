"""
Exceptions related to account balance operations.
"""
from uuid import UUID

from ..exceptions import AccountingException


class AccountBalanceException(AccountingException):
    """Base exception for account balance related errors."""
    pass


class InvalidDateRangeException(AccountBalanceException):
    """Raised when an invalid date range is provided."""
    
    def __init__(self, message: str = "Invalid date range"):
        super().__init__(message)


class PeriodAlreadyClosedException(AccountBalanceException):
    """Raised when trying to close a period that's already closed."""
    
    def __init__(self, period_end: str):
        super().__init__(f"Period ending {period_end} is already closed")


class PeriodNotClosedException(AccountBalanceException):
    """Raised when trying to perform an operation that requires a closed period."""
    
    def __init__(self, period_end: str):
        super().__init__(f"Period ending {period_end} is not closed")


class AccountBalanceNotFoundException(AccountBalanceException):
    """Raised when an account balance record is not found."""
    
    def __init__(self, balance_id: UUID):
        super().__init__(f"Account balance with ID {balance_id} not found")


class InvalidBalancePeriodException(AccountBalanceException):
    """Raised when there's an issue with balance period dates."""
    
    def __init__(self, message: str):
        super().__init__(f"Invalid balance period: {message}")
