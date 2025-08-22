"""
General Ledger models for the Paksa Financial System.
"""
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional, TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean, Column, Date, DateTime, Enum as SQLEnum, ForeignKey, 
    Numeric, String, Text, UniqueConstraint, Index
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import relationship, validates

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user_models import User

class AccountType(str, Enum):
    """Types of accounts in the chart of accounts."""
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    REVENUE = "revenue"
    EXPENSE = "expense"
    GAIN = "gain"
    LOSS = "loss"
    TEMPORARY = "temporary"  # For temporary accounts like income summary

class AccountSubType(str, Enum):
    """Subtypes for more granular account classification."""
    # Asset subtypes
    CURRENT_ASSET = "current_asset"
    FIXED_ASSET = "fixed_asset"
    INVENTORY = "inventory"
    RECEIVABLE = "receivable"
    
    # Liability subtypes
    CURRENT_LIABILITY = "current_liability"
    LONG_TERM_LIABILITY = "long_term_liability"
    PAYABLE = "payable"
    
    # Equity subtypes
    COMMON_STOCK = "common_stock"
    RETAINED_EARNINGS = "retained_earnings"
    
    # Revenue subtypes
    OPERATING_REVENUE = "operating_revenue"
    OTHER_REVENUE = "other_revenue"
    
    # Expense subtypes
    OPERATING_EXPENSE = "operating_expense"
    COGS = "cost_of_goods_sold"
    DEPRECIATION = "depreciation"
    TAX = "tax"
    
    # Other
    BANK = "bank"
    CASH = "cash"

class AccountStatus(str, Enum):
    """Status of an account."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"

class ChartOfAccounts(Base):
    """Chart of accounts model."""
    __tablename__ = "chart_of_accounts"
    __table_args__ = (
        UniqueConstraint("code", "company_id", name="uq_account_code_company"),
        {"comment": "Chart of accounts for organizing financial transactions"}
    )
    
    # Basic account information
    name = Column(String(200), nullable=False, comment="Account name")
    code = Column(String(50), nullable=False, index=True, comment="Account code (e.g., 1000, 2000)")
    description = Column(Text, nullable=True, comment="Account description")
    
    # Account classification
    account_type = Column(SQLEnum(AccountType), nullable=False, index=True, comment="Main account type")
    account_subtype = Column(SQLEnum(AccountSubType), nullable=True, index=True, comment="Account sub-type")
    
    # Account relationships
    parent_id = Column(
        PG_UUID(as_uuid=True), 
        ForeignKey("chart_of_accounts.id", ondelete="CASCADE"), 
        nullable=True,
        comment="Parent account ID for hierarchical structure"
    )
    company_id = Column(
        PG_UUID(as_uuid=True), 
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Company this account belongs to"
    )
    
    # Account settings
    is_system_account = Column(Boolean, default=False, nullable=False, comment="System-created account")
    is_tax_related = Column(Boolean, default=False, nullable=False, comment="Account is related to taxes")
    is_reconcilable = Column(Boolean, default=False, nullable=False, comment="Account can be reconciled")
    status = Column(SQLEnum(AccountStatus), default=AccountStatus.ACTIVE, nullable=False, index=True)
    
    # Financial settings
    currency_code = Column(String(3), default="USD", nullable=False, comment="ISO 4217 currency code")
    opening_balance = Column(Numeric(20, 6), default=0, nullable=False, comment="Opening balance")
    opening_balance_date = Column(Date, nullable=True, comment="Date of the opening balance")
    
    # Metadata
    metadata_ = Column("metadata", JSONB, default={}, nullable=True, comment="Additional metadata")
    
    # Relationships
    parent = relationship("ChartOfAccounts", remote_side="ChartOfAccounts.id", back_populates="children")
    children = relationship("ChartOfAccounts", back_populates="parent")
    company = relationship("Company", back_populates="chart_of_accounts")
    
    # Indexes
    __table_args__ = (
        Index("idx_account_code_company", "code", "company_id", unique=True),
        Index("idx_account_type_company", "account_type", "company_id"),
        Index("idx_account_status", "status"),
    )
    
    @validates('code')
    def validate_code(self, key, code):
        if not code:
            raise ValueError("Account code is required")
        return code.upper()
    
    def __repr__(self):
        return f"<Account {self.code} - {self.name}>"

class JournalEntryStatus(str, Enum):
    """Status of a journal entry."""
    DRAFT = "draft"
    POSTED = "posted"
    VOID = "void"
    ADJUSTING = "adjusting"
    REVERSING = "reversing"

class JournalEntry(Base):
    """Journal entry model for recording financial transactions."""
    __tablename__ = "journal_entries"
    __table_args__ = (
        {"comment": "Journal entries for recording financial transactions"}
    )
    
    # Entry identification
    entry_number = Column(String(50), unique=True, index=True, nullable=False, comment="Unique journal entry number")
    reference = Column(String(100), nullable=True, comment="External reference number")
    memo = Column(Text, nullable=True, comment="Entry description or memo")
    
    # Entry details
    entry_date = Column(Date, nullable=False, index=True, comment="Accounting date of the entry")
    posting_date = Column(Date, nullable=True, index=True, comment="Date when entry was posted")
    period_id = Column(
        PG_UUID(as_uuid=True), 
        ForeignKey("accounting_periods.id"), 
        nullable=True, 
        index=True,
        comment="Accounting period this entry belongs to"
    )
    
    # Status and type
    status = Column(SQLEnum(JournalEntryStatus), default=JournalEntryStatus.DRAFT, nullable=False, index=True)
    is_adjusting = Column(Boolean, default=False, nullable=False, comment="Is this an adjusting entry?")
    is_reversing = Column(Boolean, default=False, nullable=False, comment="Is this a reversing entry?")
    
    # Reversal information
    reversed_entry_id = Column(
        PG_UUID(as_uuid=True), 
        ForeignKey("journal_entries.id"), 
        nullable=True,
        comment="Original entry if this is a reversal"
    )
    
    # Financial details
    total_debit = Column(Numeric(20, 6), default=0, nullable=False, comment="Total debit amount")
    total_credit = Column(Numeric(20, 6), default=0, nullable=False, comment="Total credit amount")
    currency_code = Column(String(3), default="USD", nullable=False, comment="Transaction currency")
    exchange_rate = Column(Numeric(12, 6), default=1.0, nullable=False, comment="Exchange rate to base currency")
    
    # Relationships
    company_id = Column(
        PG_UUID(as_uuid=True), 
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Company this entry belongs to"
    )
    
    # Audit and metadata
    approved_by = Column(
        PG_UUID(as_uuid=True), 
        ForeignKey("users.id"), 
        nullable=True,
        comment="User who approved this entry"
    )
    metadata_ = Column("metadata", JSONB, default={}, nullable=True, comment="Additional metadata")
    
    # Relationships
    company = relationship("Company", back_populates="journal_entries")
    line_items = relationship("JournalEntryLine", back_populates="journal_entry", cascade="all, delete-orphan")
    period = relationship("AccountingPeriod", back_populates="journal_entries")
    reversed_entry = relationship("JournalEntry", remote_side="JournalEntry.id", back_populates="reversing_entries")
    reversing_entries = relationship("JournalEntry", back_populates="reversed_entry")
    approver = relationship("User", foreign_keys=[approved_by])
    
    # Indexes
    __table_args__ = (
        Index("idx_journal_entry_date", "entry_date"),
        Index("idx_journal_company_status", "company_id", "status"),
    )
    
    @validates('total_debit', 'total_credit')
    def validate_totals(self, key, value):
        if value < 0:
            raise ValueError("Amount cannot be negative")
        return value
    
    def __repr__(self):
        return f"<JournalEntry {self.entry_number} - {self.entry_date}>"

class JournalEntryLine(Base):
    """Individual line items within a journal entry."""
    __tablename__ = "journal_entry_lines"
    __table_args__ = (
        {"comment": "Individual line items within a journal entry"}
    )
    
    # Line identification
    line_number = Column(Integer, nullable=False, comment="Line number within the entry")
    
    # Entry reference
    journal_entry_id = Column(
        PG_UUID(as_uuid=True), 
        ForeignKey("journal_entries.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Parent journal entry"
    )
    
    # Account reference
    account_id = Column(
        PG_UUID(as_uuid=True), 
        ForeignKey("chart_of_accounts.id"),
        nullable=False,
        index=True,
        comment="Account this line item affects"
    )
    
    # Financial details
    debit = Column(Numeric(20, 6), default=0, nullable=False, comment="Debit amount")
    credit = Column(Numeric(20, 6), default=0, nullable=False, comment="Credit amount")
    currency_code = Column(String(3), default="USD", nullable=False, comment="Transaction currency")
    exchange_rate = Column(Numeric(12, 6), default=1.0, nullable=False, comment="Exchange rate to base currency")
    
    # Description and reference
    description = Column(Text, nullable=True, comment="Line item description")
    reference = Column(String(100), nullable=True, comment="External reference")
    
    # Tracking
    tracking_category_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("tracking_categories.id"),
        nullable=True,
        comment="Tracking category for this line"
    )
    
    # Relationships
    journal_entry = relationship("JournalEntry", back_populates="line_items")
    account = relationship("ChartOfAccounts", back_populates="journal_entry_lines")
    tracking_category = relationship("TrackingCategory", back_populates="journal_entry_lines")
    
    # Indexes
    __table_args__ = (
        Index("idx_journal_line_account", "account_id"),
        Index("idx_journal_line_tracking", "tracking_category_id"),
        UniqueConstraint("journal_entry_id", "line_number", name="uq_journal_line_number"),
    )
    
    @validates('debit', 'credit')
    def validate_amounts(self, key, value):
        if value < 0:
            raise ValueError("Amount cannot be negative")
        return value
    
    @property
    def amount(self) -> Decimal:
        """Get the effective amount (debit - credit)."""
        return self.debit - self.credit
    
    def __repr__(self):
        return f"<JournalEntryLine {self.line_number}: {self.account.code} {self.debit}/{self.credit}>"

# Add relationships to related models
ChartOfAccounts.journal_entry_lines = relationship("JournalEntryLine", back_populates="account")

class AccountingPeriod(Base):
    """Accounting period model for financial reporting."""
    __tablename__ = "accounting_periods"
    
    name = Column(String(100), nullable=False, comment="Period name (e.g., 'January 2023')")
    start_date = Column(Date, nullable=False, index=True, comment="Period start date")
    end_date = Column(Date, nullable=False, index=True, comment="Period end date")
    
    # Status
    is_closed = Column(Boolean, default=False, nullable=False, index=True, comment="Whether the period is closed")
    close_date = Column(DateTime, nullable=True, comment="When the period was closed")
    closed_by_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
        comment="User who closed the period"
    )
    
    # Company reference
    company_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Relationships
    company = relationship("Company", back_populates="accounting_periods")
    journal_entries = relationship("JournalEntry", back_populates="period")
    closed_by = relationship("User", foreign_keys=[closed_by_id])
    
    # Indexes
    __table_args__ = (
        Index("idx_period_dates", "start_date", "end_date"),
        UniqueConstraint("company_id", "start_date", "end_date", name="uq_company_period"),
    )
    
    def __repr__(self):
        return f"<AccountingPeriod {self.name} ({self.start_date} to {self.end_date})>"

class LedgerBalance(Base):
    """Stores running balances for accounts by period."""
    __tablename__ = "ledger_balances"
    
    # References
    account_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("chart_of_accounts.id"),
        primary_key=True,
        index=True,
        comment="Account ID"
    )
    period_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("accounting_periods.id"),
        primary_key=True,
        index=True,
        comment="Accounting period"
    )
    
    # Balance information
    opening_balance = Column(Numeric(20, 6), default=0, nullable=False, comment="Balance at period start")
    period_debit = Column(Numeric(20, 6), default=0, nullable=False, comment="Total debits for the period")
    period_credit = Column(Numeric(20, 6), default=0, nullable=False, comment="Total credits for the period")
    closing_balance = Column(Numeric(20, 6), default=0, nullable=False, comment="Balance at period end")
    
    # Relationships
    account = relationship("ChartOfAccounts", back_populates="ledger_balances")
    period = relationship("AccountingPeriod", back_populates="ledger_balances")
    
    # Indexes
    __table_args__ = (
        Index("idx_ledger_balance_period", "period_id"),
        Index("idx_ledger_balance_account", "account_id"),
    )

# Add relationships to related models
ChartOfAccounts.ledger_balances = relationship("LedgerBalance", back_populates="account")
AccountingPeriod.ledger_balances = relationship("LedgerBalance", back_populates="period")

class TrialBalance(Base):
    """Snapshot of account balances at a point in time."""
    __tablename__ = "trial_balances"
    
    # Identification
    name = Column(String(100), nullable=False, comment="Trial balance name")
    as_of_date = Column(Date, nullable=False, index=True, comment="Balance as of this date")
    
    # Status
    is_posted = Column(Boolean, default=False, nullable=False, index=True, comment="Whether the trial balance is final")
    posted_at = Column(DateTime, nullable=True, comment="When the trial balance was posted")
    posted_by_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
        comment="User who posted the trial balance"
    )
    
    # Company reference
    company_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Relationships
    company = relationship("Company", back_populates="trial_balances")
    accounts = relationship("TrialBalanceAccount", back_populates="trial_balance")
    posted_by = relationship("User", foreign_keys=[posted_by_id])
    
    def __repr__(self):
        return f"<TrialBalance {self.name} as of {self.as_of_date}>"

class TrialBalanceAccount(Base):
    """Account balances in a trial balance."""
    __tablename__ = "trial_balance_accounts"
    
    # References
    trial_balance_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("trial_balances.id", ondelete="CASCADE"),
        primary_key=True,
        index=True
    )
    account_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("chart_of_accounts.id"),
        primary_key=True,
        index=True
    )
    
    # Balance information
    debit_balance = Column(Numeric(20, 6), default=0, nullable=False, comment="Total debits")
    credit_balance = Column(Numeric(20, 6), default=0, nullable=False, comment="Total credits")
    
    # Relationships
    trial_balance = relationship("TrialBalance", back_populates="accounts")
    account = relationship("ChartOfAccounts")
    
    @property
    def net_balance(self) -> Decimal:
        """Calculate net balance (debit - credit)."""
        return self.debit_balance - self.credit_balance

# Add relationships to related models
TrialBalance.accounts = relationship("TrialBalanceAccount", back_populates="trial_balance")

class FinancialStatement(Base):
    """Generated financial statements."""
    __tablename__ = "financial_statements"
    
    class StatementType(str, Enum):
        BALANCE_SHEET = "balance_sheet"
        INCOME_STATEMENT = "income_statement"
        CASH_FLOW = "cash_flow"
        RETAINED_EARNINGS = "retained_earnings"
        CHANGES_IN_EQUITY = "changes_in_equity"
    
    # Identification
    name = Column(String(200), nullable=False, comment="Statement name")
    statement_type = Column(SQLEnum(StatementType), nullable=False, index=True, comment="Type of financial statement")
    
    # Period covered
    start_date = Column(Date, nullable=True, index=True, comment="Start date of the period")
    end_date = Column(Date, nullable=False, index=True, comment="End date of the period")
    
    # Status
    is_final = Column(Boolean, default=False, nullable=False, index=True, comment="Whether the statement is final")
    generated_at = Column(DateTime, nullable=False, server_default=func.now(), comment="When the statement was generated")
    generated_by_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        comment="User who generated the statement"
    )
    
    # Company reference
    company_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Statement data (stored as JSON for flexibility)
    statement_data = Column(JSONB, nullable=False, comment="Structured statement data")
    
    # Relationships
    company = relationship("Company", back_populates="financial_statements")
    generated_by = relationship("User", foreign_keys=[generated_by_id])
    
    # Indexes
    __table_args__ = (
        Index("idx_financial_statement_dates", "start_date", "end_date"),
        Index("idx_financial_statement_type", "statement_type"),
    )
    
    def __repr__(self):
        return f"<FinancialStatement {self.statement_type} for {self.end_date}>"

# Add relationships to related models
Company.financial_statements = relationship("FinancialStatement", back_populates="company")
