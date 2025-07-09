"""
Cash Management Module - Exceptions
"""
from typing import Optional, List, Dict, Any
from uuid import UUID


class CashManagementError(Exception):
    """Base exception for cash management module."""
    def __init__(self, message: str, code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.code = code or "cash_management_error"
        self.details = details or {}
        super().__init__(self.message)


class BankAccountNotFound(CashManagementError):
    """Raised when a bank account is not found."""
    def __init__(self, account_id: UUID):
        self.account_id = account_id
        super().__init__(
            f"Bank account with ID {account_id} not found",
            code="bank_account_not_found",
            details={"account_id": str(account_id)}
        )


class BankAccountAlreadyExists(CashManagementError):
    """Raised when trying to create a duplicate bank account."""
    def __init__(self, bank_name: str, account_number: str):
        self.bank_name = bank_name
        self.account_number = account_number
        super().__init__(
            f"Bank account with number {account_number} already exists at {bank_name}",
            code="bank_account_exists",
            details={
                "bank_name": bank_name,
                "account_number": account_number
            }
        )


class InvalidBankAccountOperation(CashManagementError):
    """Raised when an invalid operation is performed on a bank account."""
    def __init__(self, account_id: UUID, operation: str, reason: str):
        self.account_id = account_id
        self.operation = operation
        super().__init__(
            f"Cannot {operation} bank account {account_id}: {reason}",
            code=f"invalid_operation_{operation.lower()}",
            details={
                "account_id": str(account_id),
                "operation": operation,
                "reason": reason
            }
        )


class TransactionNotFound(CashManagementError):
    """Raised when a transaction is not found."""
    def __init__(self, transaction_id: UUID):
        self.transaction_id = transaction_id
        super().__init__(
            f"Transaction with ID {transaction_id} not found",
            code="transaction_not_found",
            details={"transaction_id": str(transaction_id)}
        )


class InvalidTransactionOperation(CashManagementError):
    """Raised when an invalid operation is performed on a transaction."""
    def __init__(self, transaction_id: UUID, operation: str, reason: str):
        self.transaction_id = transaction_id
        self.operation = operation
        super().__init__(
            f"Cannot {operation} transaction {transaction_id}: {reason}",
            code=f"invalid_transaction_operation",
            details={
                "transaction_id": str(transaction_id),
                "operation": operation,
                "reason": reason
            }
        )


class ReconciliationError(CashManagementError):
    """Raised when there's an error with bank reconciliation."""
    def __init__(self, reconciliation_id: UUID, message: str, details: Optional[Dict[str, Any]] = None):
        self.reconciliation_id = reconciliation_id
        super().__init__(
            f"Reconciliation error for {reconciliation_id}: {message}",
            code="reconciliation_error",
            details={"reconciliation_id": str(reconciliation_id), **(details or {})}
        )


class ReconciliationNotFound(CashManagementError):
    """Raised when a reconciliation is not found."""
    def __init__(self, reconciliation_id: UUID):
        self.reconciliation_id = reconciliation_id
        super().__init__(
            f"Reconciliation with ID {reconciliation_id} not found",
            code="reconciliation_not_found",
            details={"reconciliation_id": str(reconciliation_id)}
        )


class TransactionCategoryNotFound(CashManagementError):
    """Raised when a transaction category is not found."""
    def __init__(self, category_id: UUID):
        self.category_id = category_id
        super().__init__(
            f"Transaction category with ID {category_id} not found",
            code="transaction_category_not_found",
            details={"category_id": str(category_id)}
        )


class TransactionCategoryInUse(CashManagementError):
    """Raised when trying to delete a category that's in use."""
    def __init__(self, category_id: UUID, transaction_count: int):
        self.category_id = category_id
        self.transaction_count = transaction_count
        super().__init__(
            f"Cannot delete category {category_id} as it is used by {transaction_count} transactions",
            code="category_in_use",
            details={
                "category_id": str(category_id),
                "transaction_count": transaction_count
            }
        )


class BankIntegrationError(CashManagementError):
    """Raised when there's an error with bank integration."""
    def __init__(self, integration_id: UUID, message: str, details: Optional[Dict[str, Any]] = None):
        self.integration_id = integration_id
        super().__init__(
            f"Bank integration error for {integration_id}: {message}",
            code="bank_integration_error",
            details={"integration_id": str(integration_id), **(details or {})}
        )


class BankIntegrationNotFound(CashManagementError):
    """Raised when a bank integration is not found."""
    def __init__(self, integration_id: UUID):
        self.integration_id = integration_id
        super().__init__(
            f"Bank integration with ID {integration_id} not found",
            code="bank_integration_not_found",
            details={"integration_id": str(integration_id)}
        )


class BankSyncError(CashManagementError):
    """Raised when there's an error syncing with a bank."""
    def __init__(self, account_id: UUID, message: str, details: Optional[Dict[str, Any]] = None):
        self.account_id = account_id
        super().__init__(
            f"Bank sync error for account {account_id}: {message}",
            code="bank_sync_error",
            details={"account_id": str(account_id), **(details or {})}
        )


class InsufficientFundsError(CashManagementError):
    """Raised when there are insufficient funds for a transaction."""
    def __init__(self, account_id: UUID, available_balance: Decimal, requested_amount: Decimal):
        self.account_id = account_id
        self.available_balance = available_balance
        self.requested_amount = requested_amount
        super().__init__(
            f"Insufficient funds in account {account_id}. Available: {available_balance}, Requested: {requested_amount}",
            code="insufficient_funds",
            details={
                "account_id": str(account_id),
                "available_balance": float(available_balance),
                "requested_amount": float(requested_amount),
                "shortfall": float(requested_amount - available_balance)
            }
        )


class InvalidTransactionAmount(CashManagementError):
    """Raised when a transaction amount is invalid."""
    def __init__(self, amount: Decimal, reason: str):
        self.amount = amount
        super().__init__(
            f"Invalid transaction amount {amount}: {reason}",
            code="invalid_transaction_amount",
            details={"amount": float(amount) if amount is not None else None, "reason": reason}
        )


class TransactionImportError(CashManagementError):
    """Raised when there's an error importing transactions."""
    def __init__(self, account_id: UUID, message: str, errors: Optional[List[Dict[str, Any]]] = None):
        self.account_id = account_id
        self.errors = errors or []
        super().__init__(
            f"Error importing transactions for account {account_id}: {message}",
            code="transaction_import_error",
            details={"account_id": str(account_id), "errors": self.errors}
        )


class StatementProcessingError(CashManagementError):
    """Raised when there's an error processing a bank statement."""
    def __init__(self, statement_id: UUID, message: str, details: Optional[Dict[str, Any]] = None):
        self.statement_id = statement_id
        super().__init__(
            f"Error processing statement {statement_id}: {message}",
            code="statement_processing_error",
            details={"statement_id": str(statement_id), **(details or {})}
        )


class StatementNotFound(CashManagementError):
    """Raised when a bank statement is not found."""
    def __init__(self, statement_id: UUID):
        self.statement_id = statement_id
        super().__init__(
            f"Bank statement with ID {statement_id} not found",
            code="statement_not_found",
            details={"statement_id": str(statement_id)}
        )


class InvalidDateRange(CashManagementError):
    """Raised when an invalid date range is provided."""
    def __init__(self, start_date: str, end_date: str, message: str):
        self.start_date = start_date
        self.end_date = end_date
        super().__init__(
            f"Invalid date range {start_date} to {end_date}: {message}",
            code="invalid_date_range",
            details={"start_date": start_date, "end_date": end_date, "message": message}
        )
