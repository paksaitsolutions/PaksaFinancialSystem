from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional, TYPE_CHECKING, Dict, Any
from sqlalchemy import (
    Column, String, Numeric, Date, DateTime, 
    ForeignKey, Enum as SQLEnum, Text, Boolean, CheckConstraint, 
    select, and_, or_
)
from sqlalchemy.orm import relationship, Mapped, mapped_column, joinedload
from sqlalchemy.sql import func, case
from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseModel, GUID
from .currency import Currency, ExchangeRate

if TYPE_CHECKING:
    from .user import User

class ChartOfAccounts(BaseModel):
    """
    Represents the chart of accounts in the general ledger.
    """
    __tablename__ = "chart_of_accounts"
    
    # Account identification
    code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Account classification
    category = Column(String(50), nullable=False)  # Asset, Liability, Equity, Revenue, Expense
    account_type = Column(String(50), nullable=False)  # e.g., Current Asset, Fixed Asset, etc.
    
    # Account properties
    is_active = Column(Boolean, default=True, nullable=False)
    is_system = Column(Boolean, default=False, nullable=False)  # System accounts cannot be modified
    is_contra = Column(Boolean, default=False, nullable=False)  # For contra-accounts
    
    # Hierarchical structure
    parent_id = Column(GUID(), ForeignKey('chart_of_accounts.id'), nullable=True)
    
    # Financial attributes
    currency_id = Column(GUID(), ForeignKey('currencies.id'), nullable=False)
    is_base_currency = Column(Boolean, default=False, nullable=False)  # If True, this is the base currency account
    normal_balance = Column(String(1), nullable=False)  # 'D' for Debit, 'C' for Credit
    
    # Currency relationship
    currency = relationship("Currency", back_populates="gl_accounts")
    
    # Relationships
    parent = relationship(
        "ChartOfAccounts", 
        remote_side="ChartOfAccounts.id",
        back_populates="children"
    )
    children = relationship(
        "ChartOfAccounts", 
        back_populates="parent",
        cascade="all, delete-orphan"
    )
    journal_entries = relationship(
        "JournalEntryItem", 
        back_populates="account",
        cascade="all, delete-orphan"
    )
    
    # Audit fields
    created_by_id = Column(GUID(), ForeignKey('users.id'), nullable=True)
    updated_by_id = Column(GUID(), ForeignKey('users.id'), nullable=True)
    
    created_by = relationship("User", foreign_keys=[created_by_id])
    updated_by = relationship("User", foreign_keys=[updated_by_id])
    
    __table_args__ = (
        CheckConstraint(
            "normal_balance IN ('D', 'C')",
            name='check_normal_balance'
        ),
        CheckConstraint(
            "category IN ('Asset', 'Liability', 'Equity', 'Revenue', 'Expense')",
            name='check_account_category'
        ),
    )
    
    @property
    def full_code(self) -> str:
        """Return the full hierarchical account code."""
        if self.parent:
            return f"{self.parent.full_code}.{self.code}"
        return self.code
    
    @property
    def level(self) -> int:
        """Return the level of the account in the hierarchy."""
        if not self.parent:
            return 0
        return self.parent.level + 1
    
    @property
    def is_debit_balance(self) -> bool:
        """Return True if the account normally has a debit balance."""
        return self.normal_balance == 'D'
    
    @property
    def is_credit_balance(self) -> bool:
        """Return True if the account normally has a credit balance."""
        return self.normal_balance == 'C'
    
    async def get_balance(
        self, 
        db, 
        start_date: Optional[date] = None, 
        end_date: Optional[date] = None
    ) -> Decimal:
        """Calculate the account balance within a date range."""
        from sqlalchemy import select, func, and_
        from .journal_entry import JournalEntryItem
        
        # Build the query
        query = select(
            func.coalesce(func.sum(JournalEntryItem.amount), 0)
        ).where(
            JournalEntryItem.account_id == self.id
        )
        
        # Apply date filters if provided
        if start_date:
            query = query.join(JournalEntryItem.journal_entry).where(
                JournalEntryItem.journal_entry.has(date_posted >= start_date)
            )
        if end_date:
            query = query.join(JournalEntryItem.journal_entry).where(
                JournalEntryItem.journal_entry.has(date_posted <= end_date)
            )
        
        result = await db.execute(query)
        balance = result.scalar_one() or Decimal('0.00')
        
        # Adjust for normal balance
        if self.is_credit_balance:
            balance = -balance
            
        return balance
    
    def __repr__(self) -> str:
        return f"<ChartOfAccounts(id={self.id}, code='{self.code}', name='{self.name}')>"

class JournalEntry(BaseModel):
    """
    Represents a journal entry in the general ledger with multi-currency support.
    """
    __tablename__ = "journal_entries"
    
    # Entry identification
    entry_number = Column(String(50), unique=True, index=True, nullable=False)
    reference = Column(String(100), nullable=True, index=True)  # External reference
    memo = Column(Text, nullable=True)  # Description of the entry
    
    # Entry details
    date_posted = Column(Date, nullable=False, index=True)  # Accounting date
    date_created = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Status and type
    status = Column(String(20), default='draft', nullable=False)  # draft, posted, void
    entry_type = Column(String(50), nullable=True)  # e.g., 'manual', 'recurring', 'reversal', 'adjustment'
    
    # Recurring entry details
    is_recurring = Column(Boolean, default=False, nullable=False)
    recurring_frequency = Column(String(20), nullable=True)  # daily, weekly, monthly, quarterly, yearly
    recurring_end_date = Column(Date, nullable=True)
    
    # Multi-currency information
    base_currency_id = Column(GUID(), ForeignKey('currencies.id'), nullable=True)
    exchange_rate_date = Column(Date, nullable=True)  # Date used for exchange rates
    
    # Audit fields
    created_by_id = Column(GUID(), ForeignKey('users.id'), nullable=True)
    posted_by_id = Column(GUID(), ForeignKey('users.id'), nullable=True)
    posted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    items: Mapped[List["JournalEntryItem"]] = relationship(
        "JournalEntryItem", 
        back_populates="journal_entry",
        cascade="all, delete-orphan"
    )
    base_currency = relationship("Currency", foreign_keys=[base_currency_id])
    created_by = relationship("User", foreign_keys=[created_by_id])
    posted_by = relationship("User", foreign_keys=[posted_by_id])
    
    __table_args__ = (
        CheckConstraint(
            "status IN ('draft', 'posted', 'void')",
            name='check_journal_entry_status'
        ),
        CheckConstraint(
            "(is_recurring = false) OR (recurring_frequency IS NOT NULL)",
            name='check_recurring_has_frequency'
        ),
        CheckConstraint(
            "(base_currency_id IS NULL) = (exchange_rate_date IS NULL)",
            name='check_currency_and_date_both_set'
        ),
    )
    
    @property
    def has_foreign_currency(self) -> bool:
        """Check if this entry contains any foreign currency items."""
        return any(item.currency_id != self.base_currency_id for item in self.items)
    
    @property
    def is_balanced(self) -> bool:
        """Check if the journal entry is balanced in terms of debits and credits."""
        total_debit = sum(
            item.amount for item in self.items 
            if item.side == 'debit' and item.currency_id == self.base_currency_id
        )
        total_credit = sum(
            item.amount for item in self.items 
            if item.side == 'credit' and item.currency_id == self.base_currency_id
        )
        return total_debit == total_credit
    
    @property
    def is_balanced_in_foreign_currencies(self) -> bool:
        """Check if the journal entry is balanced for each foreign currency."""
        if not self.base_currency_id:
            return True
            
        currency_balances = {}
            
        for item in self.items:
            if item.currency_id != self.base_currency_id:
                amount = item.amount if item.side == 'debit' else -item.amount
                currency_balances[item.currency_id] = currency_balances.get(item.currency_id, 0) + amount
                
        return all(abs(balance) < Decimal('0.01') for balance in currency_balances.values())
    
    async def validate_balances(self, db) -> bool:
        """Validate that all items are properly balanced in their respective currencies."""
        if not self.base_currency_id:
            # If no base currency is set, we can't validate foreign currency balances
            return self.is_balanced
            
        if not self.is_balanced:
            return False
            
        if not self.is_balanced_in_foreign_currencies:
            return False
            
        # Verify that all foreign currency items have valid exchange rates
        for item in self.items:
            if item.currency_id != self.base_currency_id and not item.exchange_rate:
                # Try to get an exchange rate if not set
                rate = await ExchangeRate.get_rate(
                    db,
                    source_currency_id=item.currency_id,
                    target_currency_id=self.base_currency_id,
                    date=self.exchange_rate_date or self.date_posted
                )
                if not rate:
                    return False
                    
        return True
    
    async def post(self, db, user_id: str) -> None:
        """Post the journal entry."""
        if self.status != 'draft':
            raise ValueError("Only draft entries can be posted")
        
        if not await self.validate_balances(db):
            raise ValueError("Journal entry is not balanced")
        
        self.status = 'posted'
        self.posted_by_id = user_id
        self.posted_at = datetime.utcnow()
        
        # In a real implementation, you would update the account balances here
        # This would involve creating account balance records for each account/period
        # and updating them with the transaction amounts
    
    async def void(self, user_id: str) -> None:
        """Void the journal entry."""
        if self.status != 'posted':
            raise ValueError("Only posted entries can be voided")
        
        self.status = 'void'
        self.updated_by_id = user_id
        self.updated_at = datetime.utcnow()
        
        # In a real implementation, you would reverse the account balances here
    
    @property
    def total_debits(self) -> Decimal:
        """Calculate the total debits in the journal entry."""
        return sum(
            item.amount for item in self.items 
            if item.side == 'debit'
        )
    
    @property
    def total_credits(self) -> Decimal:
        """Calculate the total credits in the journal entry."""
        return sum(
            item.amount for item in self.items 
            if item.side == 'credit'
        )
    
    def __repr__(self) -> str:
        return f"<JournalEntry(id={self.id}, entry_number='{self.entry_number}', date='{self.date_posted}')>"

class JournalEntryItem(BaseModel):
    """
    Represents a line item in a journal entry with multi-currency support.
    """
    __tablename__ = "journal_entry_items"
    
    # Entry item details
    journal_entry_id = Column(GUID(), ForeignKey('journal_entries.id', ondelete='CASCADE'), nullable=False)
    account_id = Column(GUID(), ForeignKey('chart_of_accounts.id'), nullable=False)
    
    # Amount and type
    side = Column(String(10), nullable=False)  # 'debit' or 'credit'
    amount = Column(Numeric(20, 6), nullable=False)  # Always positive, in the account's currency
    
    # Currency information
    currency_id = Column(GUID(), ForeignKey('currencies.id'), nullable=False)
    
    # Foreign currency information (if different from account's currency)
    foreign_currency_id = Column(GUID(), ForeignKey('currencies.id'), nullable=True)
    foreign_amount = Column(Numeric(20, 6), nullable=True)  # Amount in foreign currency
    exchange_rate = Column(Numeric(20, 10), nullable=True)  # Rate from foreign to account currency
    
    # Description and reference
    description = Column(Text, nullable=True)
    reference = Column(String(100), nullable=True)  # External reference for this line
    
    # Tax information
    tax_code = Column(String(20), nullable=True)
    tax_amount = Column(Numeric(20, 6), nullable=True)
    
    # Project/Department tracking
    project_id = Column(GUID(), ForeignKey('projects.id'), nullable=True)
    department_id = Column(GUID(), ForeignKey('departments.id'), nullable=True)
    
    # Relationships
    journal_entry = relationship("JournalEntry", back_populates="items")
    account = relationship("ChartOfAccounts", back_populates="journal_entries")
    currency = relationship("Currency", foreign_keys=[currency_id])
    foreign_currency = relationship("Currency", foreign_keys=[foreign_currency_id])
    
    # Audit fields
    created_by_id = Column(GUID(), ForeignKey('users.id'), nullable=True)
    created_by = relationship("User", foreign_keys=[created_by_id])
    
    __table_args__ = (
        CheckConstraint(
            "side IN ('debit', 'credit')",
            name='check_journal_item_side'
        ),
        CheckConstraint(
            "amount >= 0",
            name='check_positive_amount'
        ),
        CheckConstraint(
            "(foreign_currency_id IS NULL) = (foreign_amount IS NULL)",
            name='check_foreign_currency_and_amount_both_set'
        ),
        CheckConstraint(
            "(foreign_currency_id IS NULL) OR (exchange_rate IS NOT NULL)",
            name='check_exchange_rate_set_for_foreign_currency'
        ),
    )
    
    @property
    def is_foreign_currency(self) -> bool:
        """Check if this item is in a foreign currency."""
        return self.foreign_currency_id is not None
    
    @property
    def effective_currency_id(self) -> UUID:
        """Get the effective currency ID for this item."""
        return self.foreign_currency_id or self.currency_id
    
    @property
    def signed_amount(self) -> Decimal:
        """Return the signed amount based on the side."""
        if self.side == 'debit':
            return self.amount
        return -self.amount
    
    async def get_account(self, db) -> Optional[ChartOfAccounts]:
        """Get the account associated with this item."""
        from sqlalchemy import select
        
        result = await db.execute(
            select(ChartOfAccounts).where(ChartOfAccounts.id == self.account_id)
        )
        return result.scalars().first()
    
    def __repr__(self) -> str:
        return f"<JournalEntryItem(id={self.id}, account_id={self.account_id}, {self.side} {self.amount})>"

# Add relationships to ChartOfAccounts that couldn't be defined earlier
ChartOfAccounts.journal_entries = relationship("JournalEntryItem", back_populates="account")
