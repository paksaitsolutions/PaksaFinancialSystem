"""
Intercompany transaction models.
"""
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, String, Numeric, Date, DateTime, ForeignKey, Enum as SQLEnum, Boolean, Text
from sqlalchemy.orm import relationship

from .base import BaseModel, GUID


class IntercompanyTransactionType(str, Enum):
    SALE = "sale"
    PURCHASE = "purchase"
    LOAN = "loan"
    EXPENSE_ALLOCATION = "expense_allocation"
    REVENUE_SHARING = "revenue_sharing"
    TRANSFER = "transfer"


class IntercompanyTransactionStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    POSTED = "posted"
    RECONCILED = "reconciled"
    CANCELLED = "cancelled"


class IntercompanyTransaction(BaseModel):
    """
    Represents an intercompany transaction between two companies.
    """
    __tablename__ = "intercompany_transactions"
    
    # Transaction details
    transaction_number = Column(String(50), unique=True, index=True, nullable=False)
    transaction_type = Column(SQLEnum(IntercompanyTransactionType), nullable=False)
    status = Column(SQLEnum(IntercompanyTransactionStatus), nullable=False, default=IntercompanyTransactionStatus.DRAFT)
    
    # Companies involved
    source_company_id = Column(GUID(), nullable=False)
    target_company_id = Column(GUID(), nullable=False)
    
    # Transaction amounts
    amount = Column(Numeric(15, 2), nullable=False)
    currency_id = Column(GUID(), ForeignKey("currencies.id"), nullable=False)
    
    # Dates
    transaction_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=True)
    
    # Accounts
    source_account_id = Column(GUID(), ForeignKey("chart_of_accounts.id"), nullable=False)
    target_account_id = Column(GUID(), ForeignKey("chart_of_accounts.id"), nullable=False)
    
    # Description and reference
    description = Column(Text, nullable=True)
    reference_number = Column(String(100), nullable=True)
    
    # Journal entries
    source_journal_entry_id = Column(GUID(), ForeignKey("journal_entries.id"), nullable=True)
    target_journal_entry_id = Column(GUID(), ForeignKey("journal_entries.id"), nullable=True)
    
    # Approval workflow
    approved_by = Column(GUID(), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    # Relationships
    currency = relationship("Currency", back_populates="intercompany_transactions")
    source_account = relationship("GLChartOfAccounts", foreign_keys=[source_account_id])
    target_account = relationship("GLChartOfAccounts", foreign_keys=[target_account_id])
    source_journal_entry = relationship("JournalEntry", foreign_keys=[source_journal_entry_id])
    target_journal_entry = relationship("JournalEntry", foreign_keys=[target_journal_entry_id])
    
    def __repr__(self) -> str:
        return f"<IntercompanyTransaction(id={self.id}, number='{self.transaction_number}', type='{self.transaction_type}')>"


class IntercompanyReconciliation(BaseModel):
    """
    Represents the reconciliation of intercompany transactions.
    """
    __tablename__ = "intercompany_reconciliations"
    
    # Reconciliation details
    reconciliation_number = Column(String(50), unique=True, index=True, nullable=False)
    reconciliation_date = Column(Date, nullable=False)
    
    # Companies involved
    company_a_id = Column(GUID(), nullable=False)
    company_b_id = Column(GUID(), nullable=False)
    
    # Period
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    
    # Status
    status = Column(String(20), nullable=False, default="draft")
    
    # Balances
    company_a_balance = Column(Numeric(15, 2), nullable=False, default=0)
    company_b_balance = Column(Numeric(15, 2), nullable=False, default=0)
    difference = Column(Numeric(15, 2), nullable=False, default=0)
    
    # Reconciliation details
    notes = Column(Text, nullable=True)
    reconciled_by = Column(GUID(), nullable=True)
    reconciled_at = Column(DateTime, nullable=True)
    
    def __repr__(self) -> str:
        return f"<IntercompanyReconciliation(id={self.id}, number='{self.reconciliation_number}')>"