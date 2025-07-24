""
Enums used across the Paksa Financial System models.
"""
from enum import Enum

class BankAccountType(str, Enum):
    """Types of bank accounts."""
    CHECKING = 'checking'
    SAVINGS = 'savings'
    CREDIT_CARD = 'credit_card'
    LOAN = 'loan'
    MONEY_MARKET = 'money_market'
    PAYMENT_PROCESSOR = 'payment_processor'  # e.g., PayPal, Stripe
    OTHER = 'other'


class TransactionStatus(str, Enum):
    """Status of a financial transaction."""
    PENDING = 'pending'  # Awaiting processing
    POSTED = 'posted'    # Successfully processed
    CLEARED = 'cleared'  # Cleared by the bank
    RECONCILED = 'reconciled'  # Reconciled with bank statement
    VOIDED = 'voided'   # Cancelled/voided
    FAILED = 'failed'   # Failed to process
    REVERSED = 'reversed'  # Transaction was reversed
    SCHEDULED = 'scheduled'  # Scheduled for future processing


class CashFlowCategory(str, Enum):
    """Categories for cash flow classification."""
    # Inflows
    SALE = 'sale'                   # Revenue from sales
    PAYMENT_RECEIVED = 'payment_received'  # Customer payments
    INTEREST_INCOME = 'interest_income'
    DIVIDEND_INCOME = 'dividend_income'
    TAX_REFUND = 'tax_refund'
    LOAN_RECEIVED = 'loan_received'
    INVESTMENT_INCOME = 'investment_income'
    OTHER_INCOME = 'other_income'
    
    # Outflows
    SUPPLIERS = 'suppliers'         # Payments to suppliers/vendors
    SALARIES = 'salaries'           # Employee salaries
    RENT = 'rent'                   # Office/space rental
    UTILITIES = 'utilities'         # Electricity, water, internet, etc.
    TAXES = 'taxes'                 # Tax payments
    LOAN_PAYMENT = 'loan_payment'   # Loan principal/interest
    INTEREST_EXPENSE = 'interest_expense'
    EQUIPMENT = 'equipment'         # Equipment purchases
    MARKETING = 'marketing'         # Marketing and advertising
    TRAVEL = 'travel'               # Business travel
    INSURANCE = 'insurance'         # Insurance payments
    PROFESSIONAL_FEES = 'professional_fees'  # Legal, accounting, etc.
    SUBSCRIPTIONS = 'subscriptions'  # Software, memberships
    MAINTENANCE = 'maintenance'     # Repairs and maintenance
    OTHER_EXPENSE = 'other_expense'


class ReconciliationStatus(str, Enum):
    """Status of bank account reconciliation."""
    IN_PROGRESS = 'in_progress'     # Reconciliation in progress
    COMPLETED = 'completed'         # Successfully completed
    OUT_OF_BALANCE = 'out_of_balance'  # Reconciliation doesn't balance
    APPROVED = 'approved'           # Approved by manager
    REJECTED = 'rejected'           # Rejected by manager


class PaymentMethod(str, Enum):
    """Payment methods for transactions."""
    CASH = 'cash'
    CHECK = 'check'
    BANK_TRANSFER = 'bank_transfer'
    CREDIT_CARD = 'credit_card'
    DEBIT_CARD = 'debit_card'
    ACH = 'ach'                     # Automated Clearing House
    WIRE_TRANSFER = 'wire_transfer'
    PAYPAL = 'paypal'
    OTHER = 'other'
