"""
Reconciliation Exceptions

This module contains custom exceptions for the account reconciliation feature.
"""
from typing import Optional
from uuid import UUID

from ..exceptions import AccountingException


class ReconciliationException(AccountingException):
    """Base exception for reconciliation-related errors."""
    pass


class ReconciliationNotFoundException(ReconciliationException):
    """Raised when a reconciliation is not found."""
    
    def __init__(self, reconciliation_id: UUID, message: Optional[str] = None):
        self.reconciliation_id = reconciliation_id
        if message is None:
            message = f"Reconciliation with ID {reconciliation_id} not found"
        super().__init__(message)


class ReconciliationItemNotFoundException(ReconciliationException):
    """Raised when a reconciliation item is not found."""
    
    def __init__(self, item_id: UUID, message: Optional[str] = None):
        self.item_id = item_id
        if message is None:
            message = f"Reconciliation item with ID {item_id} not found"
        super().__init__(message)


class InvalidReconciliationStateException(ReconciliationException):
    """Raised when an operation is performed on a reconciliation in an invalid state."""
    
    def __init__(self, message: str):
        super().__init__(message)


class ReconciliationValidationException(ReconciliationException):
    """Raised when reconciliation data fails validation."""
    
    def __init__(self, message: str, errors: Optional[dict] = None):
        self.errors = errors or {}
        super().__init__(message)


class ReconciliationAlreadyCompletedException(ReconciliationException):
    """Raised when trying to modify a completed reconciliation."""
    
    def __init__(self, reconciliation_id: UUID):
        self.reconciliation_id = reconciliation_id
        super().__init__(f"Cannot modify completed reconciliation {reconciliation_id}")


class ReconciliationItemAlreadyMatchedException(ReconciliationException):
    """Raised when trying to modify an already matched reconciliation item."""
    
    def __init__(self, item_id: UUID):
        self.item_id = item_id
        super().__init__(f"Cannot modify already matched reconciliation item {item_id}")


class ReconciliationMismatchException(ReconciliationException):
    """Raised when there's a mismatch in reconciliation data."""
    
    def __init__(self, message: str, details: Optional[dict] = None):
        self.details = details or {}
        super().__init__(message)


class ReconciliationPermissionException(ReconciliationException):
    """Raised when a user doesn't have permission to perform a reconciliation action."""
    
    def __init__(self, user_id: UUID, action: str, reconciliation_id: UUID):
        self.user_id = user_id
        self.action = action
        self.reconciliation_id = reconciliation_id
        super().__init__(
            f"User {user_id} is not authorized to {action} reconciliation {reconciliation_id}"
        )


class ReconciliationLockedException(ReconciliationException):
    """Raised when trying to modify a locked reconciliation."""
    
    def __init__(self, reconciliation_id: UUID, locked_by: UUID):
        self.reconciliation_id = reconciliation_id
        self.locked_by = locked_by
        super().__init__(
            f"Reconciliation {reconciliation_id} is currently locked by user {locked_by}"
        )


class ReconciliationItemLockedException(ReconciliationException):
    """Raised when trying to modify a locked reconciliation item."""
    
    def __init__(self, item_id: UUID, locked_by: UUID):
        self.item_id = item_id
        self.locked_by = locked_by
        super().__init__(
            f"Reconciliation item {item_id} is currently locked by user {locked_by}"
        )


class ReconciliationBalanceMismatchException(ReconciliationException):
    """Raised when the reconciliation balance doesn't match the expected value."""
    
    def __init__(
        self,
        reconciliation_id: UUID,
        expected_balance: float,
        actual_balance: float,
        difference: float
    ):
        self.reconciliation_id = reconciliation_id
        self.expected_balance = expected_balance
        self.actual_balance = actual_balance
        self.difference = difference
        super().__init__(
            f"Reconciliation {reconciliation_id} balance mismatch: "
            f"expected {expected_balance}, got {actual_balance} (difference: {difference})"
        )
