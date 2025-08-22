"""
Journal entry models.
"""
import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base

class JournalEntry(Base):
    """Journal entry model."""
    
    __tablename__ = "journal_entry"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    entry_number = Column(String(50), nullable=False, index=True)
    entry_date = Column(DateTime, nullable=False)
    reference = Column(String(100))
    description = Column(Text)
    
    # Multi-currency support
    currency_code = Column(String(3), default="USD")
    exchange_rate = Column(Numeric(precision=10, scale=6), default=1.0)
    
    # Inter-company transaction
    source_company_id = Column(UUID(as_uuid=True))
    target_company_id = Column(UUID(as_uuid=True))
    
    status = Column(String(20), default="draft")  # draft, posted, reversed
    posted_at = Column(DateTime)
    posted_by = Column(UUID(as_uuid=True))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    lines = relationship("JournalEntryLine", back_populates="journal_entry")

class JournalEntryLine(Base):
    """Journal entry line model."""
    
    __tablename__ = "journal_entry_line"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    journal_entry_id = Column(UUID(as_uuid=True), ForeignKey("journal_entry.id"), nullable=False)
    account_id = Column(UUID(as_uuid=True), ForeignKey("chart_of_accounts.id"), nullable=False)
    
    description = Column(String(500))
    debit_amount = Column(Numeric(precision=18, scale=2), default=0)
    credit_amount = Column(Numeric(precision=18, scale=2), default=0)
    
    # Multi-currency amounts
    debit_amount_base = Column(Numeric(precision=18, scale=2), default=0)
    credit_amount_base = Column(Numeric(precision=18, scale=2), default=0)
    
    # Relationships
    journal_entry = relationship("JournalEntry", back_populates="lines")
    account = relationship("ChartOfAccounts", back_populates="journal_entries")