import enum
from sqlalchemy import (
    Column, Integer, String, Text, Numeric, Date, DateTime, Boolean, ForeignKey, Index, 
    Enum as SQLEnum, JSON as JSONB, func, CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import relationship
from datetime import datetime, date
from decimal import Decimal
from typing import Optional

from app.core.base import Base

class BankAccountType(str, enum.Enum):
    CHECKING = "checking"
    SAVINGS = "savings"
    MONEY_MARKET = "money_market"
    CREDIT_LINE = "credit_line"
    INVESTMENT = "investment"

class BankAccountStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    CLOSED = "closed"
    FROZEN = "frozen"

class TransactionType(str, enum.Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER_IN = "transfer_in"
    TRANSFER_OUT = "transfer_out"
    FEE = "fee"
    INTEREST = "interest"
    REFUND = "refund"
    ADJUSTMENT = "adjustment"

class TransactionStatus(str, enum.Enum):
    PENDING = "pending"
    POSTED = "posted"
    CANCELLED = "cancelled"
    FAILED = "failed"

class ReconciliationStatus(str, enum.Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REVIEWED = "reviewed"

class BankAccount(Base):
    __tablename__ = "cm_bank_accounts"

    id = Column(Integer, primary_key=True, index=True)
    account_number = Column(String(50), unique=True, nullable=False, index=True)
    account_name = Column(String(255), nullable=False, index=True)
    bank_name = Column(String(255), nullable=False)
    bank_branch = Column(String(255))
    
    # Account Details
    account_type = Column(SQLEnum(BankAccountType, name="bank_account_type_enum"), nullable=False)
    status = Column(SQLEnum(BankAccountStatus, name="bank_account_status_enum"), default=BankAccountStatus.ACTIVE, index=True)
    currency_code = Column(String(3), default='USD')
    
    # Banking Information
    routing_number = Column(String(20))
    swift_code = Column(String(20))
    iban = Column(String(50))
    
    # Balance Information
    current_balance = Column(Numeric(15, 2), default=0, nullable=False)
    available_balance = Column(Numeric(15, 2), default=0, nullable=False)
    last_synced_balance = Column(Numeric(15, 2), default=0)
    last_synced_date = Column(DateTime(timezone=True))
    
    # Account Limits
    overdraft_limit = Column(Numeric(15, 2), default=0)
    daily_withdrawal_limit = Column(Numeric(15, 2))
    monthly_transaction_limit = Column(Integer)
    allow_overdraft = Column(Boolean, default=False)
    
    # Contact and Access Information
    contact_person = Column(String(255))
    contact_phone = Column(String(50))
    contact_email = Column(String(255))
    online_banking_id = Column(String(100))
    
    # Additional Information
    opening_date = Column(Date)
    closing_date = Column(Date)
    interest_rate = Column(Numeric(5, 4), default=0)
    minimum_balance = Column(Numeric(15, 2), default=0)
    
    # Custom Fields
    custom_fields = Column(JSONB)
    internal_notes = Column(Text)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    updated_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    
    # Relationships
    transactions = relationship("BankTransaction", back_populates="account", cascade="all, delete-orphan")
    reconciliations = relationship("BankReconciliation", back_populates="account", cascade="all, delete-orphan")
    cash_flows = relationship("CashFlowEntry", back_populates="account", cascade="all, delete-orphan")
    fees = relationship("BankingFee", back_populates="account", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_bank_account_status', 'status'),
        Index('idx_bank_account_type', 'account_type'),
        Index('idx_bank_account_bank', 'bank_name'),
    )

class BankTransaction(Base):
    __tablename__ = "cm_bank_transactions"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("cm_bank_accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Transaction Details
    transaction_date = Column(Date, nullable=False, index=True)
    transaction_type = Column(SQLEnum(TransactionType, name="transaction_type_enum"), nullable=False, index=True)
    status = Column(SQLEnum(TransactionStatus, name="transaction_status_enum"), default=TransactionStatus.PENDING, index=True)
    
    # Amount Information
    amount = Column(Numeric(15, 2), nullable=False)
    currency_code = Column(String(3), default='USD')
    exchange_rate = Column(Numeric(15, 6), default=1.0)
    
    # Transaction References
    reference_number = Column(String(100), index=True)
    check_number = Column(String(50))
    memo = Column(Text)
    payee = Column(String(255))
    
    # Categorization
    category_id = Column(Integer, ForeignKey("transaction_categories.id", ondelete="SET NULL"))
    gl_account_id = Column(Integer, ForeignKey("gl_accounts.id", ondelete="SET NULL"))
    
    # Reconciliation
    is_reconciled = Column(Boolean, default=False, index=True)
    reconciliation_id = Column(Integer, ForeignKey("cm_bank_reconciliations.id", ondelete="SET NULL"))
    reconciled_date = Column(Date)
    
    # Additional Information
    notes = Column(Text)
    attachments = Column(JSONB)
    metadata = Column(JSONB)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    updated_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    
    # Relationships
    account = relationship("BankAccount", back_populates="transactions")
    reconciliation = relationship("BankReconciliation", back_populates="transactions")
    
    # Indexes
    __table_args__ = (
        Index('idx_transaction_account_date', 'account_id', 'transaction_date'),
        Index('idx_transaction_type_status', 'transaction_type', 'status'),
        Index('idx_transaction_reconciled', 'is_reconciled'),
    )

class BankReconciliation(Base):
    __tablename__ = "cm_bank_reconciliations"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("cm_bank_accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Reconciliation Period
    reconciliation_date = Column(Date, nullable=False, index=True)
    statement_date = Column(Date, nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    
    # Balance Information
    statement_beginning_balance = Column(Numeric(15, 2), nullable=False)
    statement_ending_balance = Column(Numeric(15, 2), nullable=False)
    book_beginning_balance = Column(Numeric(15, 2), nullable=False)
    book_ending_balance = Column(Numeric(15, 2), nullable=False)
    
    # Reconciliation Results
    cleared_balance = Column(Numeric(15, 2), default=0)
    outstanding_deposits = Column(Numeric(15, 2), default=0)
    outstanding_withdrawals = Column(Numeric(15, 2), default=0)
    bank_adjustments = Column(Numeric(15, 2), default=0)
    book_adjustments = Column(Numeric(15, 2), default=0)
    difference = Column(Numeric(15, 2), default=0)
    
    # Status and Processing
    status = Column(SQLEnum(ReconciliationStatus, name="reconciliation_status_enum"), default=ReconciliationStatus.DRAFT, index=True)
    is_balanced = Column(Boolean, default=False, index=True)
    auto_reconciled_count = Column(Integer, default=0)
    manual_reconciled_count = Column(Integer, default=0)
    
    # Additional Information
    notes = Column(Text)
    reconciled_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    reviewed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    reviewed_date = Column(DateTime(timezone=True))
    
    # Custom Fields
    metadata = Column(JSONB)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    updated_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    
    # Relationships
    account = relationship("BankAccount", back_populates="reconciliations")
    transactions = relationship("BankTransaction", back_populates="reconciliation")
    
    # Indexes
    __table_args__ = (
        Index('idx_reconciliation_account_date', 'account_id', 'reconciliation_date'),
        Index('idx_reconciliation_status', 'status'),
        Index('idx_reconciliation_balanced', 'is_balanced'),
    )

class CashFlowEntry(Base):
    __tablename__ = "cm_cash_flow_entries"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("cm_bank_accounts.id", ondelete="CASCADE"), index=True)
    
    # Cash Flow Details
    entry_date = Column(Date, nullable=False, index=True)
    entry_type = Column(String(50), nullable=False, index=True)  # actual, forecast, budget
    flow_type = Column(String(50), nullable=False, index=True)   # inflow, outflow
    
    # Amount Information
    amount = Column(Numeric(15, 2), nullable=False)
    currency_code = Column(String(3), default='USD')
    
    # Categorization
    category = Column(String(100), index=True)
    subcategory = Column(String(100))
    source_reference = Column(String(255))  # Reference to source transaction/invoice/etc
    
    # Forecasting Information
    confidence_level = Column(Numeric(3, 2), default=1.0)  # 0.0 to 1.0
    forecast_method = Column(String(50))  # historical, trend, manual, etc
    
    # Additional Information
    description = Column(Text)
    notes = Column(Text)
    metadata = Column(JSONB)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    updated_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    
    # Relationships
    account = relationship("BankAccount", back_populates="cash_flows")
    
    # Indexes
    __table_args__ = (
        Index('idx_cash_flow_account_date', 'account_id', 'entry_date'),
        Index('idx_cash_flow_type', 'entry_type', 'flow_type'),
        Index('idx_cash_flow_category', 'category'),
    )

class BankingFee(Base):
    __tablename__ = "cm_banking_fees"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("cm_bank_accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Fee Details
    fee_date = Column(Date, nullable=False, index=True)
    fee_type = Column(String(100), nullable=False, index=True)
    fee_description = Column(Text, nullable=False)
    
    # Amount Information
    amount = Column(Numeric(15, 2), nullable=False)
    currency_code = Column(String(3), default='USD')
    
    # Fee Classification
    is_recurring = Column(Boolean, default=False, index=True)
    frequency = Column(String(20))  # monthly, quarterly, annually
    next_fee_date = Column(Date)
    
    # Processing Information
    transaction_id = Column(Integer, ForeignKey("cm_bank_transactions.id", ondelete="SET NULL"))
    is_processed = Column(Boolean, default=False, index=True)
    processed_date = Column(DateTime(timezone=True))
    
    # Additional Information
    fee_category = Column(String(100), index=True)
    waiver_reason = Column(Text)
    is_waived = Column(Boolean, default=False)
    waived_date = Column(Date)
    waived_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    
    # Custom Fields
    metadata = Column(JSONB)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    updated_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    
    # Relationships
    account = relationship("BankAccount", back_populates="fees")
    
    # Indexes
    __table_args__ = (
        Index('idx_banking_fee_account_date', 'account_id', 'fee_date'),
        Index('idx_banking_fee_type', 'fee_type'),
        Index('idx_banking_fee_recurring', 'is_recurring'),
    )

class BankStatementImport(Base):
    __tablename__ = "cm_bank_statement_imports"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("cm_bank_accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Import Details
    import_date = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    statement_date = Column(Date, nullable=False)
    file_name = Column(String(255))
    file_format = Column(String(50))  # csv, ofx, qif, etc
    
    # Import Results
    total_transactions = Column(Integer, default=0)
    imported_transactions = Column(Integer, default=0)
    duplicate_transactions = Column(Integer, default=0)
    failed_transactions = Column(Integer, default=0)
    
    # Processing Status
    status = Column(String(50), default='pending', index=True)  # pending, processing, completed, failed
    error_message = Column(Text)
    
    # Import Configuration
    import_settings = Column(JSONB)
    mapping_rules = Column(JSONB)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    
    # Relationships
    account = relationship("BankAccount")
    
    # Indexes
    __table_args__ = (
        Index('idx_statement_import_account_date', 'account_id', 'import_date'),
        Index('idx_statement_import_status', 'status'),
    )