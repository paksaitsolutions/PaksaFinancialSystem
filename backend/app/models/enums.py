"""
Enum definitions for the application.
"""
import enum

class VendorStatus(str, enum.Enum):
    """Status of a vendor."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    HOLD = "hold"
    PENDING_APPROVAL = "pending_approval"
    BLOCKED = "blocked"

class PaymentTerms(str, enum.Enum):
    """Payment terms for vendors and customers."""
    NET_15 = "net_15"
    NET_30 = "net_30"
    NET_45 = "net_45"
    NET_60 = "net_60"
    DUE_ON_RECEIPT = "due_on_receipt"
    PREPAID = "prepaid"
    COD = "cod"  # Cash on delivery
    CUSTOM = "custom"

class InvoiceStatus(str, enum.Enum):
    """Status of an invoice."""
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    PAID = "paid"
    PARTIALLY_PAID = "partially_paid"
    VOIDED = "voided"
    CANCELLED = "cancelled"
    OVERDUE = "overdue"

class PaymentStatus(str, enum.Enum):
    """Status of a payment."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    VOIDED = "voided"
    REFUNDED = "refunded"

class PaymentMethod(str, enum.Enum):
    """Payment methods."""
    CHECK = "check"
    ACH = "ach"
    WIRE = "wire"
    CREDIT_CARD = "credit_card"
    CASH = "cash"
    OTHER = "other"

class CreditMemoStatus(str, enum.Enum):
    """Status of a credit memo."""
    ACTIVE = "active"
    FULLY_APPLIED = "fully_applied"
    EXPIRED = "expired"
    VOIDED = "voided"

class Form1099Type(str, enum.Enum):
    """Type of 1099 form."""
    MISC = "1099-MISC"
    NEC = "1099-NEC"
    INT = "1099-INT"
    DIV = "1099-DIV"

class Form1099Status(str, enum.Enum):
    """Status of a 1099 form."""
    DRAFT = "draft"
    READY = "ready"
    FILED = "filed"
    CORRECTED = "corrected"
    VOIDED = "voided"

class CustomerStatus(str, enum.Enum):
    """Status of a customer."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    HOLD = "hold"
    PENDING_APPROVAL = "pending_approval"
    BLOCKED = "blocked"