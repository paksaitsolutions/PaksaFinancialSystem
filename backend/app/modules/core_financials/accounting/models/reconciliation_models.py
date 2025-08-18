"""
Reconciliation Models

This module contains database models related to account reconciliation functionality.
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4

from sqlalchemy import Column, ForeignKey, Index, Text, UniqueConstraint, event
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

from core.database import Base
from .base_models import BaseModel


class ReconciliationStatus(str, Enum):
    """Status of a reconciliation."""
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ReconciliationMatchType(str, Enum):
    """Type of reconciliation match."""
    MANUAL = "manual"
    AUTO = "auto"
    SYSTEM = "system"


class Reconciliation(BaseModel, Base):
    """
    Represents an account reconciliation.
    """
    __tablename__ = "reconciliations"
    
    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
        comment="Unique identifier for the reconciliation"
    )
    
    account_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="The account being reconciled"
    )
    
    status: Mapped[ReconciliationStatus] = mapped_column(
        default=ReconciliationStatus.DRAFT,
        nullable=False,
        index=True,
        comment="Current status of the reconciliation"
    )
    
    start_date: Mapped[datetime] = mapped_column(
        nullable=False,
        comment="Start date of the reconciliation period"
    )
    
    end_date: Mapped[datetime] = mapped_column(
        nullable=False,
        comment="End date of the reconciliation period"
    )
    
    statement_balance: Mapped[float] = mapped_column(
        nullable=False,
        comment="Ending balance from the bank statement"
    )
    
    statement_date: Mapped[datetime] = mapped_column(
        nullable=False,
        comment="Date of the bank statement"
    )
    
    cleared_balance: Mapped[Optional[float]] = mapped_column(
        nullable=True,
        comment="Calculated balance of cleared transactions"
    )
    
    difference: Mapped[Optional[float]] = mapped_column(
        nullable=True,
        comment="Difference between statement balance and cleared balance"
    )
    
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Additional notes about the reconciliation"
    )
    
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
        comment="When the reconciliation was completed"
    )
    
    completed_by: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=True,
        comment="User who completed the reconciliation"
    )
    
    # Relationships
    account: Mapped["Account"] = relationship(
        "Account",
        back_populates="reconciliations"
    )
    
    items: Mapped[List["ReconciliationItem"]] = relationship(
        "ReconciliationItem",
        back_populates="reconciliation",
        cascade="all, delete-orphan"
    )
    
    audit_logs: Mapped[List["ReconciliationAuditLog"]] = relationship(
        "ReconciliationAuditLog",
        back_populates="reconciliation",
        cascade="all, delete-orphan"
    )
    
    # Indexes
    __table_args__ = (
        Index("ix_reconciliations_account_status", "account_id", "status"),
        Index("ix_reconciliations_date_range", "start_date", "end_date"),
        {
            "comment": "Stores information about account reconciliations"
        }
    )


class ReconciliationItem(BaseModel, Base):
    """
    Represents an item in a reconciliation, which can be a transaction or adjustment.
    """
    __tablename__ = "reconciliation_items"
    
    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
        comment="Unique identifier for the reconciliation item"
    )
    
    reconciliation_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("reconciliations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="The reconciliation this item belongs to"
    )
    
    journal_entry_id: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("journal_entries.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="The journal entry this item represents, if any"
    )
    
    transaction_date: Mapped[datetime] = mapped_column(
        nullable=False,
        index=True,
        comment="Date of the transaction"
    )
    
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Description of the item"
    )
    
    reference: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Reference number or identifier for the transaction"
    )
    
    amount: Mapped[float] = mapped_column(
        nullable=False,
        comment="Amount of the transaction (positive for deposits, negative for withdrawals)"
    )
    
    is_cleared: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
        index=True,
        comment="Whether this item has been cleared in the bank statement"
    )
    
    cleared_date: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
        comment="Date when this item was cleared"
    )
    
    is_matched: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
        index=True,
        comment="Whether this item has been matched to a bank transaction"
    )
    
    match_type: Mapped[Optional[ReconciliationMatchType]] = mapped_column(
        nullable=True,
        comment="How this item was matched (manual, auto, system)"
    )
    
    match_confidence: Mapped[Optional[float]] = mapped_column(
        nullable=True,
        comment="Confidence score for automatic matches (0-1)"
    )
    
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Additional notes about this item"
    )
    
    metadata_: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        name="metadata",
        nullable=True,
        comment="Additional metadata for the reconciliation item"
    )
    
    # Relationships
    reconciliation: Mapped["Reconciliation"] = relationship(
        "Reconciliation",
        back_populates="items"
    )
    
    journal_entry: Mapped[Optional["JournalEntry"]] = relationship(
        "JournalEntry",
        back_populates="reconciliation_items"
    )
    
    # Indexes
    __table_args__ = (
        Index("ix_reconciliation_items_reconciliation_cleared", "reconciliation_id", "is_cleared"),
        Index("ix_reconciliation_items_reconciliation_matched", "reconciliation_id", "is_matched"),
        Index("ix_reconciliation_items_transaction_date", "transaction_date"),
        {
            "comment": "Stores individual items within a reconciliation"
        }
    )


class ReconciliationAuditLog(BaseModel, Base):
    """
    Audit log for reconciliation actions.
    """
    __tablename__ = "reconciliation_audit_logs"
    
    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        comment="Unique identifier for the audit log entry"
    )
    
    reconciliation_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("reconciliations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="The reconciliation this log entry is for"
    )
    
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="User who performed the action"
    )
    
    action: Mapped[str] = mapped_column(
        nullable=False,
        index=True,
        comment="Type of action performed (create, update, delete, etc.)"
    )
    
    details: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        comment="Detailed information about the action"
    )
    
    ip_address: Mapped[Optional[str]] = mapped_column(
        nullable=True,
        comment="IP address of the user who performed the action"
    )
    
    user_agent: Mapped[Optional[str]] = mapped_column(
        nullable=True,
        comment="User agent string of the client used to perform the action"
    )
    
    # Relationships
    reconciliation: Mapped["Reconciliation"] = relationship(
        "Reconciliation",
        back_populates="audit_logs"
    )
    
    # Indexes
    __table_args__ = (
        Index("ix_reconciliation_audit_logs_action", "action"),
        Index("ix_reconciliation_audit_logs_created_at", "created_at"),
        {
            "comment": "Audit log of all actions performed on reconciliations"
        }
    )


# Add relationships to the Account and JournalEntry models
def add_reconciliation_relationships():
    """Add reconciliation relationships to the Account and JournalEntry models."""
    # This function will be called after the models are defined
    from .account import Account
    from .journal_entry import JournalEntry
    
    # Add relationship to Account model
    if not hasattr(Account, 'reconciliations'):
        Account.reconciliations = relationship(
            "Reconciliation",
            back_populates="account",
            cascade="all, delete-orphan"
        )
    
    # Add relationship to JournalEntry model
    if not hasattr(JournalEntry, 'reconciliation_items'):
        JournalEntry.reconciliation_items = relationship(
            "ReconciliationItem",
            back_populates="journal_entry"
        )


# Call the function to set up relationships
add_reconciliation_relationships()
