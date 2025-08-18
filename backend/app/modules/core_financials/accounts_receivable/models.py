"""
Accounts Receivable models for tracking customer invoices and payments.
"""
from datetime import date, datetime
from decimal import Decimal
from enum import Enum, auto
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean, 
    CheckConstraint, 
    Column, 
    Date, 
    DateTime, 
    Enum as SQLEnum, 
    ForeignKey, 
    Integer,
    Numeric, 
    String, 
    Text,
    UniqueConstraint,
    func,
    and_,
    or_,
    select,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from core.database import Base


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
