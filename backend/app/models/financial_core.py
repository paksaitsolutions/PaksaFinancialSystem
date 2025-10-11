"""
Enhanced Financial Core Models with proper relationships and validation
"""
from sqlalchemy import Column, String, Integer, Numeric, DateTime, Boolean, Text, ForeignKey, Index
from sqlalchemy.orm import relationship, validates
from app.models.base import Base, BaseModel, AuditMixin
from datetime import datetime
import uuid
from decimal import Decimal

class FinancialCoreChartOfAccounts(BaseModel, AuditMixin):
    __tablename__ = "financial_core_chart_of_accounts"
    __table_args__ = {'extend_existing': True}
    
    account_code = Column(String(20), unique=True, nullable=False, index=True)
    account_name = Column(String(255), nullable=False)
    account_type = Column(String(50), nullable=False)  # Asset, Liability, Equity, Revenue, Expense
    parent_id = Column(String, ForeignKey("financial_core_chart_of_accounts.id"))
    is_system_account = Column(Boolean, default=False)
    normal_balance = Column(String(10), nullable=False)  # Debit, Credit
    current_balance = Column(Numeric(15, 2), default=0)
    
    # Relationships
    parent = relationship("FinancialCoreChartOfAccounts", remote_side="FinancialCoreChartOfAccounts.id")
    children = relationship("FinancialCoreChartOfAccounts", back_populates="parent")
    # Remove relationship - use unified models instead
    
    @validates('account_type')
    def validate_account_type(self, key, account_type):
        valid_types = ['Asset', 'Liability', 'Equity', 'Revenue', 'Expense']
        if account_type not in valid_types:
            raise ValueError(f"Account type must be one of: {valid_types}")
        return account_type
    
    @validates('normal_balance')
    def validate_normal_balance(self, key, normal_balance):
        if normal_balance not in ['Debit', 'Credit']:
            raise ValueError("Normal balance must be 'Debit' or 'Credit'")
        return normal_balance

# Import JournalEntry from unified models
from app.models.core_models import JournalEntry

# Use unified JournalEntryLine from core_models
from app.models.core_models import JournalEntryLine

class FinancialCoreVendor(BaseModel, AuditMixin):
    __tablename__ = "financial_core_vendors"
    __table_args__ = {'extend_existing': True}
    
    vendor_code = Column(String(20), unique=True, nullable=False)
    vendor_name = Column(String(255), nullable=False)
    contact_person = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    address = Column(Text)
    tax_id = Column(String(50))
    payment_terms = Column(String(50))
    credit_limit = Column(Numeric(15, 2), default=0)
    current_balance = Column(Numeric(15, 2), default=0)
    
    # Relationships
    bills = relationship("FinancialCoreBill", back_populates="financial_core_vendor")
    payments = relationship("VendorPayment", back_populates="financial_core_vendor")

# Customer model moved to core_models.py - using unified Customer class

class FinancialCoreBill(BaseModel, AuditMixin):
    __tablename__ = "bills"
    __table_args__ = {'extend_existing': True}
    
    bill_number = Column(String(50), unique=True, nullable=False)
    vendor_id = Column(String, ForeignKey("financial_core_vendors.id"), nullable=False)
    bill_date = Column(DateTime, nullable=False)
    due_date = Column(DateTime, nullable=False)
    total_amount = Column(Numeric(15, 2), nullable=False)
    paid_amount = Column(Numeric(15, 2), default=0)
    status = Column(String(20), default='pending')  # pending, partial, paid, overdue
    description = Column(Text)
    
    # Relationships
    financial_core_vendor = relationship("FinancialCoreVendor", back_populates="bills")
    payments = relationship("VendorPayment", back_populates="bill")
    
    @property
    def remaining_amount(self):
        return self.total_amount - self.paid_amount

class FinancialCoreInvoice(BaseModel, AuditMixin):
    __tablename__ = "invoices"
    __table_args__ = {'extend_existing': True}
    
    invoice_number = Column(String(50), unique=True, nullable=False)
    customer_id = Column(String, nullable=False)
    invoice_date = Column(DateTime, nullable=False)
    due_date = Column(DateTime, nullable=False)
    total_amount = Column(Numeric(15, 2), nullable=False)
    paid_amount = Column(Numeric(15, 2), default=0)
    status = Column(String(20), default='pending')  # pending, partial, paid, overdue
    description = Column(Text)
    
    # Relationships handled by unified models
    payments = relationship("CustomerPayment", back_populates="invoice")
    
    @property
    def remaining_amount(self):
        return self.total_amount - self.paid_amount

class VendorPayment(BaseModel, AuditMixin):
    __tablename__ = "vendor_payments"
    
    payment_number = Column(String(50), unique=True, nullable=False)
    vendor_id = Column(String, ForeignKey("financial_core_vendors.id"), nullable=False)
    bill_id = Column(String, ForeignKey("bills.id"))
    payment_date = Column(DateTime, nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    payment_method = Column(String(50))  # check, wire, ach, credit_card
    reference = Column(String(100))
    description = Column(Text)
    
    # Relationships
    financial_core_vendor = relationship("FinancialCoreVendor", back_populates="payments")
    bill = relationship("FinancialCoreBill", back_populates="payments")

class CustomerPayment(BaseModel, AuditMixin):
    __tablename__ = "customer_payments"
    
    payment_number = Column(String(50), unique=True, nullable=False)
    customer_id = Column(String, nullable=False)
    invoice_id = Column(String, ForeignKey("invoices.id"))
    payment_date = Column(DateTime, nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    payment_method = Column(String(50))  # check, wire, ach, credit_card
    reference = Column(String(100))
    description = Column(Text)
    
    # Relationships handled by unified models
    invoice = relationship("FinancialCoreInvoice", back_populates="payments")

# Currency model moved to app.models.currency - avoiding duplicate table definition

class FinancialCoreExchangeRate(BaseModel):
    __tablename__ = "financial_core_exchange_rates"
    __table_args__ = {'extend_existing': True}
    
    from_currency = Column(String(3), nullable=False)
    to_currency = Column(String(3), nullable=False)
    rate = Column(Numeric(15, 6), nullable=False)
    rate_date = Column(DateTime, nullable=False)
    source = Column(String(50))  # manual, api, bank
    
    @validates('rate')
    def validate_rate(self, key, rate):
        if rate <= 0:
            raise ValueError("Exchange rate must be positive")
        return rate

# TaxRate moved to core_models.py for unified definition

class PeriodClose(BaseModel, AuditMixin):
    __tablename__ = "period_closes"
    
    period_name = Column(String(50), nullable=False)  # 2024-01, Q1-2024
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    status = Column(String(20), default='open')  # open, closing, closed
    closed_by = Column(String)
    closed_at = Column(DateTime)
    net_income = Column(Numeric(15, 2))
    total_revenue = Column(Numeric(15, 2))
    total_expenses = Column(Numeric(15, 2))
    closing_entries = Column(Text)  # JSON array of closing entry IDs

class BankReconciliation(BaseModel, AuditMixin):
    __tablename__ = "bank_reconciliations"
    
    bank_account_id = Column(String, ForeignKey("financial_core_chart_of_accounts.id"), nullable=False)
    statement_date = Column(DateTime, nullable=False)
    statement_balance = Column(Numeric(15, 2), nullable=False)
    book_balance = Column(Numeric(15, 2), nullable=False)
    reconciliation_difference = Column(Numeric(15, 2), default=0)
    status = Column(String(20), default='pending')  # pending, reconciled, adjusted
    reconciled_by = Column(String)
    reconciled_at = Column(DateTime)
    adjustment_entries = Column(Text)  # JSON array of adjustment entry IDs
    
    # Relationships
    bank_account = relationship("FinancialCoreChartOfAccounts")

class FinancialPeriod(BaseModel, AuditMixin):
    __tablename__ = "financial_periods"
    __table_args__ = {'extend_existing': True}
    
    period_name = Column(String(50), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    is_current = Column(Boolean, default=False)
    is_closed = Column(Boolean, default=False)
    closed_at = Column(DateTime)

# Indexes for performance
Index('idx_journal_entry_date', JournalEntry.entry_date)
Index('idx_journal_entry_status', JournalEntry.status)
Index('idx_bill_due_date', FinancialCoreBill.due_date)
Index('idx_invoice_due_date', FinancialCoreInvoice.due_date)
Index('idx_account_code', FinancialCoreChartOfAccounts.account_code)
Index('idx_financial_core_exchange_rate_date', FinancialCoreExchangeRate.rate_date)
# Tax rate index moved to core_models.py
Index('idx_period_close_dates', PeriodClose.period_start, PeriodClose.period_end)