from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, Integer
from sqlalchemy.types import DECIMAL as Decimal
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime

class ChartOfAccounts(Base):
    __tablename__ = "chart_of_accounts"
    
    id = Column(String, primary_key=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    account_code = Column(String(20), unique=True, nullable=False)
    account_name = Column(String(255), nullable=False)
    account_type = Column(String(50), nullable=False)
    parent_id = Column(String, ForeignKey("chart_of_accounts.id"))
    balance = Column(Decimal(15, 2), default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class JournalEntry(Base):
    __tablename__ = "journal_entries"
    
    id = Column(String, primary_key=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    entry_number = Column(String(50), nullable=False)
    entry_date = Column(DateTime, nullable=False)
    description = Column(Text)
    reference = Column(String(100))
    total_debit = Column(Decimal(15, 2), default=0)
    total_credit = Column(Decimal(15, 2), default=0)
    status = Column(String(20), default="draft")
    created_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

class JournalEntryLine(Base):
    __tablename__ = "journal_entry_lines"
    
    id = Column(String, primary_key=True)
    journal_entry_id = Column(String, ForeignKey("journal_entries.id"), nullable=False)
    account_id = Column(String, ForeignKey("chart_of_accounts.id"), nullable=False)
    description = Column(Text)
    debit_amount = Column(Decimal(15, 2), default=0)
    credit_amount = Column(Decimal(15, 2), default=0)
    line_number = Column(Integer)

class TrialBalance(Base):
    __tablename__ = "trial_balance"
    
    id = Column(String, primary_key=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    account_id = Column(String, ForeignKey("chart_of_accounts.id"), nullable=False)
    opening_balance = Column(Decimal(15, 2), default=0)
    debit_total = Column(Decimal(15, 2), default=0)
    credit_total = Column(Decimal(15, 2), default=0)
    closing_balance = Column(Decimal(15, 2), default=0)
    created_at = Column(DateTime, default=datetime.utcnow)