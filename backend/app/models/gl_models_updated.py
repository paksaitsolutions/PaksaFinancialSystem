from sqlalchemy import Column, Integer, String, Date, Numeric, Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid
from .base import Base

class GLAccount(Base):
    """General Ledger Account Model"""
    __tablename__ = 'gl_accounts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    account_code = Column(String(20), unique=True, nullable=False)
    account_name = Column(String(100), nullable=False)
    account_type = Column(String(50), nullable=False)  # ASSET, LIABILITY, EQUITY, REVENUE, EXPENSE
    parent_id = Column(Integer, ForeignKey('gl_accounts.id'), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    parent = relationship("GLAccount", remote_side=[id], back_populates="children")
    children = relationship("GLAccount", back_populates="parent")
    journal_entry_lines = relationship("JournalEntryLine", back_populates="account")
    
    def __repr__(self):
        return f"<GLAccount(code={self.account_code}, name='{self.account_name}')>"

class JournalEntry(Base):
    """Journal Entry Header"""
    __tablename__ = 'journal_entries'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    entry_number = Column(String(20), unique=True, nullable=False)
    entry_date = Column(Date, nullable=False, index=True)
    reference = Column(String(100))
    description = Column(Text)
    status = Column(String(20), default='DRAFT')  # DRAFT, POSTED, REVERSED
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    lines = relationship("JournalEntryLine", back_populates="journal_entry", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<JournalEntry(number={self.entry_number}, date={self.entry_date})>"

class JournalEntryLine(Base):
    """Journal Entry Line Items"""
    __tablename__ = 'journal_entry_lines'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    journal_entry_id = Column(Integer, ForeignKey('journal_entries.id'), nullable=False)
    account_id = Column(Integer, ForeignKey('gl_accounts.id'), nullable=False)
    line_number = Column(Integer, nullable=False)
    debit_amount = Column(Numeric(15, 2), default=0)
    credit_amount = Column(Numeric(15, 2), default=0)
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    journal_entry = relationship("JournalEntry", back_populates="lines")
    account = relationship("GLAccount", back_populates="journal_entry_lines")
    
    def __repr__(self):
        return f"<JournalEntryLine(account={self.account_id}, debit={self.debit_amount}, credit={self.credit_amount})>"

class AccountingPeriod(Base):
    """Accounting Periods"""
    __tablename__ = 'accounting_periods'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    period_name = Column(String(20), unique=True, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_closed = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<AccountingPeriod({self.period_name} - {self.start_date} to {self.end_date})>"
