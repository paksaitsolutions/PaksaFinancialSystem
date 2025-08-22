<<<<<<< HEAD
"""
Banking models for the financial system.
"""
from datetime import datetime, date
from decimal import Decimal
from enum import Enum, auto
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean, 
    CheckConstraint, 
    Column, 
    Date, 
    DateTime, 
    Enum as SQLEnum, 
    ForeignKey, 
    Numeric, 
    String, 
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


class BankAccountType(str, Enum):
    """Types of bank accounts."""
    CHECKING = 'checking'
    SAVINGS = 'savings'
    MONEY_MARKET = 'money_market'
    CREDIT_CARD = 'credit_card'
    LINE_OF_CREDIT = 'line_of_credit'
    PAYMENT_PROCESSOR = 'payment_processor'  # e.g., PayPal, Stripe


class BankAccountStatus(str, Enum):
    """Status of a bank account."""
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    CLOSED = 'closed'
    DORMANT = 'dormant'


class BankTransactionType(str, Enum):
    """Types of bank transactions."""
    DEPOSIT = 'deposit'
    WITHDRAWAL = 'withdrawal'
    TRANSFER_IN = 'transfer_in'
    TRANSFER_OUT = 'transfer_out'
    FEE = 'fee'
    INTEREST = 'interest'
    ADJUSTMENT = 'adjustment'
    PAYMENT = 'payment'
    REFUND = 'refund'
    REVERSAL = 'reversal'
    CHECK = 'check'
    DIRECT_DEBIT = 'direct_debit'
    STANDING_ORDER = 'standing_order'
    DIRECT_DEPOSIT = 'direct_deposit'
    ATM = 'atm'
    POINT_OF_SALE = 'point_of_sale'
    ONLINE_PAYMENT = 'online_payment'
    OTHER = 'other'


class BankTransactionStatus(str, Enum):
    """Status of a bank transaction."""
    PENDING = 'pending'
    POSTED = 'posted'
    CLEARED = 'cleared'
    VOID = 'void'
    RECONCILED = 'reconciled'


class BankAccount(Base):
    """Bank account model for tracking financial institution accounts."""
    __tablename__ = 'bank_account'
    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    account_number: Mapped[Optional[str]] = mapped_column(String(50))
    routing_number: Mapped[Optional[str]] = mapped_column(String(20))  # For US/Canada
    iban: Mapped[Optional[str]] = mapped_column(String(34))  # International Bank Account Number
    swift_code: Mapped[Optional[str]] = mapped_column(String(11))  # SWIFT/BIC code
    
    # Account details
    account_type: Mapped[BankAccountType] = mapped_column(SQLEnum(BankAccountType), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default='USD', nullable=False)
    opening_balance: Mapped[Decimal] = mapped_column(Numeric(19, 4), default=0)
    current_balance: Mapped[Decimal] = mapped_column(Numeric(19, 4), default=0)
    available_balance: Mapped[Optional[Decimal]] = mapped_column(Numeric(19, 4))
    
    # Status and dates
    status: Mapped[BankAccountStatus] = mapped_column(
        SQLEnum(BankAccountStatus), 
        default=BankAccountStatus.ACTIVE,
        nullable=False,
    )
    opened_date: Mapped[date] = mapped_column(Date, default=date.today)
    closed_date: Mapped[Optional[date]]
    last_reconciled_date: Mapped[Optional[date]]
    
    # Bank information
    bank_name: Mapped[str] = mapped_column(String(100), nullable=False)
    bank_branch: Mapped[Optional[str]] = mapped_column(String(100))
    bank_address: Mapped[Optional[str]] = mapped_column(Text)
    bank_phone: Mapped[Optional[str]] = mapped_column(String(20))
    bank_website: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Accounting integration
    account_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('account.id'))
    account: Mapped[Optional['Account']] = relationship('Account')
    
    # Audit fields
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now(),
    )
    
    # Relationships
    transactions: Mapped[List['BankTransaction']] = relationship(
        'BankTransaction', 
        back_populates='bank_account',
        order_by='desc(BankTransaction.transaction_date)'
    )
    reconciliations: Mapped[List['BankReconciliation']] = relationship(
        'BankReconciliation',
        back_populates='bank_account',
        order_by='desc(BankReconciliation.end_date)'
    )
    
    # Created by/updated by
    created_by_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('user.id'))
    updated_by_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('user.id'))
    
    def __repr__(self) -> str:
        return f'<BankAccount {self.name} ({self.account_number})>'


class BankTransaction(Base):
    """Bank transaction model for tracking individual transactions."""
    __tablename__ = 'bank_transaction'
    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    transaction_id: Mapped[Optional[str]] = mapped_column(String(100), index=True)  # Bank's transaction ID
    reference: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    
    # Transaction details
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    posted_date: Mapped[Optional[date]] = mapped_column(Date, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    running_balance: Mapped[Optional[Decimal]] = mapped_column(Numeric(19, 4))
    
    # Transaction type and status
    transaction_type: Mapped[BankTransactionType] = mapped_column(
        SQLEnum(BankTransactionType), 
        nullable=False,
    )
    status: Mapped[BankTransactionStatus] = mapped_column(
        SQLEnum(BankTransactionStatus),
        default=BankTransactionStatus.PENDING,
        nullable=False,
    )
    
    # Description and metadata
    description: Mapped[Optional[str]] = mapped_column(Text)
    memo: Mapped[Optional[str]] = mapped_column(Text)
    check_number: Mapped[Optional[str]] = mapped_column(String(50))
    payee: Mapped[Optional[str]] = mapped_column(String(255))
    payer: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Additional metadata
    metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    
    # Bank account relationship
    bank_account_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), 
        ForeignKey('bank_account.id'),
        nullable=False,
    )
    bank_account: Mapped[BankAccount] = relationship('BankAccount', back_populates='transactions')
    
    # Accounting integration
    journal_entry_line_id: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True), 
        ForeignKey('journal_entry_line.id')
    )
    journal_entry_line: Mapped[Optional['JournalEntryLine']] = relationship('JournalEntryLine')
    
    # Reconciliation
    is_reconciled: Mapped[bool] = mapped_column(Boolean, default=False)
    reconciliation_id: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True), 
        ForeignKey('bank_reconciliation.id')
    )
    reconciliation: Mapped[Optional['BankReconciliation']] = relationship(
        'BankReconciliation', 
        back_populates='transactions'
    )
    
    # Audit fields
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now(),
    )
    
    # Created by/updated by
    created_by_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('user.id'))
    updated_by_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('user.id'))
    
    # Constraints
    __table_args__ = (
        UniqueConstraint(
            'bank_account_id', 
            'transaction_id',
            name='unique_transaction_per_account',
            # Allow multiple null transaction_ids per account
            postgresql_where=transaction_id.isnot(None),
        ),
    )
    
    def __repr__(self) -> str:
        return f'<BankTransaction {self.transaction_date} {self.amount} {self.transaction_type}>'
    
    @property
    def is_debit(self) -> bool:
        """Check if this is a debit transaction."""
        return self.amount < 0
    
    @property
    def is_credit(self) -> bool:
        """Check if this is a credit transaction."""
        return self.amount > 0


class BankReconciliationStatus(str, Enum):
    """Status of a bank reconciliation."""
    DRAFT = 'draft'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    ADJUSTED = 'adjusted'


class BankReconciliation(Base):
    """Bank reconciliation model for reconciling bank statements with accounting records."""
    __tablename__ = 'bank_reconciliation'
    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Reconciliation period
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    
    # Balances
    starting_balance: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    ending_balance: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    cleared_balance: Mapped[Decimal] = mapped_column(Numeric(19, 4), default=0)
    
    # Status
    status: Mapped[BankReconciliationStatus] = mapped_column(
        SQLEnum(BankReconciliationStatus),
        default=BankReconciliationStatus.DRAFT,
        nullable=False,
    )
    
    # Notes and metadata
    notes: Mapped[Optional[str]] = mapped_column(Text)
    metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    
    # Bank account relationship
    bank_account_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), 
        ForeignKey('bank_account.id'),
        nullable=False,
    )
    bank_account: Mapped[BankAccount] = relationship('BankAccount', back_populates='reconciliations')
    
    # Transactions included in this reconciliation
    transactions: Mapped[List[BankTransaction]] = relationship(
        'BankTransaction',
        back_populates='reconciliation',
    )
    
    # Audit fields
    reconciled_at: Mapped[Optional[datetime]]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now(),
    )
    
    # Created by/updated by
    created_by_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('user.id'))
    updated_by_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('user.id'))
    reconciled_by_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('user.id'))
    
    def __repr__(self) -> str:
        return f'<BankReconciliation {self.name} ({self.start_date} to {self.end_date})>'
    
    @property
    def difference(self) -> Decimal:
        """Calculate the difference between cleared balance and statement balance."""
        return self.cleared_balance - self.ending_balance
=======
"""
Banking models for the financial system.
"""
from datetime import datetime, date
from decimal import Decimal
from enum import Enum, auto
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean, 
    CheckConstraint, 
    Column, 
    Date, 
    DateTime, 
    Enum as SQLEnum, 
    ForeignKey, 
    Numeric, 
    String, 
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class BankAccountType(str, Enum):
    """Types of bank accounts."""
    CHECKING = 'checking'
    SAVINGS = 'savings'
    MONEY_MARKET = 'money_market'
    CREDIT_CARD = 'credit_card'
    LINE_OF_CREDIT = 'line_of_credit'
    PAYMENT_PROCESSOR = 'payment_processor'  # e.g., PayPal, Stripe


class BankAccountStatus(str, Enum):
    """Status of a bank account."""
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    CLOSED = 'closed'
    DORMANT = 'dormant'


class BankTransactionType(str, Enum):
    """Types of bank transactions."""
    DEPOSIT = 'deposit'
    WITHDRAWAL = 'withdrawal'
    TRANSFER_IN = 'transfer_in'
    TRANSFER_OUT = 'transfer_out'
    FEE = 'fee'
    INTEREST = 'interest'
    ADJUSTMENT = 'adjustment'
    PAYMENT = 'payment'
    REFUND = 'refund'
    REVERSAL = 'reversal'
    CHECK = 'check'
    DIRECT_DEBIT = 'direct_debit'
    STANDING_ORDER = 'standing_order'
    DIRECT_DEPOSIT = 'direct_deposit'
    ATM = 'atm'
    POINT_OF_SALE = 'point_of_sale'
    ONLINE_PAYMENT = 'online_payment'
    OTHER = 'other'


class BankTransactionStatus(str, Enum):
    """Status of a bank transaction."""
    PENDING = 'pending'
    POSTED = 'posted'
    CLEARED = 'cleared'
    VOID = 'void'
    RECONCILED = 'reconciled'


class BankAccount(Base):
    """Bank account model for tracking financial institution accounts."""
    __tablename__ = 'bank_account'
    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    account_number: Mapped[Optional[str]] = mapped_column(String(50))
    routing_number: Mapped[Optional[str]] = mapped_column(String(20))  # For US/Canada
    iban: Mapped[Optional[str]] = mapped_column(String(34))  # International Bank Account Number
    swift_code: Mapped[Optional[str]] = mapped_column(String(11))  # SWIFT/BIC code
    
    # Account details
    account_type: Mapped[BankAccountType] = mapped_column(SQLEnum(BankAccountType), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default='USD', nullable=False)
    opening_balance: Mapped[Decimal] = mapped_column(Numeric(19, 4), default=0)
    current_balance: Mapped[Decimal] = mapped_column(Numeric(19, 4), default=0)
    available_balance: Mapped[Optional[Decimal]] = mapped_column(Numeric(19, 4))
    
    # Status and dates
    status: Mapped[BankAccountStatus] = mapped_column(
        SQLEnum(BankAccountStatus), 
        default=BankAccountStatus.ACTIVE,
        nullable=False,
    )
    opened_date: Mapped[date] = mapped_column(Date, default=date.today)
    closed_date: Mapped[Optional[date]]
    last_reconciled_date: Mapped[Optional[date]]
    
    # Bank information
    bank_name: Mapped[str] = mapped_column(String(100), nullable=False)
    bank_branch: Mapped[Optional[str]] = mapped_column(String(100))
    bank_address: Mapped[Optional[str]] = mapped_column(Text)
    bank_phone: Mapped[Optional[str]] = mapped_column(String(20))
    bank_website: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Accounting integration
    account_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('account.id'))
    account: Mapped[Optional['Account']] = relationship('Account')
    
    # Audit fields
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now(),
    )
    
    # Relationships
    transactions: Mapped[List['BankTransaction']] = relationship(
        'BankTransaction', 
        back_populates='bank_account',
        order_by='desc(BankTransaction.transaction_date)'
    )
    reconciliations: Mapped[List['BankReconciliation']] = relationship(
        'BankReconciliation',
        back_populates='bank_account',
        order_by='desc(BankReconciliation.end_date)'
    )
    
    # Created by/updated by
    created_by_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('user.id'))
    updated_by_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('user.id'))
    
    def __repr__(self) -> str:
        return f'<BankAccount {self.name} ({self.account_number})>'


class BankTransaction(Base):
    """Bank transaction model for tracking individual transactions."""
    __tablename__ = 'bank_transaction'
    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    transaction_id: Mapped[Optional[str]] = mapped_column(String(100), index=True)  # Bank's transaction ID
    reference: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    
    # Transaction details
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    posted_date: Mapped[Optional[date]] = mapped_column(Date, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    running_balance: Mapped[Optional[Decimal]] = mapped_column(Numeric(19, 4))
    
    # Transaction type and status
    transaction_type: Mapped[BankTransactionType] = mapped_column(
        SQLEnum(BankTransactionType), 
        nullable=False,
    )
    status: Mapped[BankTransactionStatus] = mapped_column(
        SQLEnum(BankTransactionStatus),
        default=BankTransactionStatus.PENDING,
        nullable=False,
    )
    
    # Description and metadata
    description: Mapped[Optional[str]] = mapped_column(Text)
    memo: Mapped[Optional[str]] = mapped_column(Text)
    check_number: Mapped[Optional[str]] = mapped_column(String(50))
    payee: Mapped[Optional[str]] = mapped_column(String(255))
    payer: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Additional metadata
    metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    
    # Bank account relationship
    bank_account_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), 
        ForeignKey('bank_account.id'),
        nullable=False,
    )
    bank_account: Mapped[BankAccount] = relationship('BankAccount', back_populates='transactions')
    
    # Accounting integration
    journal_entry_line_id: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True), 
        ForeignKey('journal_entry_line.id')
    )
    journal_entry_line: Mapped[Optional['JournalEntryLine']] = relationship('JournalEntryLine')
    
    # Reconciliation
    is_reconciled: Mapped[bool] = mapped_column(Boolean, default=False)
    reconciliation_id: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True), 
        ForeignKey('bank_reconciliation.id')
    )
    reconciliation: Mapped[Optional['BankReconciliation']] = relationship(
        'BankReconciliation', 
        back_populates='transactions'
    )
    
    # Audit fields
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now(),
    )
    
    # Created by/updated by
    created_by_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('user.id'))
    updated_by_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('user.id'))
    
    # Constraints
    __table_args__ = (
        UniqueConstraint(
            'bank_account_id', 
            'transaction_id',
            name='unique_transaction_per_account',
            # Allow multiple null transaction_ids per account
            postgresql_where=transaction_id.isnot(None),
        ),
    )
    
    def __repr__(self) -> str:
        return f'<BankTransaction {self.transaction_date} {self.amount} {self.transaction_type}>'
    
    @property
    def is_debit(self) -> bool:
        """Check if this is a debit transaction."""
        return self.amount < 0
    
    @property
    def is_credit(self) -> bool:
        """Check if this is a credit transaction."""
        return self.amount > 0


class BankReconciliationStatus(str, Enum):
    """Status of a bank reconciliation."""
    DRAFT = 'draft'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    ADJUSTED = 'adjusted'


class BankReconciliation(Base):
    """Bank reconciliation model for reconciling bank statements with accounting records."""
    __tablename__ = 'bank_reconciliation'
    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Reconciliation period
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    
    # Balances
    starting_balance: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    ending_balance: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    cleared_balance: Mapped[Decimal] = mapped_column(Numeric(19, 4), default=0)
    
    # Status
    status: Mapped[BankReconciliationStatus] = mapped_column(
        SQLEnum(BankReconciliationStatus),
        default=BankReconciliationStatus.DRAFT,
        nullable=False,
    )
    
    # Notes and metadata
    notes: Mapped[Optional[str]] = mapped_column(Text)
    metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    
    # Bank account relationship
    bank_account_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), 
        ForeignKey('bank_account.id'),
        nullable=False,
    )
    bank_account: Mapped[BankAccount] = relationship('BankAccount', back_populates='reconciliations')
    
    # Transactions included in this reconciliation
    transactions: Mapped[List[BankTransaction]] = relationship(
        'BankTransaction',
        back_populates='reconciliation',
    )
    
    # Audit fields
    reconciled_at: Mapped[Optional[datetime]]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now(),
    )
    
    # Created by/updated by
    created_by_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('user.id'))
    updated_by_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('user.id'))
    reconciled_by_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('user.id'))
    
    def __repr__(self) -> str:
        return f'<BankReconciliation {self.name} ({self.start_date} to {self.end_date})>'
    
    @property
    def difference(self) -> Decimal:
        """Calculate the difference between cleared balance and statement balance."""
        return self.cleared_balance - self.ending_balance
>>>>>>> e96df7278ce4216131b6c65d411c0723f4de7f91
