"""
AR Invoice model for Accounts Receivable module.
"""
import uuid
from datetime import date, datetime
from typing import Optional, List
from sqlalchemy import Column, String, Boolean, ForeignKey, Text, Date, Enum, Integer, Numeric, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.enums import InvoiceStatus, PaymentTerms

class ARInvoice(Base):
    """Accounts Receivable Invoice model."""
    
    __tablename__ = "ar_invoice"
    __table_args__ = {'extend_existing': True}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_number = Column(String(50), nullable=False, index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customer.id"), nullable=False, index=True)
    
    # Invoice details
    invoice_date = Column(Date, nullable=False, index=True)
    due_date = Column(Date, nullable=False, index=True)
    posting_date = Column(Date, index=True)
    description = Column(Text)
    reference = Column(String(100))
    
    # Amounts
    subtotal = Column(Numeric(precision=18, scale=2), nullable=False, default=0)
    tax_amount = Column(Numeric(precision=18, scale=2), nullable=False, default=0)
    discount_amount = Column(Numeric(precision=18, scale=2), nullable=False, default=0)
    total_amount = Column(Numeric(precision=18, scale=2), nullable=False, default=0)
    paid_amount = Column(Numeric(precision=18, scale=2), nullable=False, default=0)
    balance_due = Column(Numeric(precision=18, scale=2), nullable=False, default=0)
    
    # Status and tracking
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.DRAFT, nullable=False, index=True)
    payment_terms = Column(Enum(PaymentTerms))
    currency_id = Column(UUID(as_uuid=True), ForeignKey("currencies.id"))
    
    # Relationships
    customer = relationship("Customer", back_populates="invoices")
    currency = relationship("Currency")
    line_items = relationship("ARInvoiceLineItem", back_populates="invoice", cascade="all, delete-orphan")
    payments = relationship("ARPayment", secondary="ar_invoice_payment", back_populates="invoices")
    
    def __repr__(self):
        return f"<ARInvoice {self.invoice_number}: {self.total_amount}>"


class ARInvoiceLineItem(Base):
    """Line item for an Accounts Receivable invoice."""
    
    __tablename__ = "ar_invoice_line_item"
    __table_args__ = {'extend_existing': True}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("ar_invoice.id"), nullable=False)
    
    # Line item details
    description = Column(String(255), nullable=False)
    quantity = Column(Numeric(precision=10, scale=2), nullable=False, default=1)
    unit_price = Column(Numeric(precision=18, scale=2), nullable=False)
    amount = Column(Numeric(precision=18, scale=2), nullable=False)
    
    # Accounting
    account_id = Column(UUID(as_uuid=True), ForeignKey("gl_account.id"), nullable=False)
    tax_code_id = Column(UUID(as_uuid=True), ForeignKey("tax_code.id"))
    
    # Relationships
    invoice = relationship("ARInvoice", back_populates="line_items")
    account = relationship("GLAccount")
    tax_code = relationship("TaxCode")
    
    def __repr__(self):
        return f"<ARInvoiceLineItem {self.description}: {self.amount}>"


class ARPayment(Base):
    """Payment for Accounts Receivable invoices."""
    
    __tablename__ = "ar_payment"
    __table_args__ = {'extend_existing': True}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payment_number = Column(String(50), nullable=False, index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customer.id"), nullable=False, index=True)
    
    # Payment details
    payment_date = Column(Date, nullable=False, index=True)
    amount = Column(Numeric(precision=18, scale=2), nullable=False)
    payment_method = Column(String(50), nullable=False)
    reference = Column(String(100))
    memo = Column(Text)
    
    # Status
    status = Column(Enum("pending", "completed", "voided", name="ar_payment_status"), default="pending", nullable=False)
    
    # Relationships
    customer = relationship("Customer")
    invoices = relationship("ARInvoice", secondary="ar_invoice_payment", back_populates="payments")
    
    def __repr__(self):
        return f"<ARPayment {self.payment_number}: {self.amount}>"


class ARInvoicePayment(Base):
    """Association table for invoices and payments."""
    
    __tablename__ = "ar_invoice_payment"
    __table_args__ = {'extend_existing': True}
    
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("ar_invoice.id"), primary_key=True)
    payment_id = Column(UUID(as_uuid=True), ForeignKey("ar_payment.id"), primary_key=True)
    amount = Column(Numeric(precision=18, scale=2), nullable=False)
    
    def __repr__(self):
        return f"<ARInvoicePayment: {self.amount}>"