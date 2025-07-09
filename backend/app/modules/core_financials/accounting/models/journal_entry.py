"""
Paksa Financial System 
Journal Entry Model

This module defines the Journal Entry and related models for the General Ledger system.
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4

from sqlalchemy import (
    Column, String, Numeric, Boolean, ForeignKey, 
    DateTime, Enum as SQLEnum, Text, JSON, CheckConstraint,
    UniqueConstraint, Index
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func

from app.db.base_class import Base


class JournalEntryStatus(str, Enum):
    """Status of a journal entry."""
    DRAFT = 'draft'
    POSTED = 'posted'
    VOIDED = 'voided'
    REVERSED = 'reversed'


class JournalEntryType(str, Enum):
    """Types of journal entries."""
    STANDARD = 'standard'
    ADJUSTING = 'adjusting'
    CLOSING = 'closing'
    REVERSING = 'reversing'
    RECURRING = 'recurring'
    OPENING = 'opening'


class JournalEntry(Base):
    """
    Represents a journal entry in the general ledger.
    """
    __tablename__ = 'gl_journal_entries'
    
    # Primary Key
    id = Column(PG_UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    
    # Entry Identification
    entry_number = Column(String(50), unique=True, index=True, nullable=False)
    reference = Column(String(100), index=True, nullable=True)
    description = Column(Text, nullable=True)
    
    # Entry Classification
    type = Column(SQLEnum(JournalEntryType), default=JournalEntryType.STANDARD, nullable=False)
    status = Column(SQLEnum(JournalEntryStatus), default=JournalEntryStatus.DRAFT, nullable=False, index=True)
    
    # Dates
    entry_date = Column(DateTime(timezone=True), nullable=False, index=True)
    posted_at = Column(DateTime(timezone=True), nullable=True, index=True)
    reversed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Financial Period
    period_id = Column(PG_UUID(as_uuid=True), ForeignKey('gl_periods.id', ondelete='RESTRICT'), index=True, nullable=True)
    
    # Recurring Entry Information
    is_recurring = Column(Boolean, default=False, nullable=False)
    recurring_entry_id = Column(PG_UUID(as_uuid=True), ForeignKey('gl_journal_entries.id', ondelete='SET NULL'), nullable=True)
    next_recurring_date = Column(DateTime(timezone=True), nullable=True, index=True)
    recurring_frequency = Column(String(20), nullable=True)  # daily, weekly, monthly, quarterly, yearly
    recurring_end_date = Column(DateTime(timezone=True), nullable=True)
    
    # Reversal Information
    reversed_entry_id = Column(PG_UUID(as_uuid=True), ForeignKey('gl_journal_entries.id', ondelete='SET NULL'), nullable=True)
    
    # Totals
    total_debit = Column(Numeric(20, 4), default=0, nullable=False)
    total_credit = Column(Numeric(20, 4), default=0, nullable=False)
    
    # Metadata
    metadata_ = Column('metadata', JSONB, nullable=True, default=dict)
    
    # Audit Fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(PG_UUID(as_uuid=True), nullable=False)
    updated_by = Column(PG_UUID(as_uuid=True), nullable=False)
    
    # Relationships
    lines = relationship('JournalEntryLine', back_populates='journal_entry', cascade='all, delete-orphan')
    period = relationship('GLPeriod', back_populates='journal_entries')
    
    # Recurring entry relationships
    recurring_entries = relationship('JournalEntry', back_populates='recurring_parent', remote_side=[id])
    recurring_parent = relationship('JournalEntry', remote_side=[recurring_entry_id], back_populates='recurring_entries')
    
    # Reversal relationships
    reversed_entries = relationship('JournalEntry', back_populates='reversal_parent', remote_side=[id])
    reversal_parent = relationship('JournalEntry', remote_side=[reversed_entry_id], back_populates='reversed_entries')
    
    # Indexes
    __table_args__ = (
        UniqueConstraint('entry_number', name='uq_gl_journal_entries_entry_number'),
        Index('ix_gl_journal_entries_entry_date', 'entry_date', postgresql_using='brin'),
        Index('ix_gl_journal_entries_status', 'status'),
        Index('ix_gl_journal_entries_type', 'type'),
        CheckConstraint('total_debit = total_credit', name='check_debit_equals_credit'),
        CheckConstraint(
            "(status = 'posted' AND posted_at IS NOT NULL) OR (status != 'posted' AND posted_at IS NULL)",
            name='check_posted_status_with_date'
        ),
    )
    
    @validates('entry_number')
    def validate_entry_number(self, key: str, entry_number: str) -> str:
        """Validate journal entry number format."""
        if not entry_number or not entry_number.strip():
            raise ValueError("Journal entry number cannot be empty")
        return entry_number.strip().upper()
    
    @validates('total_debit', 'total_credit')
    def validate_totals(self, key: str, value: Any) -> Any:
        """Ensure totals are non-negative."""
        if value is not None and value < 0:
            raise ValueError("Amounts cannot be negative")
        return value
    
    def __repr__(self) -> str:
        return f"<JournalEntry(id={self.id}, entry_number='{self.entry_number}', date={self.entry_date})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert journal entry to dictionary."""
        return {
            'id': str(self.id),
            'entry_number': self.entry_number,
            'reference': self.reference,
            'description': self.description,
            'type': self.type.value,
            'status': self.status.value,
            'entry_date': self.entry_date.isoformat() if self.entry_date else None,
            'posted_at': self.posted_at.isoformat() if self.posted_at else None,
            'reversed_at': self.reversed_at.isoformat() if self.reversed_at else None,
            'period_id': str(self.period_id) if self.period_id else None,
            'is_recurring': self.is_recurring,
            'recurring_entry_id': str(self.recurring_entry_id) if self.recurring_entry_id else None,
            'next_recurring_date': self.next_recurring_date.isoformat() if self.next_recurring_date else None,
            'recurring_frequency': self.recurring_frequency,
            'recurring_end_date': self.recurring_end_date.isoformat() if self.recurring_end_date else None,
            'reversed_entry_id': str(self.reversed_entry_id) if self.reversed_entry_id else None,
            'total_debit': float(self.total_debit) if self.total_debit is not None else 0.0,
            'total_credit': float(self.total_credit) if self.total_credit is not None else 0.0,
            'metadata': self.metadata_ or {},
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': str(self.created_by) if self.created_by else None,
            'updated_by': str(self.updated_by) if self.updated_by else None,
            'lines': [line.to_dict() for line in self.lines] if self.lines else []
        }


class JournalEntryLine(Base):
    """
    Represents a single line item in a journal entry.
    """
    __tablename__ = 'gl_journal_entry_lines'
    
    # Primary Key
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Foreign Keys
    journal_entry_id = Column(PG_UUID(as_uuid=True), ForeignKey('gl_journal_entries.id', ondelete='CASCADE'), nullable=False, index=True)
    account_id = Column(PG_UUID(as_uuid=True), ForeignKey('gl_accounts.id', ondelete='RESTRICT'), nullable=False, index=True)
    
    # Line Details
    line_number = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    
    # Amounts
    amount = Column(Numeric(20, 4), nullable=False)
    is_debit = Column(Boolean, nullable=False, index=True)
    
    # Allocation
    allocation_id = Column(PG_UUID(as_uuid=True), nullable=True)
    allocation_type = Column(String(50), nullable=True)
    
    # Foreign Currency
    currency_code = Column(String(3), nullable=True)
    exchange_rate = Column(Numeric(12, 6), default=1.0, nullable=True)
    foreign_amount = Column(Numeric(20, 4), nullable=True)
    
    # Tax Information
    tax_code = Column(String(20), nullable=True)
    tax_amount = Column(Numeric(20, 4), nullable=True)
    
    # Metadata
    metadata_ = Column('metadata', JSONB, nullable=True, default=dict)
    
    # Relationships
    journal_entry = relationship('JournalEntry', back_populates='lines')
    account = relationship('Account')
    
    # Indexes
    __table_args__ = (
        Index('ix_gl_journal_entry_lines_journal_entry_id', 'journal_entry_id'),
        Index('ix_gl_journal_entry_lines_account_id', 'account_id'),
        Index('ix_gl_journal_entry_lines_allocation', 'allocation_id', 'allocation_type'),
        UniqueConstraint('journal_entry_id', 'line_number', name='uq_gl_journal_entry_lines_entry_line'),
        CheckConstraint('amount > 0', name='check_positive_amount'),
    )
    
    @validates('amount')
    def validate_amount(self, key: str, amount: Decimal) -> Decimal:
        """Ensure amount is positive."""
        if amount <= 0:
            raise ValueError("Amount must be positive")
        return amount
    
    def __repr__(self) -> str:
        return f"<JournalEntryLine(id={self.id}, account_id={self.account_id}, " \
               f"amount={self.amount}, is_debit={self.is_debit})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert journal entry line to dictionary."""
        return {
            'id': str(self.id),
            'journal_entry_id': str(self.journal_entry_id),
            'account_id': str(self.account_id),
            'line_number': self.line_number,
            'description': self.description,
            'amount': float(self.amount) if self.amount is not None else 0.0,
            'is_debit': self.is_debit,
            'allocation_id': str(self.allocation_id) if self.allocation_id else None,
            'allocation_type': self.allocation_type,
            'currency_code': self.currency_code,
            'exchange_rate': float(self.exchange_rate) if self.exchange_rate is not None else 1.0,
            'foreign_amount': float(self.foreign_amount) if self.foreign_amount is not None else None,
            'tax_code': self.tax_code,
            'tax_amount': float(self.tax_amount) if self.tax_amount is not None else None,
            'metadata': self.metadata_ or {}
        }
