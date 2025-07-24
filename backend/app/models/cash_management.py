"""
Cash Management Module Models

This module contains the database models for managing cash positions, transactions,
bank accounts, and cash flow forecasting in the Paksa Financial System.
"""
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4

from sqlalchemy import (
    Column, String, Numeric, Date, DateTime, ForeignKey, 
    Enum, Boolean, JSON, Text, CheckConstraint, func, Index, and_
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, ENUM
from sqlalchemy.orm import relationship, Mapped, mapped_column, validates
from sqlalchemy.ext.hybrid import hybrid_property

from .base import BaseModel, GUID
from .enums import (
    BankAccountType, 
    TransactionStatus, 
    CashFlowCategory,
    ReconciliationStatus,
    PaymentMethod
)


class BankAccount(BaseModel):
    """
    Represents a bank account for cash management.
    """
    __tablename__ = "bank_accounts"
    
    # Account identification
    name = Column(String(100), nullable=False)
    account_number = Column(String(50), nullable=False, index=True)
    account_type = Column(ENUM(BankAccountType), nullable=False)
    
    # Bank information
    bank_name = Column(String(100), nullable=False)
    bank_code = Column(String(20), nullable=True)  # SWIFT, IFSC, etc.
    branch_name = Column(String(100), nullable=True)
    branch_code = Column(String(20), nullable=True)
    iban = Column(String(50), nullable=True)
    
    # Currency and balance
    currency_id = Column(GUID(), ForeignKey('currencies.id'), nullable=False)
    current_balance = Column(Numeric(20, 6), default=0, nullable=False)
    available_balance = Column(Numeric(20, 6), default=0, nullable=False)
    
    # Account settings
    is_active = Column(Boolean, default=True, nullable=False)
    include_in_cash_flow = Column(Boolean, default=True, nullable=False)
    allow_overdraft = Column(Boolean, default=False, nullable=False)
    overdraft_limit = Column(Numeric(20, 6), default=0, nullable=False)
    
    # Integration details
    integration_id = Column(String(100), nullable=True)  # External system ID
    last_synced_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    currency = relationship("Currency")
    transactions: Mapped[List["BankTransaction"]] = relationship(
        "BankTransaction", 
        back_populates="bank_account",
        order_by="desc(BankTransaction.transaction_date)"
    )
    reconciliations: Mapped[List["BankReconciliation"]] = relationship(
        "BankReconciliation", 
        back_populates="bank_account"
    )
    
    # Audit fields
    created_by_id = Column(GUID(), ForeignKey('users.id'), nullable=True)
    created_by = relationship("User", foreign_keys=[created_by_id])
    
    __table_args__ = (
        Index('idx_bank_account_currency', 'currency_id'),
        CheckConstraint(
            "current_balance >= CASE WHEN allow_overdraft THEN -overdraft_limit ELSE 0 END",
            name='check_overdraft_limit'
        ),
    )
    
    @property
    def display_name(self) -> str:
        """Get a display-friendly name for the account."""
        return f"{self.bank_name} - {self.account_number} ({self.currency.code})"
    
    def update_balance(self, amount: Decimal, is_credit: bool = False) -> None:
        """Update the account balance."""
        if is_credit:
            self.current_balance += amount
        else:
            self.current_balance -= amount
    
    def get_available_balance(self) -> Decimal:
        """Get the available balance considering overdraft."""
        if self.allow_overdraft:
            return self.current_balance + self.overdraft_limit
        return max(self.current_balance, Decimal('0'))


class BankTransaction(BaseModel):
    """
    Represents a bank transaction for cash management.
    """
    __tablename__ = "bank_transactions"
    
    # Transaction details
    transaction_date = Column(Date, nullable=False, index=True)
    value_date = Column(Date, nullable=True)  # When funds are available
    reference = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Amount and currency
    amount = Column(Numeric(20, 6), nullable=False)
    currency_id = Column(GUID(), ForeignKey('currencies.id'), nullable=False)
    exchange_rate = Column(Numeric(20, 10), default=1, nullable=False)
    
    # Classification
    category = Column(ENUM(CashFlowCategory), nullable=True)
    payment_method = Column(ENUM(PaymentMethod), nullable=True)
    status = Column(ENUM(TransactionStatus), default=TransactionStatus.PENDING, nullable=False)
    is_reconciled = Column(Boolean, default=False, nullable=False)
    
    # Bank account relationship
    bank_account_id = Column(GUID(), ForeignKey('bank_accounts.id'), nullable=False)
    bank_account = relationship("BankAccount", back_populates="transactions")
    
    # Related documents
    related_document_type = Column(String(50), nullable=True)  # 'invoice', 'bill', 'expense', etc.
    related_document_id = Column(GUID(), nullable=True)
    
    # Reconciliation
    reconciliation_id = Column(GUID(), ForeignKey('bank_reconciliations.id'), nullable=True)
    reconciliation = relationship("BankReconciliation", back_populates="transactions")
    
    # Metadata
    metadata = Column(JSON, nullable=True)  # Additional transaction data
    
    # Relationships
    currency = relationship("Currency")
    
    # Audit fields
    created_by_id = Column(GUID(), ForeignKey('users.id'), nullable=True)
    created_by = relationship("User", foreign_keys=[created_by_id])
    
    __table_args__ = (
        Index('idx_bank_transaction_dates', 'transaction_date', 'value_date'),
        Index('idx_bank_transaction_reference', 'reference'),
        Index('idx_bank_transaction_related', 'related_document_type', 'related_document_id'),
        CheckConstraint("amount > 0", name='check_positive_amount'),
    )
    
    @property
    def is_credit(self) -> bool:
        """Check if this is a credit transaction."""
        return self.amount > 0
    
    @property
    def is_debit(self) -> bool:
        """Check if this is a debit transaction."""
        return self.amount < 0
    
    def match_rule(self, rule: 'TransactionMatchingRule') -> bool:
        """Check if this transaction matches the given rule."""
        # Implement matching logic based on rule criteria
        # This is a simplified example
        if rule.reference_pattern and rule.reference_pattern not in (self.reference or ''):
            return False
            
        if rule.amount_min is not None and abs(self.amount) < rule.amount_min:
            return False
            
        if rule.amount_max is not None and abs(self.amount) > rule.amount_max:
            return False
            
        return True


class BankReconciliation(BaseModel):
    """
    Represents a bank reconciliation between the company's records and bank statement.
    """
    __tablename__ = "bank_reconciliations"
    
    # Reconciliation details
    statement_date = Column(Date, nullable=False)
    statement_balance = Column(Numeric(20, 6), nullable=False)
    ending_balance = Column(Numeric(20, 6), nullable=False)
    status = Column(ENUM(ReconciliationStatus), default=ReconciliationStatus.IN_PROGRESS, nullable=False)
    
    # Bank account relationship
    bank_account_id = Column(GUID(), ForeignKey('bank_accounts.id'), nullable=False)
    bank_account = relationship("BankAccount", back_populates="reconciliations")
    
    # Transactions included in this reconciliation
    transactions: Mapped[List["BankTransaction"]] = relationship(
        "BankTransaction", 
        back_populates="reconciliation",
        order_by="BankTransaction.transaction_date"
    )
    
    # Audit fields
    created_by_id = Column(GUID(), ForeignKey('users.id'), nullable=True)
    created_by = relationship("User", foreign_keys=[created_by_id])
    
    @property
    def calculated_ending_balance(self) -> Decimal:
        """Calculate the expected ending balance based on transactions."""
        if not self.transactions:
            return self.statement_balance
            
        reconciled_amount = sum(
            t.amount for t in self.transactions 
            if t.status == TransactionStatus.RECONCILED
        )
        return self.statement_balance + reconciled_amount
    
    def is_balanced(self) -> bool:
        """Check if the reconciliation is balanced."""
        return abs(self.calculated_ending_balance - self.ending_balance) < Decimal('0.01')


class CashFlowForecast(BaseModel):
    """
    Represents a cash flow forecast for planning and analysis.
    """
    __tablename__ = "cash_flow_forecasts"
    
    # Forecast details
    name = Column(String(100), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    currency_id = Column(GUID(), ForeignKey('currencies.id'), nullable=False)
    
    # Forecast settings
    include_unpaid_invoices = Column(Boolean, default=True, nullable=False)
    include_unpaid_bills = Column(Boolean, default=True, nullable=False)
    include_recurring_transactions = Column(Boolean, default=True, nullable=False)
    
    # Forecast data (cached)
    forecast_data = Column(JSON, nullable=True)
    last_calculated_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    currency = relationship("Currency")
    
    # Audit fields
    created_by_id = Column(GUID(), ForeignKey('users.id'), nullable=True)
    created_by = relationship("User", foreign_keys=[created_by_id])
    
    __table_args__ = (
        CheckConstraint("start_date <= end_date", name='check_valid_date_range'),
    )
    
    def generate_forecast(self, db) -> Dict[str, Any]:
        """Generate or update the forecast data."""
        # This would be implemented to generate the actual forecast
        # based on historical data, recurring transactions, etc.
        forecast = {
            'periods': [],
            'summary': {
                'total_inflows': 0,
                'total_outflows': 0,
                'net_cash_flow': 0,
                'ending_balance': 0
            }
        }
        
        # Update timestamps
        self.last_calculated_at = datetime.utcnow()
        self.forecast_data = forecast
        
        return forecast


class TransactionMatchingRule(BaseModel):
    """
    Defines rules for automatically matching and categorizing bank transactions.
    """
    __tablename__ = "transaction_matching_rules"
    
    # Rule details
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    priority = Column(Integer, default=0, nullable=False)  # Higher priority runs first
    
    # Matching criteria
    reference_pattern = Column(String(200), nullable=True)  # Regex pattern for reference matching
    description_pattern = Column(String(200), nullable=True)  # Regex pattern for description matching
    amount_min = Column(Numeric(20, 6), nullable=True)
    amount_max = Column(Numeric(20, 6), nullable=True)
    
    # Action to take when matched
    category = Column(ENUM(CashFlowCategory), nullable=True)
    payment_method = Column(ENUM(PaymentMethod), nullable=True)
    auto_categorize = Column(Boolean, default=False, nullable=False)
    auto_approve = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    created_by_id = Column(GUID(), ForeignKey('users.id'), nullable=True)
    created_by = relationship("User", foreign_keys=[created_by_id])
    
    __table_args__ = (
        CheckConstraint(
            "(amount_min IS NULL) OR (amount_max IS NULL) OR (amount_min <= amount_max)",
            name='check_valid_amount_range'
        ),
    )
    
    def apply_to_transaction(self, transaction: BankTransaction) -> bool:
        """Apply this rule to a transaction if it matches."""
        if not self.match_rule(transaction):
            return False
            
        if self.auto_categorize and self.category:
            transaction.category = self.category
            
        if self.payment_method:
            transaction.payment_method = self.payment_method
            
        if self.auto_approve:
            transaction.status = TransactionStatus.APPROVED
            
        return True
