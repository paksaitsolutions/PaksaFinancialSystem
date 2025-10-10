"""
Enhanced Financial Core Models with proper relationships and validation
"""
from sqlalchemy import Column, String, Integer, Numeric, DateTime, Boolean, Text, ForeignKey, Index
from sqlalchemy.orm import relationship, validates
from app.models.base import Base, BaseModel, AuditMixin
from datetime import datetime
import uuid
from decimal import Decimal

class ChartOfAccounts(BaseModel, AuditMixin):
    __tablename__ = "chart_of_accounts"
    __table_args__ = {'extend_existing': True}
    
    account_code = Column(String(20), unique=True, nullable=False, index=True)
    account_name = Column(String(255), nullable=False)
    account_type = Column(String(50), nullable=False)  # Asset, Liability, Equity, Revenue, Expense
    parent_id = Column(String, ForeignKey("chart_of_accounts.id"))
    is_system_account = Column(Boolean, default=False)
    normal_balance = Column(String(10), nullable=False)  # Debit, Credit
    current_balance = Column(Numeric(15, 2), default=0)
    
    # Relationships
    parent = relationship("ChartOfAccounts", remote_side=[id])
    children = relationship("ChartOfAccounts", back_populates="parent")
    journal_lines = relationship("JournalEntryLine", back_populates="account")
    
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

class JournalEntry(BaseModel, AuditMixin):
    __tablename__ = "journal_entries"
    __table_args__ = {'extend_existing': True}
    
    entry_number = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=False)
    reference = Column(String(100))
    entry_date = Column(DateTime, nullable=False)
    status = Column(String(20), default='draft')  # draft, pending, approved, posted
    total_debit = Column(Numeric(15, 2), default=0)
    total_credit = Column(Numeric(15, 2), default=0)
    approved_by = Column(String)
    posted_by = Column(String)
    approved_at = Column(DateTime)
    posted_at = Column(DateTime)
    
    # Relationships
    lines = relationship("JournalEntryLine", back_populates="journal_entry", cascade="all, delete-orphan")
    
    @validates('status')
    def validate_status(self, key, status):
        valid_statuses = ['draft', 'pending', 'approved', 'posted']
        if status not in valid_statuses:
            raise ValueError(f"Status must be one of: {valid_statuses}")
        return status
    
    def validate_balanced_entry(self):
        """Ensure journal entry is balanced"""
        if abs(self.total_debit - self.total_credit) > Decimal('0.01'):
            raise ValueError("Journal entry must be balanced (debits = credits)")

class JournalEntryLine(BaseModel):
    __tablename__ = "journal_entry_lines"
    __table_args__ = {'extend_existing': True}
    
    journal_entry_id = Column(String, ForeignKey("journal_entries.id"), nullable=False)
    account_id = Column(String, ForeignKey("chart_of_accounts.id"), nullable=False)
    description = Column(String(255))
    debit_amount = Column(Numeric(15, 2), default=0)
    credit_amount = Column(Numeric(15, 2), default=0)
    line_number = Column(Integer, nullable=False)
    
    # Relationships
    journal_entry = relationship("JournalEntry", back_populates="lines")
    account = relationship("ChartOfAccounts", back_populates="journal_lines")
    
    @validates('debit_amount', 'credit_amount')
    def validate_amounts(self, key, amount):
        if amount < 0:
            raise ValueError("Amounts cannot be negative")
        return amount
    
    def validate_debit_credit_exclusive(self):
        """Ensure only debit OR credit is entered, not both"""
        if self.debit_amount > 0 and self.credit_amount > 0:
            raise ValueError("Cannot have both debit and credit amounts")
        if self.debit_amount == 0 and self.credit_amount == 0:
            raise ValueError("Must have either debit or credit amount")

class Vendor(BaseModel, AuditMixin):
    __tablename__ = "vendors"
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
    bills = relationship("Bill", back_populates="vendor")
    payments = relationship("VendorPayment", back_populates="vendor")

class Customer(BaseModel, AuditMixin):
    __tablename__ = "customers"
    __table_args__ = {'extend_existing': True}
    
    customer_code = Column(String(20), unique=True, nullable=False)
    customer_name = Column(String(255), nullable=False)
    contact_person = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    address = Column(Text)
    tax_id = Column(String(50))
    payment_terms = Column(String(50))
    credit_limit = Column(Numeric(15, 2), default=0)
    current_balance = Column(Numeric(15, 2), default=0)
    
    # Relationships
    invoices = relationship("Invoice", back_populates="customer")
    payments = relationship("CustomerPayment", back_populates="customer")

class Bill(BaseModel, AuditMixin):
    __tablename__ = "bills"
    __table_args__ = {'extend_existing': True}
    
    bill_number = Column(String(50), unique=True, nullable=False)
    vendor_id = Column(String, ForeignKey("vendors.id"), nullable=False)
    bill_date = Column(DateTime, nullable=False)
    due_date = Column(DateTime, nullable=False)
    total_amount = Column(Numeric(15, 2), nullable=False)
    paid_amount = Column(Numeric(15, 2), default=0)
    status = Column(String(20), default='pending')  # pending, partial, paid, overdue
    description = Column(Text)
    
    # Relationships
    vendor = relationship("Vendor", back_populates="bills")
    payments = relationship("VendorPayment", back_populates="bill")
    
    @property
    def remaining_amount(self):
        return self.total_amount - self.paid_amount

class Invoice(BaseModel, AuditMixin):
    __tablename__ = "invoices"
    __table_args__ = {'extend_existing': True}
    
    invoice_number = Column(String(50), unique=True, nullable=False)
    customer_id = Column(String, ForeignKey("customers.id"), nullable=False)
    invoice_date = Column(DateTime, nullable=False)
    due_date = Column(DateTime, nullable=False)
    total_amount = Column(Numeric(15, 2), nullable=False)
    paid_amount = Column(Numeric(15, 2), default=0)
    status = Column(String(20), default='pending')  # pending, partial, paid, overdue
    description = Column(Text)
    
    # Relationships
    customer = relationship("Customer", back_populates="invoices")
    payments = relationship("CustomerPayment", back_populates="invoice")
    
    @property
    def remaining_amount(self):
        return self.total_amount - self.paid_amount

class VendorPayment(BaseModel, AuditMixin):
    __tablename__ = "vendor_payments"
    
    payment_number = Column(String(50), unique=True, nullable=False)
    vendor_id = Column(String, ForeignKey("vendors.id"), nullable=False)
    bill_id = Column(String, ForeignKey("bills.id"))
    payment_date = Column(DateTime, nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    payment_method = Column(String(50))  # check, wire, ach, credit_card
    reference = Column(String(100))
    description = Column(Text)
    
    # Relationships
    vendor = relationship("Vendor", back_populates="payments")
    bill = relationship("Bill", back_populates="payments")

class CustomerPayment(BaseModel, AuditMixin):
    __tablename__ = "customer_payments"
    
    payment_number = Column(String(50), unique=True, nullable=False)
    customer_id = Column(String, ForeignKey("customers.id"), nullable=False)
    invoice_id = Column(String, ForeignKey("invoices.id"))
    payment_date = Column(DateTime, nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    payment_method = Column(String(50))  # check, wire, ach, credit_card
    reference = Column(String(100))
    description = Column(Text)
    
    # Relationships
    customer = relationship("Customer", back_populates="payments")
    invoice = relationship("Invoice", back_populates="payments")

# Currency model moved to app.models.currency - avoiding duplicate table definition

class ExchangeRate(BaseModel):
    __tablename__ = "exchange_rates"
    
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

class TaxRate(BaseModel, AuditMixin):
    __tablename__ = "tax_rates"
    __table_args__ = {'extend_existing': True}
    
    tax_code = Column(String(20), unique=True, nullable=False)
    tax_name = Column(String(100), nullable=False)
    rate_percentage = Column(Numeric(5, 4), nullable=False)  # 8.25% = 8.2500
    tax_type = Column(String(50), nullable=False)  # sales, vat, income, property
    jurisdiction = Column(String(100))  # state, country, city
    effective_date = Column(DateTime, nullable=False)
    expiry_date = Column(DateTime)
    
    @validates('rate_percentage')
    def validate_rate(self, key, rate):
        if rate < 0 or rate > 100:
            raise ValueError("Tax rate must be between 0 and 100")
        return rate

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
    
    bank_account_id = Column(String, ForeignKey("chart_of_accounts.id"), nullable=False)
    statement_date = Column(DateTime, nullable=False)
    statement_balance = Column(Numeric(15, 2), nullable=False)
    book_balance = Column(Numeric(15, 2), nullable=False)
    reconciliation_difference = Column(Numeric(15, 2), default=0)
    status = Column(String(20), default='pending')  # pending, reconciled, adjusted
    reconciled_by = Column(String)
    reconciled_at = Column(DateTime)
    adjustment_entries = Column(Text)  # JSON array of adjustment entry IDs
    
    # Relationships
    bank_account = relationship("ChartOfAccounts")

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
Index('idx_bill_due_date', Bill.due_date)
Index('idx_invoice_due_date', Invoice.due_date)
Index('idx_account_code', ChartOfAccounts.account_code)
Index('idx_exchange_rate_date', ExchangeRate.rate_date)
Index('idx_tax_rate_effective', TaxRate.effective_date)
Index('idx_period_close_dates', PeriodClose.period_start, PeriodClose.period_end)