from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, Integer
from sqlalchemy.types import DECIMAL as Decimal
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime

class Vendor(Base):
    __tablename__ = "vendors"
    
    id = Column(String, primary_key=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    vendor_code = Column(String(20), unique=True, nullable=False)
    vendor_name = Column(String(255), nullable=False)
    contact_person = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    address = Column(Text)
    tax_id = Column(String(50))
    payment_terms = Column(String(50))
    credit_limit = Column(Decimal(15, 2), default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class APInvoice(Base):
    __tablename__ = "ap_invoices"
    
    id = Column(String, primary_key=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    vendor_id = Column(String, ForeignKey("vendors.id"), nullable=False)
    invoice_number = Column(String(50), nullable=False)
    invoice_date = Column(DateTime, nullable=False)
    due_date = Column(DateTime, nullable=False)
    subtotal = Column(Decimal(15, 2), default=0)
    tax_amount = Column(Decimal(15, 2), default=0)
    total_amount = Column(Decimal(15, 2), default=0)
    paid_amount = Column(Decimal(15, 2), default=0)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

class APPayment(Base):
    __tablename__ = "ap_payments"
    
    id = Column(String, primary_key=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    vendor_id = Column(String, ForeignKey("vendors.id"), nullable=False)
    payment_number = Column(String(50), nullable=False)
    payment_date = Column(DateTime, nullable=False)
    payment_method = Column(String(50))
    amount = Column(Decimal(15, 2), nullable=False)
    reference = Column(String(100))
    status = Column(String(20), default="completed")
    created_at = Column(DateTime, default=datetime.utcnow)

class CreditMemo(Base):
    __tablename__ = "credit_memos"
    
    id = Column(String, primary_key=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    vendor_id = Column(String, ForeignKey("vendors.id"), nullable=False)
    memo_number = Column(String(50), nullable=False)
    memo_date = Column(DateTime, nullable=False)
    amount = Column(Decimal(15, 2), nullable=False)
    reason = Column(Text)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)

class Form1099(Base):
    __tablename__ = "form_1099"
    
    id = Column(String, primary_key=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    vendor_id = Column(String, ForeignKey("vendors.id"), nullable=False)
    tax_year = Column(Integer, nullable=False)
    total_payments = Column(Decimal(15, 2), default=0)
    form_type = Column(String(20), default="1099-NEC")
    status = Column(String(20), default="draft")
    created_at = Column(DateTime, default=datetime.utcnow)