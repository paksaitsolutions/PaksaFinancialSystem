"""
Accounting models aggregator - imports from unified models.
All accounting models are now centralized in app.models.core_models.
"""

# Import all accounting models from unified models
from app.models.core_models import (
    JournalEntry,
    JournalEntryLine,
    JournalEntryStatus,
    ChartOfAccounts,
    Vendor,
    Customer,
    APInvoice,
    ARInvoice,
    APPayment,
    ARPayment
)

# Aliases for backward compatibility
GLAccount = ChartOfAccounts
Invoice = ARInvoice  # Default to AR Invoice
Bill = APInvoice
Payment = ARPayment  # Default to AR Payment

# Keep enums for backward compatibility
from enum import Enum

class AccountType(str, Enum):
    """Types of accounts in the chart of accounts."""
    ASSET = 'asset'
    LIABILITY = 'liability'
    EQUITY = 'equity'
    REVENUE = 'revenue'
    EXPENSE = 'expense'
    GAIN = 'gain'
    LOSS = 'loss'
    TEMPORARY = 'temporary'

class AccountSubType(str, Enum):
    """Subtypes for more detailed account classification."""
    # Asset subtypes
    CURRENT_ASSET = 'current_asset'
    FIXED_ASSET = 'fixed_asset'
    INTANGIBLE_ASSET = 'intangible_asset'
    PREPAID_EXPENSE = 'prepaid_expense'
    INVENTORY = 'inventory'
    RECEIVABLE = 'receivable'
    
    # Liability subtypes
    CURRENT_LIABILITY = 'current_liability'
    LONG_TERM_LIABILITY = 'long_term_liability'
    
    # Equity subtypes
    RETAINED_EARNINGS = 'retained_earnings'
    COMMON_STOCK = 'common_stock'
    PREFERRED_STOCK = 'preferred_stock'
    
    # Revenue/Expense subtypes
    OPERATING_REVENUE = 'operating_revenue'
    OTHER_REVENUE = 'other_revenue'
    COST_OF_GOODS_SOLD = 'cogs'
    OPERATING_EXPENSE = 'operating_expense'
    DEPRECIATION = 'depreciation'
    AMORTIZATION = 'amortization'
    INTEREST = 'interest'
    TAX = 'tax'

class AccountStatus(str, Enum):
    """Status of an account."""
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    CLOSED = 'closed'