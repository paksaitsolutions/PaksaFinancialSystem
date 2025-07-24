"""
Invoicing models.
"""
import uuid
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import Column, String, Boolean, ForeignKey, Date, DateTime, Numeric, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base

class InvoiceTemplate(Base):
    """Invoice template model."""
    
    __tablename__ = "invoice_template"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    template_html = Column(Text, nullable=False)
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Invoice(Base):
    """Invoice model."""
    
    __tablename__ = "invoice"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    invoice_number = Column(String(50), nullable=False, index=True)
    customer_id = Column(UUID(as_uuid=True), nullable=False)
    template_id = Column(UUID(as_uuid=True), ForeignKey("invoice_template.id"))
    
    issue_date = Column(Date, nullable=False, default=date.today)
    due_date = Column(Date, nullable=False)
    subtotal = Column(Numeric(precision=18, scale=2), nullable=False)
    tax_amount = Column(Numeric(precision=18, scale=2), default=0)
    total_amount = Column(Numeric(precision=18, scale=2), nullable=False)
    
    status = Column(String(20), default="draft", index=True)  # draft, sent, paid, overdue, cancelled
    payment_status = Column(String(20), default="unpaid")  # unpaid, partial, paid
    
    notes = Column(Text)
    terms = Column(Text)
    
    is_recurring = Column(Boolean, default=False)
    recurring_frequency = Column(String(20))  # monthly, quarterly, yearly
    next_invoice_date = Column(Date)
    
    sent_at = Column(DateTime)
    paid_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    template = relationship("InvoiceTemplate")
    items = relationship("InvoiceItem", back_populates="invoice")
    payments = relationship("InvoicePayment", back_populates="invoice")

class InvoiceItem(Base):
    """Invoice item model."""
    
    __tablename__ = "invoice_item"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoice.id"), nullable=False)
    
    description = Column(String(500), nullable=False)
    quantity = Column(Numeric(precision=10, scale=2), nullable=False)
    unit_price = Column(Numeric(precision=18, scale=2), nullable=False)
    total_price = Column(Numeric(precision=18, scale=2), nullable=False)
    
    # Relationships
    invoice = relationship("Invoice", back_populates="items")

class InvoicePayment(Base):
    """Invoice payment model."""
    
    __tablename__ = "invoice_payment"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoice.id"), nullable=False)
    
    payment_date = Column(Date, nullable=False, default=date.today)
    amount = Column(Numeric(precision=18, scale=2), nullable=False)
    payment_method = Column(String(50), nullable=False)
    reference = Column(String(100))
    notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    invoice = relationship("Invoice", back_populates="payments")

class InvoiceApproval(Base):
    """Invoice approval workflow model."""
    
    __tablename__ = "invoice_approval"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoice.id"), nullable=False)
    
    approver_id = Column(UUID(as_uuid=True), nullable=False)
    status = Column(String(20), nullable=False)  # pending, approved, rejected
    comments = Column(Text)
    approved_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)