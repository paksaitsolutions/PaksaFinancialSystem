"""
Reconciliation Models

This module contains the database models for account reconciliation.
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, Enum as SQLEnum, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, relationship, mapped_column

from app.models.base import Base


class ReconciliationStatus(str, Enum):
    """Status of a reconciliation."""
    DRAFT = 'draft'  # Reconciliation is being prepared
    IN_PROGRESS = 'in_progress'  # Reconciliation is in progress
    COMPLETED = 'completed'  # Reconciliation is completed
    APPROVED = 'approved'  # Reconciliation is approved
    REJECTED = 'rejected'  # Reconciliation is rejected
    VOIDED = 'voided'  # Reconciliation is voided


class ReconciliationMatchType(str, Enum):
    """Type of reconciliation match."""
    AUTO = 'auto'  # Automatically matched by the system
    MANUAL = 'manual'  # Manually matched by the user
    SUGGESTED = 'suggested'  # Suggested by the system, not yet confirmed


class Reconciliation(Base):
    """
    Represents an account reconciliation.
    
    A reconciliation matches transactions from the general ledger with external
    statements (e.g., bank statements) to ensure they agree.
    """
    __tablename__ = 'reconciliations'
    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    account_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('accounts.id'), nullable=False)
    reference: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    status: Mapped[ReconciliationStatus] = mapped_column(SQLEnum(ReconciliationStatus), default=ReconciliationStatus.DRAFT, nullable=False)
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    # Statement information
    statement_balance: Mapped[float] = mapped_column(Numeric(19, 4), nullable=False)
    statement_currency: Mapped[str] = mapped_column(String(3), default='USD', nullable=False)
    statement_reference: Mapped[Optional[str]] = mapped_column(String(100))
    statement_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    # Calculated fields
    calculated_balance: Mapped[float] = mapped_column(Numeric(19, 4), nullable=False)
    difference: Mapped[float] = mapped_column(Numeric(19, 4), nullable=False, default=0)
    
    # Audit fields
    created_by: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    approved_by: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True))
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Relationships
    account: Mapped['Account'] = relationship('Account', back_populates='reconciliations')
    items: Mapped[List['ReconciliationItem']] = relationship('ReconciliationItem', back_populates='reconciliation', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Reconciliation {self.reference} ({self.status})>"


class ReconciliationItem(Base):
    """
    Represents an item in a reconciliation, which can be either a journal entry
    or a statement line that needs to be reconciled.
    """
    __tablename__ = 'reconciliation_items'
    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    reconciliation_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('reconciliations.id'), nullable=False)
    
    # Reference to the journal entry (if applicable)
    journal_entry_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('journal_entries.id'))
    journal_entry_line_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('journal_entry_lines.id'))
    
    # Statement line information (for external transactions)
    statement_line_ref: Mapped[Optional[str]] = mapped_column(String(100))
    statement_line_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    statement_line_description: Mapped[Optional[str]] = mapped_column(Text)
    statement_line_amount: Mapped[Optional[float]] = mapped_column(Numeric(19, 4))
    
    # Reconciliation details
    match_type: Mapped[ReconciliationMatchType] = mapped_column(SQLEnum(ReconciliationMatchType), default=ReconciliationMatchType.MANUAL)
    is_matched: Mapped[bool] = mapped_column(default=False)
    matched_with: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('reconciliation_items.id'))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Audit fields
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    reconciliation: Mapped['Reconciliation'] = relationship('Reconciliation', back_populates='items')
    journal_entry: Mapped[Optional['JournalEntry']] = relationship('JournalEntry')
    journal_entry_line: Mapped[Optional['JournalEntryLine']] = relationship('JournalEntryLine')
    
    def __repr__(self):
        if self.journal_entry_id:
            return f"<ReconciliationItem JE:{self.journal_entry_id}>"
        return f"<ReconciliationItem {self.statement_line_ref}>"


class ReconciliationAuditLog(Base):
    """
    Audit log for reconciliation activities.
    """
    __tablename__ = 'reconciliation_audit_logs'
    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    reconciliation_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('reconciliations.id'), nullable=False)
    
    # Action details
    action: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., 'create', 'update', 'match', 'unmatch', 'approve', 'reject'
    details: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # User who performed the action
    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    
    def __repr__(self):
        return f"<ReconciliationAuditLog {self.action} by {self.user_id} at {self.created_at}>"