"""
Accounts Payable models for vendors, invoices, and payments.
"""
from sqlalchemy import Column, Integer, String, Decimal, Date, DateTime, Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from app.models.base import BaseModel, AuditModel
import enum

class VendorStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class InvoiceStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    PAID = "paid"
    CANCELLED = "cancelled"

class Vendor(AuditModel):
    __tablename__ = 'vendors'
    
    vendor_code = Column(String(20), unique=True, nullable=False)
    vendor_name = Column(String(100), nullable=False)
    contact_person = Column(String(100))
    email = Column(String(100))
    phone = Column(String(20))
    address = Column(Text)
    tax_id = Column(String(50))
    payment_terms = Column(String(50))
    status = Column(Enum(VendorStatus), default=VendorStatus.ACTIVE)
    
    invoices = relationship("APInvoice", back_populates="vendor")

class APInvoice(AuditModel):
    __tablename__ = 'ap_invoices'
    
    invoice_number = Column(String(50), nullable=False)
    vendor_id = Column(Integer, ForeignKey('vendors.id'), nullable=False)
    invoice_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    total_amount = Column(Decimal(15, 2), nullable=False)
    paid_amount = Column(Decimal(15, 2), default=0)
    balance_due = Column(Decimal(15, 2), nullable=False)
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.PENDING)
    description = Column(Text)
    
    vendor = relationship("Vendor", back_populates="invoices")
    payments = relationship("APPayment", back_populates="invoice")

class APPayment(AuditModel):
    __tablename__ = 'ap_payments'
    
    payment_number = Column(String(50), unique=True, nullable=False)
    invoice_id = Column(Integer, ForeignKey('ap_invoices.id'), nullable=False)
    payment_date = Column(Date, nullable=False)
    payment_amount = Column(Decimal(15, 2), nullable=False)
    payment_method = Column(String(50))
    reference_number = Column(String(100))
    
    invoice = relationship("APInvoice", back_populates="payments")