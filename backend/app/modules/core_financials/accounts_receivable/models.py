import enum
from sqlalchemy import (
    Column, Integer, String, Text, Numeric, Date, DateTime, Boolean, ForeignKey, Index, 
    Enum as SQLEnum, JSON as JSONB, func, CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr
from datetime import datetime, timedelta
from enum import Enum as PyEnum
from typing import Optional
from decimal import Decimal

from app.core.base import Base

class CustomerStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    CREDIT_HOLD = "credit_hold"
    PENDING_APPROVAL = "pending_approval"

class CustomerType(str, enum.Enum):
    INDIVIDUAL = "individual"
    BUSINESS = "business"
    GOVERNMENT = "government"
    NON_PROFIT = "non_profit"

class InvoiceStatus(str, enum.Enum):
    DRAFT = "draft"
    SENT = "sent"
    VIEWED = "viewed"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    VOID = "void"

class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSED = "processed"
    FAILED = "failed"
    REFUNDED = "refunded"

class CollectionStatus(str, enum.Enum):
    CURRENT = "current"
    FIRST_NOTICE = "first_notice"
    SECOND_NOTICE = "second_notice"
    FINAL_NOTICE = "final_notice"
    COLLECTIONS = "collections"
    WRITE_OFF = "write_off"

class Customer(Base):
    __tablename__ = "ar_customers"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    legal_name = Column(String(255))
    customer_type = Column(SQLEnum(CustomerType, name="customer_type_enum"), nullable=False)
    
    # Contact Information
    email = Column(String(255), index=True)
    phone = Column(String(50))
    website = Column(String(255))
    
    # Primary Contact
    contact_person = Column(String(100))
    contact_title = Column(String(100))
    contact_email = Column(String(100))
    contact_phone = Column(String(50))
    
    # Billing Address
    billing_address_line1 = Column(String(255))
    billing_address_line2 = Column(String(255))
    billing_city = Column(String(100))
    billing_state = Column(String(100))
    billing_postal_code = Column(String(20))
    billing_country = Column(String(100))
    
    # Shipping Address
    shipping_same_as_billing = Column(Boolean, default=True)
    shipping_address_line1 = Column(String(255))
    shipping_address_line2 = Column(String(255))
    shipping_city = Column(String(100))
    shipping_state = Column(String(100))
    shipping_postal_code = Column(String(20))
    shipping_country = Column(String(100))
    
    # Credit Information
    credit_limit = Column(Numeric(15, 2), default=0)
    current_balance = Column(Numeric(15, 2), default=0)
    credit_rating = Column(String(10), index=True)
    payment_terms = Column(String(50), default="NET30")
    credit_hold = Column(Boolean, default=False, index=True)
    
    # Status and Categories
    status = Column(SQLEnum(CustomerStatus, name="customer_status_enum"), default=CustomerStatus.ACTIVE, index=True)
    customer_since = Column(Date, default=func.current_date())
    last_order_date = Column(Date)
    
    # Financial Information
    total_sales_ytd = Column(Numeric(15, 2), default=0)
    total_payments_ytd = Column(Numeric(15, 2), default=0)
    average_days_to_pay = Column(Integer, default=0)
    
    # Additional Information
    tax_id = Column(String(50))
    tax_exempt = Column(Boolean, default=False)
    preferred_currency = Column(String(3), default='USD')
    preferred_language = Column(String(10), default='en')
    
    # Custom Fields
    custom_fields = Column(JSONB)
    internal_notes = Column(Text)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    updated_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    
    # Relationships
    invoices = relationship("ARInvoice", back_populates="customer", cascade="all, delete-orphan")
    payments = relationship("ARPayment", back_populates="customer", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_customer_name_type', 'name', 'customer_type'),
        Index('idx_customer_status_credit', 'status', 'credit_hold'),
        Index('idx_customer_contact', 'email', 'phone'),
    )

    @property
    def outstanding_balance(self):
        return sum(invoice.balance_due for invoice in self.invoices if invoice.balance_due > 0)

    @property
    def overdue_balance(self):
        from datetime import date
        today = date.today()
        return sum(
            invoice.balance_due for invoice in self.invoices 
            if invoice.balance_due > 0 and invoice.due_date < today
        )

class ARInvoice(Base):
    __tablename__ = "ar_invoices"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("ar_customers.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Invoice Details
    invoice_date = Column(Date, nullable=False, index=True)
    due_date = Column(Date, nullable=False, index=True)
    terms = Column(String(50))
    po_number = Column(String(100))
    
    # Amounts
    subtotal = Column(Numeric(15, 2), nullable=False, default=0)
    tax_amount = Column(Numeric(15, 2), default=0)
    discount_amount = Column(Numeric(15, 2), default=0)
    total_amount = Column(Numeric(15, 2), nullable=False, default=0)
    paid_amount = Column(Numeric(15, 2), default=0)
    balance_due = Column(Numeric(15, 2), default=0)
    
    # Status and Tracking
    status = Column(SQLEnum(InvoiceStatus, name="ar_invoice_status_enum"), default=InvoiceStatus.DRAFT, index=True)
    sent_date = Column(DateTime(timezone=True))
    viewed_date = Column(DateTime(timezone=True))
    
    # Additional Information
    notes = Column(Text)
    terms_conditions = Column(Text)
    currency_code = Column(String(3), default='USD')
    exchange_rate = Column(Numeric(15, 6), default=1.0)
    
    # Recurring Invoice Information
    is_recurring = Column(Boolean, default=False, index=True)
    recurring_frequency = Column(String(20))  # monthly, quarterly, annually
    next_invoice_date = Column(Date)
    
    # Custom Fields
    custom_fields = Column(JSONB)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    updated_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    
    # Relationships
    customer = relationship("Customer", back_populates="invoices")
    line_items = relationship("ARInvoiceLineItem", back_populates="invoice", cascade="all, delete-orphan")
    payments = relationship("ARPaymentInvoice", back_populates="invoice", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_ar_invoice_customer_status', 'customer_id', 'status'),
        Index('idx_ar_invoice_dates', 'invoice_date', 'due_date'),
        Index('idx_ar_invoice_balance', 'balance_due'),
    )

    @property
    def days_overdue(self):
        if self.due_date and self.balance_due > 0:
            from datetime import date
            today = date.today()
            if today > self.due_date:
                return (today - self.due_date).days
        return 0

class ARInvoiceLineItem(Base):
    __tablename__ = "ar_invoice_line_items"

    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey("ar_invoices.id", ondelete="CASCADE"), nullable=False, index=True)
    line_number = Column(Integer, nullable=False)
    
    # Item Details
    item_code = Column(String(50))
    description = Column(Text, nullable=False)
    quantity = Column(Numeric(15, 4), default=1)
    unit_price = Column(Numeric(15, 4), nullable=False)
    
    # Amounts
    line_total = Column(Numeric(15, 2), nullable=False)
    tax_amount = Column(Numeric(15, 2), default=0)
    discount_amount = Column(Numeric(15, 2), default=0)
    
    # Accounting
    revenue_account_id = Column(Integer, ForeignKey("gl_accounts.id", ondelete="SET NULL"))
    
    # Relationships
    invoice = relationship("ARInvoice", back_populates="line_items")
    
    # Indexes
    __table_args__ = (
        Index('idx_ar_line_invoice_number', 'invoice_id', 'line_number', unique=True),
    )

class ARPayment(Base):
    __tablename__ = "ar_payments"

    id = Column(Integer, primary_key=True, index=True)
    payment_number = Column(String(50), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("ar_customers.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Payment Details
    payment_date = Column(Date, nullable=False, index=True)
    payment_method = Column(String(50))
    reference_number = Column(String(100))
    amount = Column(Numeric(15, 2), nullable=False)
    
    # Status and Processing
    status = Column(SQLEnum(PaymentStatus, name="ar_payment_status_enum"), default=PaymentStatus.PENDING, index=True)
    processed_date = Column(DateTime(timezone=True))
    
    # Additional Information
    notes = Column(Text)
    currency_code = Column(String(3), default='USD')
    exchange_rate = Column(Numeric(15, 6), default=1.0)
    
    # Bank Information
    bank_account_id = Column(Integer, ForeignKey("bank_accounts.id", ondelete="SET NULL"))
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    updated_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    
    # Relationships
    customer = relationship("Customer", back_populates="payments")
    invoice_applications = relationship("ARPaymentInvoice", back_populates="payment", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_ar_payment_customer_date', 'customer_id', 'payment_date'),
    )

class ARPaymentInvoice(Base):
    __tablename__ = "ar_payment_invoices"

    id = Column(Integer, primary_key=True)
    payment_id = Column(Integer, ForeignKey("ar_payments.id", ondelete="CASCADE"), nullable=False, index=True)
    invoice_id = Column(Integer, ForeignKey("ar_invoices.id", ondelete="CASCADE"), nullable=False, index=True)
    amount_applied = Column(Numeric(15, 2), nullable=False)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    payment = relationship("ARPayment", back_populates="invoice_applications")
    invoice = relationship("ARInvoice", back_populates="payments")
    
    # Indexes
    __table_args__ = (
        Index('idx_ar_payment_invoice', 'payment_id', 'invoice_id', unique=True),
    )

class CollectionActivity(Base):
    __tablename__ = "ar_collection_activities"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("ar_customers.id", ondelete="CASCADE"), nullable=False, index=True)
    invoice_id = Column(Integer, ForeignKey("ar_invoices.id", ondelete="CASCADE"), index=True)
    
    # Activity Details
    activity_date = Column(Date, nullable=False, default=func.current_date(), index=True)
    activity_type = Column(String(50), nullable=False, index=True)  # call, email, letter, meeting
    status = Column(SQLEnum(CollectionStatus, name="collection_status_enum"), nullable=False, index=True)
    
    # Content
    subject = Column(String(255))
    description = Column(Text)
    outcome = Column(Text)
    
    # Follow-up
    follow_up_date = Column(Date, index=True)
    follow_up_action = Column(String(255))
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    
    # Indexes
    __table_args__ = (
        Index('idx_collection_customer_date', 'customer_id', 'activity_date'),
        Index('idx_collection_status_followup', 'status', 'follow_up_date'),
    )