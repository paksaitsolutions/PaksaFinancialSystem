"""
General Ledger models for chart of accounts, journal entries, and financial periods.
"""
from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, ForeignKey, Text, Enum, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.db.base import BaseModel
import enum

class AccountType(enum.Enum):
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    REVENUE = "revenue"
    EXPENSE = "expense"

class Account(BaseModel):
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

# Import JournalEntry and JournalEntryLine from unified models
from app.models.core_models import JournalEntry, JournalEntryLine

class FiscalPeriod(BaseModel):
    __tablename__ = 'fiscal_periods'
    
    period_name = Column(String(50), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_closed = Column(Boolean, default=False)
    fiscal_year = Column(Integer, nullable=False)