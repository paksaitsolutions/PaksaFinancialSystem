"""
Constants for the Accounts Receivable module.
"""
from enum import Enum

# Default settings
DEFAULT_TERMS_DAYS = 30
DEFAULT_TAX_RATE = 0.0  # Default tax rate if not specified
DEFAULT_CURRENCY = "USD"

# Invoice settings
INVOICE_NUMBER_PREFIX = "INV"
INVOICE_REFUND_WINDOW_DAYS = 30

# Payment settings
PAYMENT_NUMBER_PREFIX = "PAY"
PAYMENT_METHODS = ["credit_card", "bank_transfer", "check", "cash", "other"]
PAYMENT_STATUSES = ["pending", "completed", "failed", "refunded", "partially_refunded"]

# Credit Note settings
CREDIT_NOTE_PREFIX = "CN"
CREDIT_NOTE_VALID_DAYS = 365  # How long a credit note is valid

# Aging buckets in days
AGING_BUCKETS = [0, 30, 60, 90, 120]  # Days for aging reports

# Email templates
class EmailTemplates(str, Enum):
    INVOICE_SENT = "invoice_sent"
    PAYMENT_RECEIVED = "payment_received"
    PAYMENT_OVERDUE = "payment_overdue"
    CREDIT_NOTE_ISSUED = "credit_note_issued"

# Notification messages
class NotificationMessages(str, Enum):
    INVOICE_CREATED = "Invoice {invoice_number} has been created"
    INVOICE_SENT = "Invoice {invoice_number} has been sent to {customer_email}"
    INVOICE_PAID = "Invoice {invoice_number} has been paid in full"
    PAYMENT_RECEIVED = "Payment of {amount} received for invoice {invoice_number}"
    PAYMENT_OVERDUE = "Invoice {invoice_number} is now {days_overdue} days overdue"
    CREDIT_NOTE_ISSUED = "Credit note {credit_note_number} has been issued"

# Error messages
class ErrorMessages(str, Enum):
    INVOICE_NOT_FOUND = "Invoice not found"
    PAYMENT_NOT_FOUND = "Payment not found"
    CREDIT_NOTE_NOT_FOUND = "Credit note not found"
    CUSTOMER_NOT_FOUND = "Customer not found"
    INVOICE_ALREADY_PAID = "Invoice has already been paid"
    INVOICE_OVERDUE = "Invoice is overdue"
    INVALID_PAYMENT_AMOUNT = "Payment amount exceeds invoice balance"
    CREDIT_NOTE_EXPIRED = "Credit note has expired"
    INSUFFICIENT_CREDIT = "Insufficient credit available"

# Validation messages
class ValidationMessages(str, Enum):
    INVALID_INVOICE_STATUS = "Invalid invoice status transition"
    INVALID_PAYMENT_METHOD = "Invalid payment method"
    INVALID_TAX_RATE = "Tax rate must be between 0 and 100"
    INVALID_DISCOUNT = "Discount must be between 0 and 100"
    INVALID_QUANTITY = "Quantity must be greater than 0"
    INVALID_AMOUNT = "Amount must be greater than 0"

# Report names
class ReportNames(str, Enum):
    AGING_SUMMARY = "accounts_aging_summary"
    REVENUE_BY_CUSTOMER = "revenue_by_customer"
    PAYMENT_HISTORY = "payment_history"
    TAX_REPORT = "tax_report"
    COLLECTION_EFFICIENCY = "collection_efficiency"

# Export formats
class ExportFormats(str, Enum):
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    JSON = "json"
