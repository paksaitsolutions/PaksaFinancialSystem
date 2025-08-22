"""
Invoice model for Accounts Payable module.
"""
import uuid
from datetime import date, datetime
from typing import Optional, List
from sqlalchemy import Column, String, Boolean, ForeignKey, Text, Date, Enum, Integer, Numeric, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.enums import InvoiceStatus, PaymentTerms

class APInvoice(Base):
    """Accounts Payable Invoice model."""
    
    __tablename__ = "ap_invoice"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_number = Column(String(50), nullable=False, index=True)
    vendor_id = Column(UUID(as_uuid=True), ForeignKey("vendor.id"), nullable=False, index=True)
    
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
    currency_id = Column(UUID(as_uuid=True), ForeignKey("currency.id"))
    
    # Approval
    requires_approval = Column(Boolean, default=False)
    approved_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    approved_at = Column(DateTime)
    
    # Relationships
    vendor = relationship("Vendor", back_populates="invoices")
    currency = relationship("Currency")
    approved_by = relationship("User")
    line_items = relationship("APInvoiceLineItem", back_populates="invoice", cascade="all, delete-orphan")
    payments = relationship("APPayment", secondary="ap_invoice_payment", back_populates="invoices")
    
    def __repr__(self):
        return f"<APInvoice {self.invoice_number}: {self.total_amount}>"


class APInvoiceLineItem(Base):
    """Line item for an Accounts Payable invoice."""
    
    __tablename__ = "ap_invoice_line_item"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("ap_invoice.id"), nullable=False)
    
    # Line item details
    description = Column(String(255), nullable=False)
    quantity = Column(Numeric(precision=10, scale=2), nullable=False, default=1)
    unit_price = Column(Numeric(precision=18, scale=2), nullable=False)
    amount = Column(Numeric(precision=18, scale=2), nullable=False)
    
    # Accounting
    account_id = Column(UUID(as_uuid=True), ForeignKey("gl_account.id"), nullable=False)
    tax_code_id = Column(UUID(as_uuid=True), ForeignKey("tax_code.id"))
    
    # Relationships
    invoice = relationship("APInvoice", back_populates="line_items")
    account = relationship("GLAccount")
    tax_code = relationship("TaxCode")
    
    def __repr__(self):
        return f"<APInvoiceLineItem {self.description}: {self.amount}>"


class APPayment(Base):
    """Payment for Accounts Payable invoices."""
    
    __tablename__ = "ap_payment"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payment_number = Column(String(50), nullable=False, index=True)
    vendor_id = Column(UUID(as_uuid=True), ForeignKey("vendor.id"), nullable=False, index=True)
    
    # Payment details
    payment_date = Column(Date, nullable=False, index=True)
    amount = Column(Numeric(precision=18, scale=2), nullable=False)
    payment_method = Column(String(50), nullable=False)
    reference = Column(String(100))
    memo = Column(Text)
    
    # Status
    status = Column(Enum("pending", "completed", "voided", name="payment_status"), default="pending", nullable=False)
    
    # Relationships
    vendor = relationship("Vendor")
    invoices = relationship("APInvoice", secondary="ap_invoice_payment", back_populates="payments")
    
    def __repr__(self):
        return f"<APPayment {self.payment_number}: {self.amount}>"


class APInvoicePayment(Base):
    """Association table for invoices and payments."""
    
    __tablename__ = "ap_invoice_payment"
    
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("ap_invoice.id"), primary_key=True)
    payment_id = Column(UUID(as_uuid=True), ForeignKey("ap_payment.id"), primary_key=True)
    amount = Column(Numeric(precision=18, scale=2), nullable=False)
    
    def __repr__(self):
        return f"<APInvoicePayment: {self.amount}>"