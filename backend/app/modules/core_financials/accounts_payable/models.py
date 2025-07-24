import enum  # Python standard library enum
from sqlalchemy import (
    Column, Integer, String, Text, Numeric, Date, DateTime, Boolean, ForeignKey, Index, 
    Enum as SQLEnum, JSON as JSONB, func, CheckConstraint, UniqueConstraint, Table, Float
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB as pgJSONB
from sqlalchemy.ext.declarative import declared_attr
from datetime import datetime, timedelta
from enum import Enum as PyEnum
from typing import Optional, List, Dict, Any, Union

# Import base model
from app.core.base import Base

# Define enums BEFORE you use them in SQLAlchemy columns
class VendorCategory(str, enum.Enum):
    SUPPLIER = "supplier"
    CONTRACTOR = "contractor"
    SERVICE_PROVIDER = "service_provider"
    CONSULTANT = "consultant"
    UTILITY = "utility"
    GOVERNMENT = "government"
    OTHER = "other"

class VendorStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    BLACKLISTED = "blacklisted"
    PENDING_APPROVAL = "pending_approval"

class PaymentTerms(str, enum.Enum):
    NET_15 = "net15"
    NET_30 = "net30"
    NET_45 = "net45"
    NET_60 = "net60"
    NET_90 = "net90"
    DUE_ON_RECEIPT = "due_on_receipt"
    COD = "cod"
    PREPAID = "prepaid"

class VendorRiskLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ApprovalStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    UNDER_REVIEW = "under_review"

class InvoiceStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    VOID = "void"

# Now define the Vendor model
class PaymentTerm(Base):
    """Payment terms that can be assigned to vendors"""
    
    __tablename__ = "payment_terms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text)
    
    # Net days (e.g., Net 30, Net 60)
    net_days = Column(Integer, default=0, comment="Number of days until payment is due")
    
    # Discount terms (e.g., 2/10 Net 30)
    discount_days = Column(Integer, default=0, comment="Number of days discount is available")
    discount_percent = Column(Numeric(5, 2), default=0, comment="Discount percentage (e.g., 2.00 for 2%)")
    
    # Recurring terms (e.g., 15th of month, end of month + 15 days)
    day_of_month = Column(Integer, comment="Specific day of month payment is due (1-31)")
    end_of_month = Column(Boolean, default=False, comment="Payment due at end of month")
    days_after_eom = Column(Integer, default=0, comment="Days after end of month payment is due")
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    updated_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    
    # Relationships
    vendors = relationship("Vendor", back_populates="payment_terms_rel")
    
    # Indexes
    __table_args__ = (
        Index('idx_payment_term_active', 'is_active'),
    )
    
    def calculate_due_date(self, invoice_date: Optional[datetime] = None) -> datetime:
        """Calculate the due date based on the payment terms"""
        if invoice_date is None:
            invoice_date = datetime.now()
            
        due_date = invoice_date
        
        if self.net_days > 0:
            due_date = invoice_date + timedelta(days=self.net_days)
        
        if self.day_of_month:
            # Set to specific day of month, same or next month
            if invoice_date.day > self.day_of_month:
                # If current day is past the due day, go to next month
                if invoice_date.month == 12:
                    due_date = datetime(invoice_date.year + 1, 1, self.day_of_month)
                else:
                    due_date = datetime(invoice_date.year, invoice_date.month + 1, self.day_of_month)
            else:
                due_date = datetime(invoice_date.year, invoice_date.month, self.day_of_month)
        
        if self.end_of_month:
            # Set to last day of current month
            if invoice_date.month == 12:
                due_date = datetime(invoice_date.year + 1, 1, 1) - timedelta(days=1)
            else:
                due_date = datetime(invoice_date.year, invoice_date.month + 1, 1) - timedelta(days=1)
            
            # Add additional days if specified
            if self.days_after_eom > 0:
                due_date += timedelta(days=self.days_after_eom)
        
        return due_date
    
    def calculate_discount_date(self, invoice_date: Optional[datetime] = None) -> Optional[datetime]:
        """Calculate the last date the discount is available"""
        if not self.discount_days or not self.discount_percent:
            return None
            
        if invoice_date is None:
            invoice_date = datetime.now()
            
        return invoice_date + timedelta(days=self.discount_days)
    
    def get_discount_amount(self, amount: Union[int, float, Decimal]) -> Decimal:
        """Calculate the discount amount for a given total"""
        if not self.discount_percent:
            return Decimal('0.00')
            
        return (Decimal(str(amount)) * Decimal(str(self.discount_percent / 100))).quantize(Decimal('0.01'))


class Vendor(Base):
    __tablename__ = "ap_vendors"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    legal_name = Column(String(255))
    category = Column(SQLEnum(VendorCategory, name="vendor_category_enum"), nullable=False)
    
    # Contact Information
    contact_person = Column(String(255))
    website = Column(String(255))
    email = Column(String(255), index=True)
    phone = Column(String(50))
    fax = Column(String(50))
    
    # Primary Contact
    primary_contact_name = Column(String(100))
    primary_contact_title = Column(String(100))
    primary_contact_email = Column(String(100), index=True)
    primary_contact_phone = Column(String(50))
    primary_contact_mobile = Column(String(50))
    
    # Billing Address
    billing_address_line1 = Column(String(255))
    billing_address_line2 = Column(String(255))
    billing_city = Column(String(100))
    billing_state = Column(String(100))
    billing_postal_code = Column(String(20))
    billing_country = Column(String(100))
    
    # Shipping Address (if different)
    shipping_address_same = Column(Boolean, default=True)
    shipping_contact_name = Column(String(100))
    shipping_contact_phone = Column(String(50))
    shipping_address_line1 = Column(String(255))
    shipping_address_line2 = Column(String(255))
    shipping_city = Column(String(100))
    shipping_state = Column(String(100))
    shipping_postal_code = Column(String(20))
    shipping_country = Column(String(100))
    shipping_instructions = Column(Text, comment="Special shipping instructions")
    
    # Payment Information
    payment_terms_id = Column(Integer, ForeignKey("payment_terms.id", ondelete="SET NULL"), index=True)
    preferred_payment_method = Column(String(50), comment="e.g., Check, ACH, Wire, Credit Card")
    payment_method_reference = Column(String(100), comment="Reference for payment method")
    
    # Bank Account Information
    bank_name = Column(String(100))
    bank_branch = Column(String(100))
    bank_account_number = Column(String(50))
    bank_account_name = Column(String(255))
    bank_routing_number = Column(String(50))
    bank_swift_code = Column(String(50))
    iban = Column(String(50))
    
    # Credit and Terms
    credit_limit = Column(Numeric(15, 2), default=0)
    current_balance = Column(Numeric(15, 2), default=0)
    credit_hold = Column(Boolean, default=False, index=True)
    credit_rating = Column(String(20), index=True, comment="Internal credit rating")
    credit_terms = Column(String(100), comment="Custom credit terms")
    
    # Status and Categories
    status = Column(String(20), default='active', index=True)  # active, inactive, on-hold, blacklisted
    vendor_type = Column(String(50), index=True, comment="e.g., Supplier, Service Provider, Consultant")
    vendor_category = Column(String(50), index=True, comment="e.g., Raw Materials, Services, Equipment")
    
    # Additional Information
    lead_time_days = Column(Integer, comment="Standard lead time in days")
    minimum_order_value = Column(Numeric(15, 2), comment="Minimum order value required")
    preferred_currency = Column(String(3), default='USD')
    preferred_language = Column(String(10), default='en')
    
    # Custom Fields and Attachments
    custom_fields = Column(JSONB, comment="Flexible schema for additional vendor-specific fields")
    attachments = Column(JSONB, comment="References to attached documents")
    
    # Internal Notes
    internal_notes = Column(Text, comment="Internal notes about the vendor")
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    updated_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    
    # Relationships
    invoices = relationship("Invoice", back_populates="vendor", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="vendor", cascade="all, delete-orphan")
    contracts = relationship("VendorContract", back_populates="vendor", cascade="all, delete-orphan")
    evaluations = relationship("VendorEvaluation", back_populates="vendor", cascade="all, delete-orphan")
    payment_terms_rel = relationship("PaymentTerm", back_populates="vendors")
    
    # Indexes
    __table_args__ = (
        Index('idx_vendor_name', 'legal_name', 'display_name'),
        Index('idx_vendor_tax_info', 'tax_id', 'vat_number'),
        Index('idx_vendor_status', 'status'),
        Index('idx_vendor_type_category', 'vendor_type', 'vendor_category'),
        Index('idx_vendor_contact_info', 'email', 'phone'),
        Index('idx_vendor_credit', 'credit_hold', 'credit_rating')
    )

    @property
    def outstanding_balance(self):
        return sum(invoice.balance_due for invoice in self.invoices if invoice.balance_due > 0)

    @property
    def total_spent_ytd(self):
        from datetime import datetime
        current_year = datetime.now().year
        return sum(
            invoice.total_amount for invoice in self.invoices 
            if invoice.invoice_date.year == current_year and invoice.status == InvoiceStatus.PAID
        )


class Invoice(Base):
    """AP Invoice model for tracking vendor invoices"""
    
    __tablename__ = "ap_invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    reference_number = Column(String(100))
    vendor_id = Column(Integer, ForeignKey("ap_vendors.id", ondelete="CASCADE"), nullable=False, index=True)
    invoice_date = Column(Date, nullable=False, index=True)
    due_date = Column(Date, nullable=False, index=True)
    posting_date = Column(Date, default=func.current_date())
    subtotal = Column(Numeric(15, 2), nullable=False, default=0)
    tax_amount = Column(Numeric(15, 2), default=0)
    discount_amount = Column(Numeric(15, 2), default=0)
    total_amount = Column(Numeric(15, 2), nullable=False, default=0)
    paid_amount = Column(Numeric(15, 2), default=0)
    balance_due = Column(Numeric(15, 2), default=0)
    status = Column(SQLEnum(InvoiceStatus, name="invoice_status_enum"), default=InvoiceStatus.DRAFT)
    approval_status = Column(SQLEnum(ApprovalStatus, name="invoice_approval_status_enum"), default=ApprovalStatus.PENDING)
    payment_terms = Column(String(50))
    payment_due_date = Column(Date)
    notes = Column(Text)
    terms_conditions = Column(Text)
    attachments = Column(JSONB)
    custom_fields = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    updated_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    
    # Relationships
    vendor = relationship("Vendor", back_populates="invoices")
    payments = relationship("PaymentInvoice", back_populates="invoice", cascade="all, delete-orphan")
    line_items = relationship("InvoiceLineItem", back_populates="invoice", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_invoice_vendor_status', 'vendor_id', 'status'),
        Index('idx_invoice_dates', 'invoice_date', 'due_date'),
    )


class Payment(Base):
    """AP Payment model for tracking payments to vendors"""
    
    __tablename__ = "ap_payments"
    
    id = Column(Integer, primary_key=True, index=True)
    payment_number = Column(String(50), unique=True, nullable=False, index=True)
    vendor_id = Column(Integer, ForeignKey("ap_vendors.id", ondelete="CASCADE"), nullable=False, index=True)
    payment_date = Column(Date, nullable=False, index=True)
    payment_method = Column(String(50))
    reference_number = Column(String(100))
    memo = Column(Text)
    amount = Column(Numeric(15, 2), nullable=False)
    currency_code = Column(String(3), default='USD')
    exchange_rate = Column(Numeric(15, 6), default=1.0)
    status = Column(String(20), default='draft')
    bank_account_id = Column(Integer, ForeignKey("bank_accounts.id", ondelete="SET NULL"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    updated_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    
    # Relationships
    vendor = relationship("Vendor", back_populates="payments")
    invoice_applications = relationship("PaymentInvoice", back_populates="payment", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_payment_vendor_date', 'vendor_id', 'payment_date'),
    )


class PaymentInvoice(Base):
    """Junction table for many-to-many relationship between Payments and Invoices"""
    
    __tablename__ = "ap_payment_invoices"
    
    id = Column(Integer, primary_key=True)
    payment_id = Column(Integer, ForeignKey("ap_payments.id", ondelete="CASCADE"), nullable=False, index=True)
    invoice_id = Column(Integer, ForeignKey("ap_invoices.id", ondelete="CASCADE"), nullable=False, index=True)
    amount_applied = Column(Numeric(15, 2), nullable=False)
    discount_taken = Column(Numeric(15, 2), default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    payment = relationship("Payment", back_populates="invoice_applications")
    invoice = relationship("Invoice", back_populates="payments")
    
    # Indexes
    __table_args__ = (
        Index('idx_payment_invoice', 'payment_id', 'invoice_id', unique=True),
    )


class InvoiceLineItem(Base):
    """Line items for AP Invoices"""
    
    __tablename__ = "ap_invoice_line_items"
    
    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey("ap_invoices.id", ondelete="CASCADE"), nullable=False, index=True)
    line_number = Column(Integer, nullable=False)
    item_code = Column(String(50), index=True)
    description = Column(Text)
    quantity = Column(Numeric(15, 4), default=1)
    unit_price = Column(Numeric(15, 4), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    tax_amount = Column(Numeric(15, 2), default=0)
    tax_rate = Column(Numeric(5, 2), default=0)
    discount_amount = Column(Numeric(15, 2), default=0)
    discount_rate = Column(Numeric(5, 2), default=0)
    line_total = Column(Numeric(15, 2), nullable=False)
    gl_account_id = Column(Integer, ForeignKey("gl_accounts.id", ondelete="SET NULL"), index=True)
    cost_center_id = Column(Integer, ForeignKey("cost_centers.id", ondelete="SET NULL"), index=True, nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="SET NULL"), index=True, nullable=True)
    custom_fields = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    invoice = relationship("Invoice", back_populates="line_items")
    
    # Indexes
    __table_args__ = (
        Index('idx_invoice_line_number', 'invoice_id', 'line_number', unique=True),
    )


class VendorContract(Base):
    """Contract information for vendors"""
    
    __tablename__ = "ap_vendor_contracts"
    
    id = Column(Integer, primary_key=True)
    vendor_id = Column(Integer, ForeignKey("ap_vendors.id", ondelete="CASCADE"), nullable=False, index=True)
    contract_number = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, index=True)
    auto_renew = Column(Boolean, default=False, index=True)
    contract_value = Column(Numeric(15, 2))
    currency_code = Column(String(3), default='USD')
    payment_terms = Column(String(100))
    status = Column(String(20), default='active', index=True)
    document_reference = Column(String(255))
    terms_conditions = Column(Text)
    notice_period_days = Column(Integer, default=30)
    renewal_terms = Column(Text)
    termination_clause = Column(Text)
    attachments = Column(JSONB)
    custom_fields = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    updated_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    
    # Relationships
    vendor = relationship("Vendor", back_populates="contracts")
    
    # Indexes
    __table_args__ = (
        Index('idx_vendor_contract_dates', 'vendor_id', 'start_date', 'end_date'),
        Index('idx_contract_status', 'status'),
        Index('idx_contract_auto_renew', 'auto_renew')
    )


class VendorEvaluation(Base):
    """Vendor performance evaluation records"""
    
    __tablename__ = "ap_vendor_evaluations"
    
    id = Column(Integer, primary_key=True)
    vendor_id = Column(Integer, ForeignKey("ap_vendors.id", ondelete="CASCADE"), nullable=False, index=True)
    evaluation_date = Column(Date, nullable=False, default=func.current_date(), index=True)
    evaluator_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Evaluation metrics (0-5 scale)
    quality_score = Column(Numeric(3, 2), comment="Score for product/service quality (0-5)")
    delivery_score = Column(Numeric(3, 2), comment="Score for on-time delivery performance (0-5)")
    price_score = Column(Numeric(3, 2), comment="Score for competitive pricing (0-5)")
    service_score = Column(Numeric(3, 2), comment="Score for customer service (0-5)")
    communication_score = Column(Numeric(3, 2), comment="Score for communication effectiveness (0-5)")
    
    # Overall evaluation
    overall_score = Column(Numeric(3, 2), nullable=False)
    recommendation = Column(String(50), index=True)  # continue, conditional, discontinue, etc.
    
    # Detailed feedback
    strengths = Column(Text, comment="Key strengths observed")
    areas_for_improvement = Column(Text, comment="Areas needing improvement")
    comments = Column(Text, comment="General comments")
    
    # Status and follow-up
    status = Column(String(20), default='draft', index=True)  # draft, submitted, reviewed, archived
    follow_up_date = Column(Date, index=True, comment="Date for next evaluation or follow-up")
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    updated_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    
    # Relationships
    vendor = relationship("Vendor", back_populates="evaluations")
    
    # Indexes
    __table_args__ = (
        Index('idx_vendor_evaluation_date', 'vendor_id', 'evaluation_date'),
        Index('idx_evaluation_status', 'status'),
        Index('idx_evaluation_score', 'overall_score')
    )
