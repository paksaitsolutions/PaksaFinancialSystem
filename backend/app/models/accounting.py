# -*- coding: utf-8 -*-
"""
Comprehensive Accounting Models
------------------------------
Complete models for GL, AP, AR, Budget, Tax integration
"""

from sqlalchemy import Column, Integer, String, Date, DateTime, Text, ForeignKey, Numeric, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base

# Chart of Accounts
class ChartOfAccounts(Base):
    __tablename__ = 'chart_of_accounts'
    
    id = Column(Integer, primary_key=True, index=True)
    account_code = Column(String(20), unique=True, nullable=False, index=True)
    account_name = Column(String(255), nullable=False)
    account_type = Column(String(50), nullable=False)  # ASSET, LIABILITY, EQUITY, REVENUE, EXPENSE
    parent_id = Column(Integer, ForeignKey('chart_of_accounts.id'))
    is_active = Column(Boolean, default=True)
    balance = Column(Numeric(15, 2), default=0)
    
    # Audit fields
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    parent = relationship("ChartOfAccounts", remote_side=[id])
    journal_entries = relationship("JournalEntryLine", back_populates="account")

# Journal Entries
class JournalEntry(Base):
    __tablename__ = 'journal_entries'
    
    id = Column(Integer, primary_key=True, index=True)
    entry_number = Column(String(50), unique=True, nullable=False)
    entry_date = Column(Date, nullable=False)
    description = Column(Text)
    reference = Column(String(100))
    total_debit = Column(Numeric(15, 2), default=0)
    total_credit = Column(Numeric(15, 2), default=0)
    status = Column(String(20), default='DRAFT')  # DRAFT, POSTED, REVERSED
    
    # Audit fields
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    created_by = Column(Integer)
    
    # Relationships
    lines = relationship("JournalEntryLine", back_populates="journal_entry", cascade="all, delete-orphan")

class JournalEntryLine(Base):
    __tablename__ = 'journal_entry_lines'
    
    id = Column(Integer, primary_key=True, index=True)
    journal_entry_id = Column(Integer, ForeignKey('journal_entries.id'), nullable=False)
    account_id = Column(Integer, ForeignKey('chart_of_accounts.id'), nullable=False)
    description = Column(String(255))
    debit_amount = Column(Numeric(15, 2), default=0)
    credit_amount = Column(Numeric(15, 2), default=0)
    
    # Relationships
    journal_entry = relationship("JournalEntry", back_populates="lines")
    account = relationship("ChartOfAccounts", back_populates="journal_entries")

# Vendors (AP)
class Vendor(Base):
    __tablename__ = 'vendors'
    
    id = Column(Integer, primary_key=True, index=True)
    vendor_code = Column(String(20), unique=True, nullable=False)
    vendor_name = Column(String(255), nullable=False)
    contact_person = Column(String(100))
    email = Column(String(100))
    phone = Column(String(20))
    address = Column(Text)
    tax_id = Column(String(50))
    payment_terms = Column(String(50))
    is_active = Column(Boolean, default=True)
    
    # Audit fields
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    bills = relationship("Bill", back_populates="vendor")

# Bills (AP)
class Bill(Base):
    __tablename__ = 'bills'
    
    id = Column(Integer, primary_key=True, index=True)
    bill_number = Column(String(50), unique=True, nullable=False)
    vendor_id = Column(Integer, ForeignKey('vendors.id'), nullable=False)
    bill_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    total_amount = Column(Numeric(15, 2), nullable=False)
    paid_amount = Column(Numeric(15, 2), default=0)
    status = Column(String(20), default='PENDING')  # PENDING, PAID, OVERDUE, CANCELLED
    
    # Audit fields
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    vendor = relationship("Vendor", back_populates="bills")
    payments = relationship("Payment", back_populates="bill")

# Customers (AR)
class Customer(Base):
    __tablename__ = 'customers'
    
    id = Column(Integer, primary_key=True, index=True)
    customer_code = Column(String(20), unique=True, nullable=False)
    customer_name = Column(String(255), nullable=False)
    contact_person = Column(String(100))
    email = Column(String(100))
    phone = Column(String(20))
    address = Column(Text)
    credit_limit = Column(Numeric(15, 2), default=0)
    is_active = Column(Boolean, default=True)
    
    # Audit fields
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    invoices = relationship("Invoice", back_populates="customer")

# Invoices (AR)
class Invoice(Base):
    __tablename__ = 'invoices'
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(50), unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    invoice_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    total_amount = Column(Numeric(15, 2), nullable=False)
    paid_amount = Column(Numeric(15, 2), default=0)
    status = Column(String(20), default='PENDING')  # PENDING, PAID, OVERDUE, CANCELLED
    
    # Audit fields
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    customer = relationship("Customer", back_populates="invoices")
    payments = relationship("Payment", back_populates="invoice")

# Payments (Both AP and AR)
class Payment(Base):
    __tablename__ = 'payments'
    
    id = Column(Integer, primary_key=True, index=True)
    payment_number = Column(String(50), unique=True, nullable=False)
    payment_date = Column(Date, nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    payment_method = Column(String(50))  # CASH, CHECK, BANK_TRANSFER, CREDIT_CARD
    reference = Column(String(100))
    
    # Links to either bill or invoice
    bill_id = Column(Integer, ForeignKey('bills.id'))
    invoice_id = Column(Integer, ForeignKey('invoices.id'))
    
    # Audit fields
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    bill = relationship("Bill", back_populates="payments")
    invoice = relationship("Invoice", back_populates="payments")

# Tax Codes
class TaxCode(Base):
    __tablename__ = 'tax_codes'
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    rate = Column(Numeric(5, 4), nullable=False)  # e.g., 0.0825 for 8.25%
    tax_type = Column(String(50))  # SALES, PURCHASE, VAT, GST
    is_active = Column(Boolean, default=True)
    
    # Audit fields
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())