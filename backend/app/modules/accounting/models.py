"""
Accounting models for the financial system.
"""
from datetime import datetime
from decimal import Decimal
from enum import Enum, auto
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean, 
    CheckConstraint, 
    Column, 
    DateTime, 
    Enum as SQLEnum, 
    ForeignKey, 
    Numeric, 
    String, 
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


class AccountType(str, Enum):
    """Types of accounts in the chart of accounts."""
    ASSET = 'asset'
    LIABILITY = 'liability'
    EQUITY = 'equity'
    REVENUE = 'revenue'
    EXPENSE = 'expense'
    GAIN = 'gain'
    LOSS = 'loss'
    TEMPORARY = 'temporary'  # For temporary accounts like income summary


class AccountSubType(str, Enum):
    """Subtypes for more detailed account classification."""
    # Asset subtypes
    CURRENT_ASSET = 'current_asset'
    FIXED_ASSET = 'fixed_asset'
    INTANGIBLE_ASSET = 'intangible_asset'
    PREPAID_EXPENSE = 'prepaid_expense'
    INVENTORY = 'inventory'
    RECEIVABLE = 'receivable'
    
    # Liability subtypes
    CURRENT_LIABILITY = 'current_liability'
    LONG_TERM_LIABILITY = 'long_term_liability'
    
    # Equity subtypes
    RETAINED_EARNINGS = 'retained_earnings'
    COMMON_STOCK = 'common_stock'
    PREFERRED_STOCK = 'preferred_stock'
    
    # Revenue/Expense subtypes
    OPERATING_REVENUE = 'operating_revenue'
    OTHER_REVENUE = 'other_revenue'
    COST_OF_GOODS_SOLD = 'cogs'
    OPERATING_EXPENSE = 'operating_expense'
    DEPRECIATION = 'depreciation'
    AMORTIZATION = 'amortization'
    INTEREST = 'interest'
    TAX = 'tax'


class AccountStatus(str, Enum):
    """Status of an account."""
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    CLOSED = 'closed'


class Account(Base):
    """Chart of accounts model."""
    __tablename__ = 'account'
    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # Account classification
    type: Mapped[AccountType] = mapped_column(SQLEnum(AccountType), nullable=False)
    subtype: Mapped[Optional[AccountSubType]] = mapped_column(SQLEnum(AccountSubType))
    
    # Financial properties
    currency: Mapped[str] = mapped_column(String(3), default='USD', nullable=False)
    is_contra: Mapped[bool] = mapped_column(Boolean, default=False)
    is_system_account: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Account hierarchy
    parent_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('account.id'))
    parent: Mapped[Optional['Account']] = relationship(
        'Account', 
        remote_side=[id],
        back_populates='children',
    )
    children: Mapped[List['Account']] = relationship(
        'Account',
        back_populates='parent',
        cascade='all, delete-orphan',
    )
    
    # Account status
    status: Mapped[AccountStatus] = mapped_column(
        SQLEnum(AccountStatus), 
        default=AccountStatus.ACTIVE,
        nullable=False,
    )
    
    # Audit fields
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now(),
    )
    
    # Relationships
    journal_entries: Mapped[List['JournalEntryLine']] = relationship(
        'JournalEntryLine', 
        back_populates='account',
    )
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            'char_length(code) >= 2', 
            name='account_code_min_length'
        ),
        UniqueConstraint('code', 'currency', name='unique_account_code_currency'),
    )
    
    def __repr__(self) -> str:
        return f'<Account {self.code} - {self.name}>'
    
    @property
    def full_code(self) -> str:
        """Get the full account code including parent codes."""
        if self.parent:
            return f'{self.parent.full_code}.{self.code}'
        return self.code
    
    @property
    def normal_balance(self) -> str:
        """Get the normal balance side for this account type (debit/credit)."""
        if self.type in (AccountType.ASSET, AccountType.EXPENSE, AccountType.LOSS):
            return 'debit'
        return 'credit'


class JournalEntryStatus(str, Enum):
    """Status of a journal entry."""
    DRAFT = 'draft'
    POSTED = 'posted'
    ADJUSTING = 'adjusting'
    REVERSING = 'reversing'
    VOID = 'void'


class JournalEntry(Base):
    """Journal entry model for recording financial transactions."""
    __tablename__ = 'journal_entry'
    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    entry_number: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    entry_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    reference: Mapped[Optional[str]] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # Status and type
    status: Mapped[JournalEntryStatus] = mapped_column(
        SQLEnum(JournalEntryStatus),
        default=JournalEntryStatus.DRAFT,
        nullable=False,
    )
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    is_reversed: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Totals
    total_debit: Mapped[Decimal] = mapped_column(Numeric(19, 4), default=0)
    total_credit: Mapped[Decimal] = mapped_column(Numeric(19, 4), default=0)
    
    # Audit fields
    posted_at: Mapped[Optional[datetime]]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now(),
    )
    
    # Relationships
    lines: Mapped[List['JournalEntryLine']] = relationship(
        'JournalEntryLine', 
        back_populates='journal_entry',
        cascade='all, delete-orphan',
    )
    
    # Created by/updated by
    created_by_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('user.id'))
    updated_by_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('user.id'))
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            'total_debit = total_credit',
            name='debit_credit_balance',
        ),
    )
    
    def __repr__(self) -> str:
        return f'<JournalEntry {self.entry_number}>'


class JournalEntryLine(Base):
    """Individual line items within a journal entry."""
    __tablename__ = 'journal_entry_line'
    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    line_number: Mapped[int] = mapped_column(nullable=False)
    
    # Amounts
    debit: Mapped[Decimal] = mapped_column(Numeric(19, 4), default=0)
    credit: Mapped[Decimal] = mapped_column(Numeric(19, 4), default=0)
    currency: Mapped[str] = mapped_column(String(3), default='USD', nullable=False)
    
    # Description and reference
    description: Mapped[Optional[str]] = mapped_column(Text)
    reference: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Relationships
    journal_entry_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), 
        ForeignKey('journal_entry.id'),
        nullable=False,
    )
    journal_entry: Mapped[JournalEntry] = relationship(
        'JournalEntry', 
        back_populates='lines',
    )
    
    account_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), 
        ForeignKey('account.id'),
        nullable=False,
    )
    account: Mapped[Account] = relationship('Account', back_populates='journal_entries')
    
    # For tracking related transactions
    related_line_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('journal_entry_line.id'))
    related_line: Mapped[Optional['JournalEntryLine']] = relationship(
        'JournalEntryLine',
        remote_side=[id],
        back_populates='related_lines',
    )
    related_lines: Mapped[List['JournalEntryLine']] = relationship(
        'JournalEntryLine',
        remote_side=[related_line_id],
        back_populates='related_line',
    )
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            '(debit > 0 AND credit = 0) OR (credit > 0 AND debit = 0)',
            name='debit_xor_credit',
        ),
        UniqueConstraint(
            'journal_entry_id', 
            'line_number', 
            name='unique_journal_line_number',
        ),
    )
    
    def __repr__(self) -> str:
        return f'<JournalEntryLine {self.line_number} - {self.debit} / {self.credit}>'
    
    @property
    def amount(self) -> Decimal:
        """Get the absolute amount of the line (positive for debit, negative for credit)."""
        return self.debit - self.credit
