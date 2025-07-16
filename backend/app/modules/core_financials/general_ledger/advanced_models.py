"""
Advanced General Ledger Models
Multi-dimensional COA, real-time processing, and comprehensive audit trails
"""

from sqlalchemy import Column, Integer, String, Text, Decimal, DateTime, Date, Boolean, ForeignKey, Enum as SQLEnum, JSON, Index, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.models.base import Base
import enum
import uuid
from datetime import datetime, date
from decimal import Decimal as D

class AccountType(enum.Enum):
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    REVENUE = "revenue"
    EXPENSE = "expense"
    CONTRA_ASSET = "contra_asset"
    CONTRA_LIABILITY = "contra_liability"
    CONTRA_EQUITY = "contra_equity"
    CONTRA_REVENUE = "contra_revenue"

class AccountSubType(enum.Enum):
    # Assets
    CURRENT_ASSET = "current_asset"
    FIXED_ASSET = "fixed_asset"
    INTANGIBLE_ASSET = "intangible_asset"
    OTHER_ASSET = "other_asset"
    
    # Liabilities
    CURRENT_LIABILITY = "current_liability"
    LONG_TERM_LIABILITY = "long_term_liability"
    OTHER_LIABILITY = "other_liability"
    
    # Equity
    PAID_IN_CAPITAL = "paid_in_capital"
    RETAINED_EARNINGS = "retained_earnings"
    OTHER_EQUITY = "other_equity"
    
    # Revenue
    OPERATING_REVENUE = "operating_revenue"
    NON_OPERATING_REVENUE = "non_operating_revenue"
    
    # Expenses
    COST_OF_GOODS_SOLD = "cost_of_goods_sold"
    OPERATING_EXPENSE = "operating_expense"
    NON_OPERATING_EXPENSE = "non_operating_expense"

class JournalEntryStatus(enum.Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    POSTED = "posted"
    REVERSED = "reversed"
    CANCELLED = "cancelled"

class JournalEntryType(enum.Enum):
    MANUAL = "manual"
    AUTOMATIC = "automatic"
    RECURRING = "recurring"
    REVERSING = "reversing"
    ACCRUAL = "accrual"
    DEFERRAL = "deferral"
    DEPRECIATION = "depreciation"
    REVALUATION = "revaluation"
    CONSOLIDATION = "consolidation"
    ELIMINATION = "elimination"

class PeriodStatus(enum.Enum):
    OPEN = "open"
    CLOSED = "closed"
    LOCKED = "locked"

# Enhanced Chart of Accounts with Multi-Dimensional Support
class GLAccount(Base):
    __tablename__ = "gl_accounts_advanced"
    
    id = Column(Integer, primary_key=True, index=True)
    account_code = Column(String(20), unique=True, nullable=False, index=True)
    account_name = Column(String(255), nullable=False, index=True)
    account_type = Column(SQLEnum(AccountType), nullable=False)
    account_subtype = Column(SQLEnum(AccountSubType), nullable=False)
    
    # Hierarchical Structure
    parent_account_id = Column(Integer, ForeignKey("gl_accounts_advanced.id"))
    level = Column(Integer, default=0)
    path = Column(String(500))  # Materialized path for hierarchy
    
    # Multi-Dimensional Attributes
    department_required = Column(Boolean, default=False)
    cost_center_required = Column(Boolean, default=False)
    project_required = Column(Boolean, default=False)
    location_required = Column(Boolean, default=False)
    product_required = Column(Boolean, default=False)
    
    # Financial Attributes
    normal_balance = Column(String(10), nullable=False)  # 'debit' or 'credit'
    is_active = Column(Boolean, default=True)
    is_control_account = Column(Boolean, default=False)
    subsidiary_ledger_type = Column(String(50))  # 'ar', 'ap', 'inventory', etc.
    
    # Currency and Multi-Currency
    currency_code = Column(String(3), default='USD')
    allow_multi_currency = Column(Boolean, default=False)
    
    # Budgeting and Planning
    budget_enabled = Column(Boolean, default=True)
    statistical_account = Column(Boolean, default=False)  # For non-monetary data
    
    # Consolidation and Reporting
    consolidation_account = Column(String(20))
    financial_statement_line = Column(String(100))
    report_category = Column(String(100))
    
    # Compliance and Controls
    requires_approval = Column(Boolean, default=False)
    approval_limit = Column(Decimal(15, 2))
    tax_relevant = Column(Boolean, default=False)
    
    # Metadata
    description = Column(Text)
    tags = Column(JSONB)
    custom_attributes = Column(JSONB)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    parent_account = relationship("GLAccount", remote_side=[id])
    child_accounts = relationship("GLAccount")
    journal_entries = relationship("GLJournalEntry", back_populates="account")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_account_type_subtype', 'account_type', 'account_subtype'),
        Index('idx_account_hierarchy', 'parent_account_id', 'level'),
        Index('idx_account_active', 'is_active', 'account_type'),
        CheckConstraint('normal_balance IN (\'debit\', \'credit\')', name='check_normal_balance'),
    )

# Dimensional Attributes for Multi-Dimensional Reporting
class GLDimension(Base):
    __tablename__ = "gl_dimensions"
    
    id = Column(Integer, primary_key=True, index=True)
    dimension_type = Column(String(50), nullable=False)  # 'department', 'cost_center', 'project', etc.
    dimension_code = Column(String(20), nullable=False)
    dimension_name = Column(String(255), nullable=False)
    parent_dimension_id = Column(Integer, ForeignKey("gl_dimensions.id"))
    is_active = Column(Boolean, default=True)
    
    # Hierarchical support for dimensions
    level = Column(Integer, default=0)
    path = Column(String(500))
    
    # Metadata
    description = Column(Text)
    attributes = Column(JSONB)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    parent_dimension = relationship("GLDimension", remote_side=[id])
    child_dimensions = relationship("GLDimension")
    
    __table_args__ = (
        Index('idx_dimension_type_code', 'dimension_type', 'dimension_code'),
        Index('idx_dimension_active', 'is_active', 'dimension_type'),
    )

# Enhanced Journal Entry with Multi-Dimensional Support
class GLJournalEntry(Base):
    __tablename__ = "gl_journal_entries_advanced"
    
    id = Column(Integer, primary_key=True, index=True)
    entry_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Entry Classification
    entry_type = Column(SQLEnum(JournalEntryType), nullable=False)
    status = Column(SQLEnum(JournalEntryStatus), default=JournalEntryStatus.DRAFT)
    
    # Dates and Periods
    entry_date = Column(Date, nullable=False)
    posting_date = Column(Date)
    period_id = Column(Integer, ForeignKey("gl_periods.id"), nullable=False)
    
    # Financial Information
    total_debit = Column(Decimal(15, 2), nullable=False, default=0)
    total_credit = Column(Decimal(15, 2), nullable=False, default=0)
    currency_code = Column(String(3), default='USD')
    exchange_rate = Column(Decimal(10, 6), default=1.0)
    
    # Source and Reference
    source_module = Column(String(50))  # 'ap', 'ar', 'cash', 'payroll', etc.
    source_document_type = Column(String(50))
    source_document_id = Column(Integer)
    reference_number = Column(String(100))
    
    # Recurring Entry Support
    recurring_template_id = Column(Integer, ForeignKey("gl_recurring_templates.id"))
    recurring_sequence = Column(Integer)
    
    # Reversal Support
    reversed_entry_id = Column(Integer, ForeignKey("gl_journal_entries_advanced.id"))
    reversal_date = Column(Date)
    auto_reverse_date = Column(Date)
    
    # Approval Workflow
    requires_approval = Column(Boolean, default=False)
    approved_by = Column(Integer, ForeignKey("users.id"))
    approved_at = Column(DateTime(timezone=True))
    approval_notes = Column(Text)
    
    # Description and Notes
    description = Column(Text, nullable=False)
    notes = Column(Text)
    
    # Metadata
    tags = Column(JSONB)
    custom_fields = Column(JSONB)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_by = Column(Integer, ForeignKey("users.id"))
    posted_by = Column(Integer, ForeignKey("users.id"))
    posted_at = Column(DateTime(timezone=True))
    
    # Relationships
    period = relationship("GLPeriod", back_populates="journal_entries")
    lines = relationship("GLJournalEntryLine", back_populates="journal_entry", cascade="all, delete-orphan")
    recurring_template = relationship("GLRecurringTemplate", back_populates="entries")
    reversed_entry = relationship("GLJournalEntry", remote_side=[id])
    
    # Indexes
    __table_args__ = (
        Index('idx_entry_date_period', 'entry_date', 'period_id'),
        Index('idx_entry_status_type', 'status', 'entry_type'),
        Index('idx_entry_source', 'source_module', 'source_document_type', 'source_document_id'),
        CheckConstraint('total_debit = total_credit', name='check_balanced_entry'),
    )

# Enhanced Journal Entry Lines with Multi-Dimensional Support
class GLJournalEntryLine(Base):
    __tablename__ = "gl_journal_entry_lines_advanced"
    
    id = Column(Integer, primary_key=True, index=True)
    journal_entry_id = Column(Integer, ForeignKey("gl_journal_entries_advanced.id"), nullable=False)
    line_number = Column(Integer, nullable=False)
    
    # Account Information
    account_id = Column(Integer, ForeignKey("gl_accounts_advanced.id"), nullable=False)
    
    # Multi-Dimensional Attributes
    department_id = Column(Integer, ForeignKey("gl_dimensions.id"))
    cost_center_id = Column(Integer, ForeignKey("gl_dimensions.id"))
    project_id = Column(Integer, ForeignKey("gl_dimensions.id"))
    location_id = Column(Integer, ForeignKey("gl_dimensions.id"))
    product_id = Column(Integer, ForeignKey("gl_dimensions.id"))
    
    # Additional Dimensions (flexible)
    dimension_1_id = Column(Integer, ForeignKey("gl_dimensions.id"))
    dimension_2_id = Column(Integer, ForeignKey("gl_dimensions.id"))
    dimension_3_id = Column(Integer, ForeignKey("gl_dimensions.id"))
    
    # Financial Amounts
    debit_amount = Column(Decimal(15, 2), default=0)
    credit_amount = Column(Decimal(15, 2), default=0)
    
    # Multi-Currency Support
    currency_code = Column(String(3), default='USD')
    exchange_rate = Column(Decimal(10, 6), default=1.0)
    base_currency_debit = Column(Decimal(15, 2), default=0)
    base_currency_credit = Column(Decimal(15, 2), default=0)
    
    # Line Description and Reference
    description = Column(Text)
    reference = Column(String(255))
    
    # Tax Information
    tax_code = Column(String(20))
    tax_amount = Column(Decimal(15, 2), default=0)
    
    # Metadata
    line_attributes = Column(JSONB)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    journal_entry = relationship("GLJournalEntry", back_populates="lines")
    account = relationship("GLAccount", back_populates="journal_entries")
    department = relationship("GLDimension", foreign_keys=[department_id])
    cost_center = relationship("GLDimension", foreign_keys=[cost_center_id])
    project = relationship("GLDimension", foreign_keys=[project_id])
    location = relationship("GLDimension", foreign_keys=[location_id])
    product = relationship("GLDimension", foreign_keys=[product_id])
    
    # Indexes
    __table_args__ = (
        Index('idx_line_account_date', 'account_id', 'journal_entry_id'),
        Index('idx_line_dimensions', 'department_id', 'cost_center_id', 'project_id'),
        CheckConstraint('(debit_amount > 0 AND credit_amount = 0) OR (credit_amount > 0 AND debit_amount = 0)', 
                       name='check_debit_or_credit'),
    )

# Accounting Periods Management
class GLPeriod(Base):
    __tablename__ = "gl_periods"
    
    id = Column(Integer, primary_key=True, index=True)
    period_name = Column(String(50), nullable=False)
    fiscal_year = Column(Integer, nullable=False)
    period_number = Column(Integer, nullable=False)
    
    # Period Dates
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    # Period Status
    status = Column(SQLEnum(PeriodStatus), default=PeriodStatus.OPEN)
    
    # Close Process
    closed_by = Column(Integer, ForeignKey("users.id"))
    closed_at = Column(DateTime(timezone=True))
    close_notes = Column(Text)
    
    # Adjustments allowed after close
    allow_adjustments = Column(Boolean, default=False)
    adjustment_cutoff_date = Column(Date)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    journal_entries = relationship("GLJournalEntry", back_populates="period")
    
    __table_args__ = (
        Index('idx_period_fiscal_year', 'fiscal_year', 'period_number'),
        Index('idx_period_dates', 'start_date', 'end_date'),
    )

# Recurring Journal Entry Templates
class GLRecurringTemplate(Base):
    __tablename__ = "gl_recurring_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    template_name = Column(String(255), nullable=False)
    template_code = Column(String(50), unique=True, nullable=False)
    
    # Recurrence Pattern
    frequency = Column(String(20), nullable=False)  # 'monthly', 'quarterly', 'annually'
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    next_run_date = Column(Date)
    
    # Template Configuration
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    auto_post = Column(Boolean, default=False)
    
    # Approval Requirements
    requires_approval = Column(Boolean, default=False)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    entries = relationship("GLJournalEntry", back_populates="recurring_template")
    template_lines = relationship("GLRecurringTemplateLine", back_populates="template", cascade="all, delete-orphan")

class GLRecurringTemplateLine(Base):
    __tablename__ = "gl_recurring_template_lines"
    
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("gl_recurring_templates.id"), nullable=False)
    line_number = Column(Integer, nullable=False)
    
    # Account and Dimensions
    account_id = Column(Integer, ForeignKey("gl_accounts_advanced.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("gl_dimensions.id"))
    cost_center_id = Column(Integer, ForeignKey("gl_dimensions.id"))
    project_id = Column(Integer, ForeignKey("gl_dimensions.id"))
    
    # Amount Configuration
    debit_amount = Column(Decimal(15, 2), default=0)
    credit_amount = Column(Decimal(15, 2), default=0)
    amount_formula = Column(String(500))  # For calculated amounts
    
    # Line Details
    description = Column(Text)
    reference = Column(String(255))
    
    # Relationships
    template = relationship("GLRecurringTemplate", back_populates="template_lines")
    account = relationship("GLAccount")

# Account Balances - Real-time balance tracking
class GLAccountBalance(Base):
    __tablename__ = "gl_account_balances"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("gl_accounts_advanced.id"), nullable=False)
    period_id = Column(Integer, ForeignKey("gl_periods.id"), nullable=False)
    
    # Multi-Dimensional Balance Tracking
    department_id = Column(Integer, ForeignKey("gl_dimensions.id"))
    cost_center_id = Column(Integer, ForeignKey("gl_dimensions.id"))
    project_id = Column(Integer, ForeignKey("gl_dimensions.id"))
    
    # Balance Amounts
    beginning_balance_debit = Column(Decimal(15, 2), default=0)
    beginning_balance_credit = Column(Decimal(15, 2), default=0)
    period_debit = Column(Decimal(15, 2), default=0)
    period_credit = Column(Decimal(15, 2), default=0)
    ending_balance_debit = Column(Decimal(15, 2), default=0)
    ending_balance_credit = Column(Decimal(15, 2), default=0)
    
    # Multi-Currency Balances
    currency_code = Column(String(3), default='USD')
    base_currency_ending_balance = Column(Decimal(15, 2), default=0)
    
    # Balance Metadata
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    account = relationship("GLAccount")
    period = relationship("GLPeriod")
    
    __table_args__ = (
        Index('idx_balance_account_period', 'account_id', 'period_id'),
        Index('idx_balance_dimensions', 'department_id', 'cost_center_id', 'project_id'),
    )

# Integration Tracking - Audit trail for module integrations
class GLIntegrationLog(Base):
    __tablename__ = "gl_integration_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Source Information
    source_module = Column(String(50), nullable=False)
    source_transaction_type = Column(String(50), nullable=False)
    source_transaction_id = Column(Integer, nullable=False)
    
    # GL Impact
    journal_entry_id = Column(Integer, ForeignKey("gl_journal_entries_advanced.id"))
    
    # Integration Status
    status = Column(String(20), default='pending')  # 'pending', 'posted', 'failed', 'reversed'
    error_message = Column(Text)
    
    # Processing Information
    processed_at = Column(DateTime(timezone=True))
    retry_count = Column(Integer, default=0)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    journal_entry = relationship("GLJournalEntry")
    
    __table_args__ = (
        Index('idx_integration_source', 'source_module', 'source_transaction_type', 'source_transaction_id'),
        Index('idx_integration_status', 'status', 'created_at'),
    )