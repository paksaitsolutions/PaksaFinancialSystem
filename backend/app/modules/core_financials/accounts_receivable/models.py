"""
Accounts Receivable models for tracking customer invoices and payments.
"""
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class InvoiceStatus(str, Enum):
    """Status of an invoice."""
    DRAFT = 'draft'
    SENT = 'sent'
    VIEWED = 'viewed'
    PARTIALLY_PAID = 'partially_paid'
    PAID = 'paid'
    OVERDUE = 'overdue'
    VOID = 'void'
    UNCOLLECTIBLE = 'uncollectible'


class PaymentStatus(str, Enum):
    """Status of a payment."""
    PENDING = 'pending'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'
    REFUNDED = 'refunded'
    PARTIALLY_REFUNDED = 'partially_refunded'
    CANCELLED = 'cancelled'


class Invoice(Base):
    """Invoice model for tracking customer invoices."""
    __tablename__ = 'ar_invoices'
    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    invoice_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    
    # Customer information
    customer_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('customers.id'), nullable=False)
    customer: Mapped['Customer'] = relationship('Customer')
    
    # Invoice details
    issue_date: Mapped[date] = mapped_column(Date, nullable=False, server_default=func.current_date())
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[InvoiceStatus] = mapped_column(SQLEnum(InvoiceStatus), default=InvoiceStatus.DRAFT, nullable=False)
    
    # Amounts
    subtotal: Mapped[Decimal] = mapped_column(Numeric(19, 4), default=0, nullable=False)
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(19, 4), default=0, nullable=False)
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(19, 4), default=0, nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(19, 4), default=0, nullable=False)
    amount_paid: Mapped[Decimal] = mapped_column(Numeric(19, 4), default=0, nullable=False)
    balance_due: Mapped[Decimal] = mapped_column(Numeric(19, 4), server_default='0', nullable=False)
    
    # Dates
    date_sent: Mapped[Optional[datetime]]
    date_viewed: Mapped[Optional[datetime]]
    date_paid: Mapped[Optional[datetime]]
    
    # References
    po_number: Mapped[Optional[str]] = mapped_column(String(50))
    terms: Mapped[Optional[str]] = mapped_column(Text)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Accounting integration
    gl_journal_entry_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('gl_journal_entries.id'))
    
    # Audit fields
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now(),
    )
    
    # Relationships
    invoice_items: Mapped[List['InvoiceItem']] = relationship('InvoiceItem', back_populates='invoice')
    payments: Mapped[List['Payment']] = relationship('Payment', back_populates='invoice')
    
    # Created by/updated by
    created_by_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('users.id'))
    updated_by_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('users.id'))
    
    # Constraints
    __table_args__ = (
        CheckConstraint('total_amount = subtotal + tax_amount - discount_amount', name='check_invoice_amounts'),
        CheckConstraint('balance_due = total_amount - amount_paid', name='check_balance_due'),
        CheckConstraint('amount_paid <= total_amount', name='check_amount_paid'),
    )
    
    def __repr__(self) -> str:
        return f'<Invoice {self.invoice_number} ({self.status})>'


class InvoiceItem(Base):
    """Line items for an invoice."""
    __tablename__ = 'ar_invoice_items'
    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    invoice_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('ar_invoices.id'), nullable=False)
    
    # Item details
    description: Mapped[str] = mapped_column(Text, nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 4), default=1, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    
    # Amounts
    discount_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0, nullable=False)
    tax_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0, nullable=False)
    
    # References
    item_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('inventory_items.id'))
    gl_account_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('gl_accounts.id'), nullable=False)
    
    # Relationships
    invoice: Mapped['Invoice'] = relationship('Invoice', back_populates='invoice_items')
    
    # Computed properties
    @property
    def subtotal(self) -> Decimal:
        return self.quantity * self.unit_price
    
    @property
    def discount_amount(self) -> Decimal:
        return (self.subtotal * self.discount_percent) / 100
    
    @property
    def taxable_amount(self) -> Decimal:
        return self.subtotal - self.discount_amount
    
    @property
    def tax_amount(self) -> Decimal:
        return (self.taxable_amount * self.tax_rate) / 100
    
    @property
    def total_amount(self) -> Decimal:
        return self.taxable_amount + self.tax_amount
    
    def __repr__(self) -> str:
        return f'<InvoiceItem {self.description[:30]}...>'


class Payment(Base):
    """Payments received from customers."""
    __tablename__ = 'ar_payments'
    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    payment_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    
    # Payment details
    payment_date: Mapped[date] = mapped_column(Date, nullable=False, server_default=func.current_date())
    status: Mapped[PaymentStatus] = mapped_column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    
    # Payment method
    payment_method: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., 'credit_card', 'bank_transfer', 'cash'
    transaction_id: Mapped[Optional[str]] = mapped_column(String(100))
    reference_number: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Accounting integration
    gl_journal_entry_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('gl_journal_entries.id'))
    
    # Relationships
    invoice_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('ar_invoices.id'))
    invoice: Mapped[Optional['Invoice']] = relationship('Invoice', back_populates='payments')
    
    customer_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('customers.id'), nullable=False)
    customer: Mapped['Customer'] = relationship('Customer')
    
    # Audit fields
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now(),
    )
    
    # Created by/updated by
    created_by_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('users.id'))
    updated_by_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('users.id'))
    
    def __repr__(self) -> str:
        return f'<Payment {self.payment_number} ({self.amount})>'


class CreditNote(Base):
    """Credit notes issued to customers."""
    __tablename__ = 'ar_credit_notes'
    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    credit_note_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    
    # Customer information
    customer_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('customers.id'), nullable=False)
    customer: Mapped['Customer'] = relationship('Customer')
    
    # Credit note details
    issue_date: Mapped[date] = mapped_column(Date, nullable=False, server_default=func.current_date())
    status: Mapped[str] = mapped_column(String(20), default='open', nullable=False)  # open, applied, expired, void
    
    # Amounts
    total_amount: Mapped[Decimal] = mapped_column(Numeric(19, 4), default=0, nullable=False)
    remaining_amount: Mapped[Decimal] = mapped_column(Numeric(19, 4), default=0, nullable=False)
    
    # References
    reference_invoice_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('ar_invoices.id'))
    reason: Mapped[Optional[str]] = mapped_column(Text)
    
    # Accounting integration
    gl_journal_entry_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('gl_journal_entries.id'))
    
    # Audit fields
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now(),
    )
    
    # Created by/updated by
    created_by_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('users.id'))
    updated_by_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('users.id'))
    
    # Relationships
    credit_note_items: Mapped[List['CreditNoteItem']] = relationship('CreditNoteItem', back_populates='credit_note')
    
    def __repr__(self) -> str:
        return f'<CreditNote {self.credit_note_number} ({self.total_amount})>'
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
>>>>>>> e96df7278ce4216131b6c65d411c0723f4de7f91
