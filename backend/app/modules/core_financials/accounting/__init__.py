"""
Paksa Financial System 
Accounting Module

This module provides core accounting functionality including general ledger,
chart of accounts, journal entries, financial reporting, and account reconciliation.
"""
# Import models
from .models import (
    ChartOfAccounts,
    GLAccount,  # Alias for ChartOfAccounts
    AccountStatus,
    AccountSubType,
    AccountType,
    JournalEntry,
    JournalEntryLine,
    JournalEntryStatus,
)

# Import services (only if they exist)
try:
    from .services.account_service import AccountService
except ImportError:
    AccountService = None

try:
    from .services.journal_entry_service import JournalEntryService
except ImportError:
    JournalEntryService = None

try:
    from .services.account_balance_service import AccountBalanceService
except ImportError:
    AccountBalanceService = None

# Import exceptions (only if they exist)
try:
    from ..exceptions import AccountingException
except ImportError:
    AccountingException = None

try:
    from .exceptions.account_exceptions import (
        AccountNotFoundException,
        DuplicateAccountCodeException,
        InvalidAccountTypeException,
    )
except ImportError:
    AccountNotFoundException = None
    DuplicateAccountCodeException = None
    InvalidAccountTypeException = None

try:
    from .exceptions.journal_entry_exceptions import (
        JournalEntryNotFoundException,
        UnbalancedJournalEntryException,
        InvalidJournalEntryStatusException,
        InvalidJournalEntryDateException,
    )
except ImportError:
    JournalEntryNotFoundException = None
    UnbalancedJournalEntryException = None
    InvalidJournalEntryStatusException = None
    InvalidJournalEntryDateException = None

__all__ = [
    # Module
    'models',
    'schemas',
    'services',
    'exceptions',
    # Models
    'ChartOfAccounts',
    'GLAccount',
    'AccountStatus',
    'AccountSubType',
    'AccountType',
    'JournalEntry',
    'JournalEntryLine',
    'JournalEntryStatus',
    
    # Services
    'AccountService',
    'JournalEntryService',
    'AccountBalanceService',
    
    # Exceptions
    'AccountingException',
    'AccountNotFoundException',
    'DuplicateAccountCodeException',
    'InvalidAccountTypeException',
    'JournalEntryNotFoundException',
    'UnbalancedJournalEntryException',
    'InvalidJournalEntryStatusException',
    'InvalidJournalEntryDateException',
]
