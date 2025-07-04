"""
Accounts Receivable (AR) database models.
"""
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


class InvoiceStatus(str, Enum):
    """Status of an invoice in the system."""
    DRAFT = "draft"
    SENT = "sent"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    WRITTEN_OFF = "written_off"


class PaymentMethod(str, Enum):
    """Payment methods for customer payments."""
    CASH = "cash"
    CHECK = "check"
    CREDIT_CARD = "credit_card"
    BANK_TRANSFER = "bank_transfer"
    DIGITAL_WALLET = "digital_wallet"
    OTHER = "other"


class Invoice(Base):
    """Invoice model for tracking customer invoices."""
    __tablename__ = "invoices"
    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    invoice_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    customer_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False)
    
    # Dates
    issue_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    paid_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Status and flags
    status: Mapped[InvoiceStatus] = mapped_column(
        SQLEnum(InvoiceStatus, name="invoice_status"),
        default=InvoiceStatus.DRAFT,
        nullable=False
    )
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    recurring_invoice_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    
    # Financials
    subtotal: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    amount_paid: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    balance_due: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    
    # References and notes
    reference: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    terms: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Audit fields
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    created_by_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    updated_by_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Relationships
    customer = relationship("Customer", back_populates="invoices")
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    payments = relationship("PaymentReceipt", back_populates="invoice", cascade="all, delete-orphan")
    created_by = relationship("User", foreign_keys=[created_by_id])
    updated_by = relationship("User", foreign_keys=[updated_by_id])
    
    __table_args__ = (
        CheckConstraint("due_date >= issue_date", name="check_due_date_after_issue"),
        CheckConstraint("total_amount >= 0", name="check_positive_total"),
        CheckConstraint("amount_paid >= 0", name="check_positive_paid"),
        CheckConstraint("balance_due = total_amount - amount_paid", name="check_balance_due"),
    )
    
    def __repr__(self):
        return f"<Invoice {self.invoice_number} - {self.status}>"


class InvoiceItem(Base):
    """Line items for an invoice."""
    __tablename__ = "invoice_items"
    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    invoice_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("invoices.id"), nullable=False)
    product_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("products.id"), nullable=True)
    account_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("chart_of_accounts.id"), nullable=False)
    
    # Item details
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(15, 3), nullable=False, default=1)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    tax_rate: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False, default=0)
    discount_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=0)
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    
    # Audit fields
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    
    # Relationships
    invoice = relationship("Invoice", back_populates="items")
    product = relationship("Product")
    account = relationship("ChartOfAccounts")
    
    __table_args__ = (
        CheckConstraint("quantity > 0", name="check_positive_quantity"),
        CheckConstraint("unit_price >= 0", name="check_non_negative_unit_price"),
        CheckConstraint("tax_rate >= 0 AND tax_rate <= 1", name="check_tax_rate_range"),
        CheckConstraint("discount_percent >= 0 AND discount_percent <= 100", name="check_discount_range"),
    )
    
    def __repr__(self):
        return f"<InvoiceItem {self.id} - {self.description[:30]}>"


class PaymentReceipt(Base):
    """Payment receipts for customer payments."""
    __tablename__ = "payment_receipts"
    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    receipt_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    invoice_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("invoices.id"), nullable=False)
    customer_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False)
    
    # Payment details
    payment_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    payment_method: Mapped[PaymentMethod] = mapped_column(SQLEnum(PaymentMethod, name="payment_method"), nullable=False)
    reference: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_posted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    posted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Audit fields
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    created_by_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    updated_by_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Relationships
    invoice = relationship("Invoice", back_populates="payments")
    customer = relationship("Customer", back_populates="payments")
    created_by = relationship("User", foreign_keys=[created_by_id])
    updated_by = relationship("User", foreign_keys=[updated_by_id])
    
    __table_args__ = (
        CheckConstraint("amount > 0", name="check_positive_amount"),
    )
    
    def __repr__(self):
        return f"<PaymentReceipt {self.receipt_number} - {self.amount}>"
