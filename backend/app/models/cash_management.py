from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, Integer
from sqlalchemy.types import DECIMAL as Decimal
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime

class BankAccount(Base):
    __tablename__ = "bank_accounts"
    
    id = Column(String, primary_key=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    account_name = Column(String(255), nullable=False)
    account_number = Column(String(50), nullable=False)
    bank_name = Column(String(255), nullable=False)
    routing_number = Column(String(50))
    account_type = Column(String(50))
    currency = Column(String(3), default="USD")
    current_balance = Column(Decimal(15, 2), default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CashTransaction(Base):
    __tablename__ = "cash_transactions"
    
    id = Column(String, primary_key=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    bank_account_id = Column(String, ForeignKey("bank_accounts.id"), nullable=False)
    transaction_date = Column(DateTime, nullable=False)
    transaction_type = Column(String(20), nullable=False)  # debit, credit
    amount = Column(Decimal(15, 2), nullable=False)
    description = Column(Text)
    reference = Column(String(100))
    reconciled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class BankReconciliation(Base):
    __tablename__ = "bank_reconciliations"
    
    id = Column(String, primary_key=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    bank_account_id = Column(String, ForeignKey("bank_accounts.id"), nullable=False)
    reconciliation_date = Column(DateTime, nullable=False)
    statement_balance = Column(Decimal(15, 2), nullable=False)
    book_balance = Column(Decimal(15, 2), nullable=False)
    adjusted_balance = Column(Decimal(15, 2), nullable=False)
    status = Column(String(20), default="in_progress")
    created_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

class CashForecast(Base):
    __tablename__ = "cash_forecasts"
    
    id = Column(String, primary_key=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    forecast_date = Column(DateTime, nullable=False)
    projected_inflow = Column(Decimal(15, 2), default=0)
    projected_outflow = Column(Decimal(15, 2), default=0)
    net_cash_flow = Column(Decimal(15, 2), default=0)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)