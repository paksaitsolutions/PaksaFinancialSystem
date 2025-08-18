class AccountingException(Exception):
    """Base exception for the accounting module."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class AccountNotFoundException(AccountingException):
    """Raised when an account is not found."""
    def __init__(self, account_id: str):
        super().__init__(f"Account with ID '{account_id}' not found.")

class JournalEntryNotFoundException(AccountingException):
    """Raised when a journal entry is not found."""
    def __init__(self, entry_id: str):
        super().__init__(f"Journal entry with ID '{entry_id}' not found.")

class UnbalancedJournalEntryException(AccountingException):
    """Raised when debits do not equal credits in a journal entry."""
    def __init__(self, debit_total: float, credit_total: float):
        super().__init__(f"Journal entry is unbalanced. Debits: {debit_total}, Credits: {credit_total}")

class InvalidJournalEntryPostException(AccountingException):
    """Raised when attempting to post an invalid or already posted journal entry."""
    pass

class InvalidAccountOperationException(AccountingException):
    """Raised for invalid operations on an account, e.g., deleting a system account."""
    pass
