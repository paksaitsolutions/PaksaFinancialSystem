"""
Cash Management models for bank accounts, transactions, and reconciliation.
"""
from sqlalchemy import Column, Integer, String, Decimal, Date, DateTime, Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from app.models.base import BaseModel, AuditModel
import enum

class AccountType(enum.Enum):
    CHECKING = "checking"
    SAVINGS = "savings"
    MONEY_MARKET = "money_market"
    CREDIT_LINE = "credit_line"

class TransactionType(enum.Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"
    FEE = "fee"
    INTEREST = "interest"

class BankAccount(AuditModel):
    __tablename__ = 'bank_accounts'
    
    account_number = Column(String(50), unique=True, nullable=False)
    account_name = Column(String(100), nullable=False)
    bank_name = Column(String(100), nullable=False)
    account_type = Column(Enum(AccountType), nullable=False)
    routing_number = Column(String(20))
    current_balance = Column(Decimal(15, 2), default=0)
    available_balance = Column(Decimal(15, 2), default=0)
    is_active = Column(Boolean, default=True)
    
    transactions = relationship("BankTransaction", back_populates="bank_account")
    reconciliations = relationship("BankReconciliation", back_populates="bank_account")

class BankTransaction(AuditModel):
    __tablename__ = 'bank_transactions'
    
    bank_account_id = Column(Integer, ForeignKey('bank_accounts.id'), nullable=False)
    transaction_date = Column(Date, nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    amount = Column(Decimal(15, 2), nullable=False)
    description = Column(Text, nullable=False)
    reference_number = Column(String(100))
    is_reconciled = Column(Boolean, default=False)
    
    bank_account = relationship("BankAccount", back_populates="transactions")

class BankReconciliation(AuditModel):
    __tablename__ = 'bank_reconciliations'
    
    bank_account_id = Column(Integer, ForeignKey('bank_accounts.id'), nullable=False)
    reconciliation_date = Column(Date, nullable=False)
    statement_balance = Column(Decimal(15, 2), nullable=False)
    book_balance = Column(Decimal(15, 2), nullable=False)
    adjusted_balance = Column(Decimal(15, 2), nullable=False)
    is_balanced = Column(Boolean, default=False)
    
    bank_account = relationship("BankAccount", back_populates="reconciliations")

class CashFlowForecast(AuditModel):
    __tablename__ = 'cash_flow_forecasts'
    
    forecast_date = Column(Date, nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    opening_balance = Column(Decimal(15, 2), nullable=False)
    projected_inflows = Column(Decimal(15, 2), default=0)
    projected_outflows = Column(Decimal(15, 2), default=0)
    closing_balance = Column(Decimal(15, 2), nullable=False)