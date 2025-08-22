"""
Chart of accounts models.
"""
import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, Numeric, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base

class ChartOfAccounts(Base):
    """Chart of accounts model."""
    
    __tablename__ = "chart_of_accounts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    account_code = Column(String(20), nullable=False, index=True)
    account_name = Column(String(200), nullable=False)
    account_type = Column(String(50), nullable=False)  # asset, liability, equity, revenue, expense
    parent_id = Column(UUID(as_uuid=True), ForeignKey("chart_of_accounts.id"))
    
    is_active = Column(Boolean, default=True)
    is_system = Column(Boolean, default=False)  # System accounts cannot be deleted
    level = Column(Integer, default=1)
    
    # Multi-currency support
    currency_code = Column(String(3), default="USD")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    parent = relationship("ChartOfAccounts", remote_side=[id])
    children = relationship("ChartOfAccounts")
    journal_entries = relationship("JournalEntryLine", back_populates="account")

class FinancialPeriod(Base):
    """Financial period model."""
    
    __tablename__ = "financial_period"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    period_name = Column(String(100), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    
    is_closed = Column(Boolean, default=False)
    is_current = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime)

class AccountingRule(Base):
    """Automated accounting rule model."""
    
    __tablename__ = "accounting_rule"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    rule_name = Column(String(200), nullable=False)
    trigger_event = Column(String(100), nullable=False)  # invoice_created, payment_received, etc.
    conditions = Column(String(1000))  # JSON conditions
    
    debit_account_id = Column(UUID(as_uuid=True), ForeignKey("chart_of_accounts.id"))
    credit_account_id = Column(UUID(as_uuid=True), ForeignKey("chart_of_accounts.id"))
    
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    debit_account = relationship("ChartOfAccounts", foreign_keys=[debit_account_id])
    credit_account = relationship("ChartOfAccounts", foreign_keys=[credit_account_id])