"""
Cash Management Module - Database Models
"""
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4

from sqlalchemy import Column, String, Numeric, Date, DateTime, ForeignKey, Text, Boolean, Enum as SQLEnum, JSON, Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import relationship, backref

from app.core.database import Base
from app.models.base import BaseModel


class BankAccountType(str, Enum):
    """Types of bank accounts."""
    CHECKING = "checking"
    SAVINGS = "savings"
    MONEY_MARKET = "money_market"
    CREDIT_CARD = "credit_card"
    LINE_OF_CREDIT = "line_of_credit"
    PAYMENT_PROCESSOR = "payment_processor"
    OTHER = "other"


class BankAccountStatus(str, Enum):
    """Status of a bank account."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    CLOSED = "closed"
    PENDING = "pending"
    SUSPENDED = "suspended"


class TransactionType(str, Enum):
    """Types of bank transactions."""
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER_IN = "transfer_in"
    TRANSFER_OUT = "transfer_out"
    FEE = "fee"
    INTEREST = "interest"
    PAYMENT = "payment"
    REFUND = "refund"
    ADJUSTMENT = "adjustment"
    OTHER = "other"


class TransactionStatus(str, Enum):
    """Status of a bank transaction."""
    PENDING = "pending"
    POSTED = "posted"
    CLEARED = "cleared"
    VOID = "void"
    RECONCILED = "reconciled"
    FAILED = "failed"


class ReconciliationStatus(str, Enum):
    """Status of a bank reconciliation."""
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ADJUSTED = "adjusted"
    CANCELLED = "cancelled"


class BankAccount(BaseModel, Base):
    """Bank account information."""
    __tablename__ = "bank_accounts"
    
    # Account Information
    name = Column(String(255), nullable=False, index=True)
    account_number = Column(String(100), nullable=False, index=True)
    account_type = Column(SQLEnum(BankAccountType), nullable=False, index=True)
    status = Column(SQLEnum(BankAccountStatus), default=BankAccountStatus.ACTIVE, index=True)
    currency = Column(String(3), default="USD", nullable=False)
    
    # Bank Information
    bank_name = Column(String(255), nullable=False)
    bank_code = Column(String(50))
    routing_number = Column(String(50))
    iban = Column(String(50))
    swift_code = Column(String(50))
    
    # Balance Information
    current_balance = Column(Numeric(19, 4), default=Decimal('0.00'), nullable=False)
    available_balance = Column(Numeric(19, 4), default=Decimal('0.00'), nullable=False)
    last_synced_balance = Column(Numeric(19, 4))
    last_synced_date = Column(DateTime)
    
    # GL Integration
    gl_account_id = Column(PG_UUID(as_uuid=True), ForeignKey('gl_accounts.id', ondelete='RESTRICT'))
    
    # Relationships
    transactions = relationship("BankTransaction", back_populates="account", cascade="all, delete-orphan")
    reconciliations = relationship("BankReconciliation", back_populates="account", cascade="all, delete-orphan")
    gl_account = relationship("GLAccount", back_populates="bank_accounts")
    
    # Metadata
    metadata_ = Column("metadata", JSONB, default=dict, nullable=False)
    
    # Indexes
    __table_args__ = (
        Index('ix_bank_accounts_bank_name_account_number', 'bank_name', 'account_number', unique=True),
    )


class BankTransaction(BaseModel, Base):
    """Bank transaction records."""
    __tablename__ = "bank_transactions"
    
    # Transaction Information
    account_id = Column(PG_UUID(as_uuid=True), ForeignKey('bank_accounts.id', ondelete='CASCADE'), nullable=False, index=True)
    transaction_date = Column(Date, nullable=False, index=True)
    posted_date = Column(Date, index=True)
    transaction_type = Column(SQLEnum(TransactionType), nullable=False, index=True)
    status = Column(SQLEnum(TransactionStatus), default=TransactionStatus.PENDING, index=True)
    
    # Amounts
    amount = Column(Numeric(19, 4), nullable=False)
    running_balance = Column(Numeric(19, 4))
    
    # Transaction Details
    reference_number = Column(String(100), index=True)
    check_number = Column(String(50), index=True)
    memo = Column(Text)
    notes = Column(Text)
    
    # Categorization
    category_id = Column(PG_UUID(as_uuid=True), ForeignKey('transaction_categories.id', ondelete='SET NULL'))
    payment_method = Column(String(100))
    payee = Column(String(255), index=True)
    
    # Reconciliation
    is_reconciled = Column(Boolean, default=False, index=True)
    reconciliation_id = Column(PG_UUID(as_uuid=True), ForeignKey('bank_reconciliations.id', ondelete='SET NULL'))
    
    # GL Integration
    gl_entry_id = Column(PG_UUID(as_uuid=True), ForeignKey('gl_journal_entries.id', ondelete='SET NULL'))
    
    # Relationships
    account = relationship("BankAccount", back_populates="transactions")
    reconciliation = relationship("BankReconciliation", back_populates="transactions")
    category = relationship("TransactionCategory", back_populates="transactions")
    gl_entry = relationship("JournalEntry", foreign_keys=[gl_entry_id])
    
    # Metadata
    metadata_ = Column("metadata", JSONB, default=dict, nullable=False)
    
    # Indexes
    __table_args__ = (
        Index('ix_bank_transactions_account_date', 'account_id', 'transaction_date'),
        Index('ix_bank_transactions_reference', 'account_id', 'reference_number', unique=True),
    )


class BankReconciliation(BaseModel, Base):
    """Bank reconciliation records."""
    __tablename__ = "bank_reconciliations"
    
    # Reconciliation Information
    account_id = Column(PG_UUID(as_uuid=True), ForeignKey('bank_accounts.id', ondelete='CASCADE'), nullable=False, index=True)
    statement_date = Column(Date, nullable=False, index=True)
    statement_ending_balance = Column(Numeric(19, 4), nullable=False)
    reconciliation_date = Column(Date, nullable=False, index=True)
    status = Column(SQLEnum(ReconciliationStatus), default=ReconciliationStatus.DRAFT, index=True)
    
    # Calculated Fields
    cleared_balance = Column(Numeric(19, 4))
    difference = Column(Numeric(19, 4))
    
    # GL Integration
    gl_entry_id = Column(PG_UUID(as_uuid=True), ForeignKey('gl_journal_entries.id', ondelete='SET NULL'))
    
    # Relationships
    account = relationship("BankAccount", back_populates="reconciliations")
    transactions = relationship("BankTransaction", back_populates="reconciliation")
    gl_entry = relationship("JournalEntry", foreign_keys=[gl_entry_id])
    
    # Metadata
    notes = Column(Text)
    metadata_ = Column("metadata", JSONB, default=dict, nullable=False)


class TransactionCategory(BaseModel, Base):
    """Transaction categories for bank transactions."""
    __tablename__ = "transaction_categories"
    
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text)
    parent_id = Column(PG_UUID(as_uuid=True), ForeignKey('transaction_categories.id', ondelete='CASCADE'))
    
    # GL Integration
    gl_account_id = Column(PG_UUID(as_uuid=True), ForeignKey('gl_accounts.id', ondelete='SET NULL'))
    
    # Relationships
    parent = relationship("TransactionCategory", remote_side="TransactionCategory.id", backref="subcategories")
    transactions = relationship("BankTransaction", back_populates="category")
    gl_account = relationship("GLAccount")
    
    # Metadata
    metadata_ = Column("metadata", JSONB, default=dict, nullable=False)


class BankIntegration(BaseModel, Base):
    """Bank integration configuration."""
    __tablename__ = "bank_integrations"
    
    name = Column(String(100), nullable=False, unique=True, index=True)
    provider = Column(String(100), nullable=False, index=True)  # e.g., 'plaid', 'stripe', 'custom'
    is_active = Column(Boolean, default=True, index=True)
    
    # Authentication
    api_key = Column(Text, nullable=True)  # Encrypted in production
    client_id = Column(Text, nullable=True)  # Encrypted in production
    secret = Column(Text, nullable=True)  # Encrypted in production
    
    # Configuration
    config = Column(JSONB, default=dict, nullable=False)
    
    # Sync Information
    last_sync = Column(DateTime)
    sync_status = Column(String(50))
    sync_interval_minutes = Column(Integer, default=1440)  # Default: 24 hours
    
    # Relationships
    accounts = relationship("BankAccount", back_populates="integration")
    
    # Metadata
    metadata_ = Column("metadata", JSONB, default=dict, nullable=False)


class BankAccountStatement(BaseModel, Base):
    """Bank account statements."""
    __tablename__ = "bank_account_statements"
    
    account_id = Column(PG_UUID(as_uuid=True), ForeignKey('bank_accounts.id', ondelete='CASCADE'), nullable=False, index=True)
    statement_date = Column(Date, nullable=False, index=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    # Balance Information
    opening_balance = Column(Numeric(19, 4), nullable=False)
    closing_balance = Column(Numeric(19, 4), nullable=False)
    
    # File Information
    file_name = Column(String(255))
    file_type = Column(String(50))  # e.g., 'pdf', 'csv', 'ofx'
    file_size = Column(Integer)  # in bytes
    file_url = Column(Text)  # URL or path to the statement file
    
    # Processing Information
    is_processed = Column(Boolean, default=False, index=True)
    processed_at = Column(DateTime)
    
    # Relationships
    account = relationship("BankAccount", back_populates="statements")
    
    # Metadata
    notes = Column(Text)
    metadata_ = Column("metadata", JSONB, default=dict, nullable=False)
    
    # Indexes
    __table_args__ = (
        Index('ix_bank_account_statements_account_date', 'account_id', 'statement_date', unique=True),
    )


# Add back-references to GL Account
from app.models.gl_models import GLAccount  # noqa: E402

if not hasattr(GLAccount, 'bank_accounts'):
    GLAccount.bank_accounts = relationship("BankAccount", back_populates="gl_account")

# Add back-reference to BankAccount for statements
BankAccount.statements = relationship("BankAccountStatement", back_populates="account", cascade="all, delete-orphan")

# Add back-reference to BankAccount for integrations
BankAccount.integration_id = Column(PG_UUID(as_uuid=True), ForeignKey('bank_integrations.id', ondelete='SET NULL'), index=True)
BankAccount.integration = relationship("BankIntegration", back_populates="accounts")
