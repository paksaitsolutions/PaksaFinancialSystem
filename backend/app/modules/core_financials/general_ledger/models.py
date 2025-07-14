"""
General Ledger models for chart of accounts, journal entries, and financial periods.
"""
from sqlalchemy import Column, Integer, String, Decimal, Date, DateTime, Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import BaseModel, AuditModel
import enum

class AccountType(enum.Enum):
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    REVENUE = "revenue"
    EXPENSE = "expense"

class Account(AuditModel):
    __tablename__ = 'accounts'
    
    account_code = Column(String(20), unique=True, nullable=False)
    account_name = Column(String(100), nullable=False)
    account_type = Column(Enum(AccountType), nullable=False)
    parent_account_id = Column(Integer, ForeignKey('accounts.id'))
    is_active = Column(Boolean, default=True)
    description = Column(Text)
    
    parent = relationship("Account", remote_side=[id])
    children = relationship("Account")
    journal_entries = relationship("JournalEntryLine", back_populates="account")

class JournalEntry(AuditModel):
    __tablename__ = 'journal_entries'
    
    entry_number = Column(String(50), unique=True, nullable=False)
    entry_date = Column(Date, nullable=False)
    description = Column(Text, nullable=False)
    reference = Column(String(100))
    total_debit = Column(Decimal(15, 2), default=0)
    total_credit = Column(Decimal(15, 2), default=0)
    status = Column(String(20), default='draft')
    
    lines = relationship("JournalEntryLine", back_populates="journal_entry")

class JournalEntryLine(BaseModel):
    __tablename__ = 'journal_entry_lines'
    
    journal_entry_id = Column(Integer, ForeignKey('journal_entries.id'), nullable=False)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    description = Column(Text)
    debit_amount = Column(Decimal(15, 2), default=0)
    credit_amount = Column(Decimal(15, 2), default=0)
    
    journal_entry = relationship("JournalEntry", back_populates="lines")
    account = relationship("Account", back_populates="journal_entries")

class FiscalPeriod(BaseModel):
    __tablename__ = 'fiscal_periods'
    
    period_name = Column(String(50), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_closed = Column(Boolean, default=False)
    fiscal_year = Column(Integer, nullable=False)