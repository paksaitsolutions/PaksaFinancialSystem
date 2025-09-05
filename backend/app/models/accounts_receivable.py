from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, Integer
from sqlalchemy.types import DECIMAL as Decimal
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime

class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(String, primary_key=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    customer_code = Column(String(20), unique=True, nullable=False)
    customer_name = Column(String(255), nullable=False)
    contact_person = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    address = Column(Text)
    credit_limit = Column(Decimal(15, 2), default=0)
    payment_terms = Column(String(50))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ARInvoice(Base):
    __tablename__ = "ar_invoices"
    
    id = Column(String, primary_key=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    customer_id = Column(String, ForeignKey("customers.id"), nullable=False)
    invoice_number = Column(String(50), nullable=False)
    invoice_date = Column(DateTime, nullable=False)
    due_date = Column(DateTime, nullable=False)
    subtotal = Column(Decimal(15, 2), default=0)
    tax_amount = Column(Decimal(15, 2), default=0)
    total_amount = Column(Decimal(15, 2), default=0)
    paid_amount = Column(Decimal(15, 2), default=0)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

class ARPayment(Base):
    __tablename__ = "ar_payments"
    
    id = Column(String, primary_key=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    customer_id = Column(String, ForeignKey("customers.id"), nullable=False)
    payment_number = Column(String(50), nullable=False)
    payment_date = Column(DateTime, nullable=False)
    payment_method = Column(String(50))
    amount = Column(Decimal(15, 2), nullable=False)
    reference = Column(String(100))
    status = Column(String(20), default="completed")
    created_at = Column(DateTime, default=datetime.utcnow)

class Collection(Base):
    __tablename__ = "collections"
    
    id = Column(String, primary_key=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    customer_id = Column(String, ForeignKey("customers.id"), nullable=False)
    invoice_id = Column(String, ForeignKey("ar_invoices.id"), nullable=False)
    collection_date = Column(DateTime, nullable=False)
    amount_collected = Column(Decimal(15, 2), nullable=False)
    collection_method = Column(String(50))
    notes = Column(Text)
    status = Column(String(20), default="completed")
    created_at = Column(DateTime, default=datetime.utcnow)