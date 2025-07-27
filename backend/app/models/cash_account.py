from sqlalchemy import Column, String, Numeric, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel, GUID

class CashAccount(BaseModel):
    __tablename__ = "cash_accounts"
    
    tenant_id = Column(GUID(), nullable=False, index=True)
    account_name = Column(String(200), nullable=False)
    account_number = Column(String(50))
    bank_name = Column(String(200))
    account_type = Column(String(50))  # checking, savings, credit
    current_balance = Column(Numeric(15, 2), default=0)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    transactions = relationship("CashTransaction", back_populates="cash_account")

class CashTransaction(BaseModel):
    __tablename__ = "cash_transactions"
    
    tenant_id = Column(GUID(), nullable=False, index=True)
    cash_account_id = Column(GUID(), ForeignKey('cash_accounts.id'), nullable=False)
    transaction_date = Column(String(10), nullable=False)
    description = Column(String(500))
    amount = Column(Numeric(15, 2), nullable=False)
    transaction_type = Column(String(20))  # debit, credit
    reference = Column(String(100))
    
    # Relationships
    cash_account = relationship("CashAccount", back_populates="transactions")