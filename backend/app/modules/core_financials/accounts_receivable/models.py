"""
Accounts Receivable models for customers, invoices, and payments.
"""
from sqlalchemy import Column, Integer, String, Decimal, Date, DateTime, Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from app.models.base import BaseModel, AuditModel
import enum

class CustomerStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class InvoiceStatus(enum.Enum):
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"

class Customer(AuditModel):
    __tablename__ = 'customers'
    
    customer_code = Column(String(20), unique=True, nullable=False)
    customer_name = Column(String(100), nullable=False)
    contact_person = Column(String(100))
    email = Column(String(100))
    phone = Column(String(20))
    billing_address = Column(Text)
    shipping_address = Column(Text)
    tax_id = Column(String(50))
    credit_limit = Column(Decimal(15, 2))
    payment_terms = Column(String(50))
    status = Column(Enum(CustomerStatus), default=CustomerStatus.ACTIVE)
    
    invoices = relationship("ARInvoice", back_populates="customer")

class ARInvoice(AuditModel):
    __tablename__ = 'ar_invoices'
    
    invoice_number = Column(String(50), unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    invoice_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    subtotal = Column(Decimal(15, 2), nullable=False)
    tax_amount = Column(Decimal(15, 2), default=0)
    total_amount = Column(Decimal(15, 2), nullable=False)
    paid_amount = Column(Decimal(15, 2), default=0)
    balance_due = Column(Decimal(15, 2), nullable=False)
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.DRAFT)
    
    customer = relationship("Customer", back_populates="invoices")
    line_items = relationship("ARInvoiceLineItem", back_populates="invoice")
    payments = relationship("ARPayment", back_populates="invoice")

class ARInvoiceLineItem(BaseModel):
    __tablename__ = 'ar_invoice_line_items'
    
    invoice_id = Column(Integer, ForeignKey('ar_invoices.id'), nullable=False)
    description = Column(Text, nullable=False)
    quantity = Column(Decimal(10, 2), default=1)
    unit_price = Column(Decimal(15, 2), nullable=False)
    line_total = Column(Decimal(15, 2), nullable=False)
    
    invoice = relationship("ARInvoice", back_populates="line_items")

class ARPayment(AuditModel):
    __tablename__ = 'ar_payments'
    
    payment_number = Column(String(50), unique=True, nullable=False)
    invoice_id = Column(Integer, ForeignKey('ar_invoices.id'), nullable=False)
    payment_date = Column(Date, nullable=False)
    payment_amount = Column(Decimal(15, 2), nullable=False)
    payment_method = Column(String(50))
    reference_number = Column(String(100))
    
    invoice = relationship("ARInvoice", back_populates="payments")