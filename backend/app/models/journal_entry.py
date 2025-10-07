from sqlalchemy import Column, String, Numeric, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from .base import BaseModel
import uuid

class JournalEntry(BaseModel):
    __tablename__ = "journal_entries"
    
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True, default=uuid.uuid4)
    entry_number = Column(String(50), nullable=False, unique=True)
    entry_date = Column(Date, nullable=False)
    description = Column(Text)
    reference = Column(String(100))
    total_debit = Column(Numeric(15, 2), default=0)
    total_credit = Column(Numeric(15, 2), default=0)
    status = Column(String(20), default='draft')  # draft, posted, reversed
    
    # Relationships
    lines = relationship("JournalEntryLine", back_populates="journal_entry", cascade="all, delete-orphan")

class JournalEntryLine(BaseModel):
    __tablename__ = "journal_entry_lines"
    
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True, default=uuid.uuid4)
    journal_entry_id = Column(UUID(as_uuid=True), ForeignKey('journal_entries.id'), nullable=False)
    account_id = Column(UUID(as_uuid=True), ForeignKey('gl_accounts.id'), nullable=False)
    description = Column(Text)
    debit_amount = Column(Numeric(15, 2), default=0)
    credit_amount = Column(Numeric(15, 2), default=0)
    
    # Relationships
    journal_entry = relationship("JournalEntry", back_populates="lines")
    account = relationship("GLAccount", back_populates="journal_entries")