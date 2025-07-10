"""
Paksa Financial System 
Account Model

This module defines the Account model for the General Ledger system.
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4

from sqlalchemy import (
    Column, String, Numeric, Boolean, ForeignKey, 
    DateTime, Enum as SQLEnum, Text, JSON, UniqueConstraint, Index
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship, validates

from app.db.base_class import Base


class AccountType(str, Enum):
    """Types of accounts in the chart of accounts."""
    ASSET = 'asset'
    LIABILITY = 'liability'
    EQUITY = 'equity'
    REVENUE = 'revenue'
    EXPENSE = 'expense'
    GAIN = 'gain'
    LOSS = 'loss'
    TEMPORARY = 'temporary'


class AccountStatus(str, Enum):
    """Status of an account."""
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    CLOSED = 'closed'


class NormalBalance(str, Enum):
    """Normal balance type for an account (debit or credit)."""
    DEBIT = 'debit'
    CREDIT = 'credit'


class Account(Base):
    """
    Represents an account in the chart of accounts.
    """
    __tablename__ = 'gl_accounts'
    
    # Primary Key
    id = Column(PG_UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    
    # Account Identification
    code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Account Classification
    type = Column(SQLEnum(AccountType), nullable=False, index=True)
    normal_balance = Column(SQLEnum(NormalBalance), nullable=False)
    
    # Hierarchy Management
    parent_id = Column(PG_UUID(as_uuid=True), ForeignKey('gl_accounts.id', ondelete='RESTRICT'), index=True)
    path = Column(Text, index=True)  # Materialized path for hierarchy queries
    level = Column(Numeric(2, 0), nullable=False, default=0)  # Depth in hierarchy
    
    # Status and Control
    status = Column(SQLEnum(AccountStatus), default=AccountStatus.ACTIVE, nullable=False, index=True)
    is_contra = Column(Boolean, default=False, nullable=False)  # For contra-accounts
    is_bank_account = Column(Boolean, default=False, nullable=False)
    is_cash_account = Column(Boolean, default=False, nullable=False)
    is_reconcilable = Column(Boolean, default=False, nullable=False, index=True)
    
    # Financial Settings
    currency_code = Column(String(3), nullable=False, default='PKR')
    tax_code = Column(String(20), nullable=True)
    
    # Metadata
    metadata_ = Column('metadata', JSON, nullable=True, default=dict)
    
    # Audit Fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(PG_UUID(as_uuid=True), nullable=False)
    updated_by = Column(PG_UUID(as_uuid=True), nullable=False)
    
    # Relationships
    parent = relationship('Account', remote_side=[id], backref='children', post_update=True)
    
    # Indexes
    __table_args__ = (
        UniqueConstraint('code', name='uq_gl_accounts_code'),
        Index('ix_gl_accounts_path_gin', 'path', postgresql_using='gin', 
              postgresql_ops={'path': 'gin_trgm_ops'}),
    )
    
    @validates('code')
    def validate_code(self, key: str, code: str) -> str:
        """Validate account code format."""
        if not code or not code.strip():
            raise ValueError("Account code cannot be empty")
        # Add any additional validation rules for account codes
        return code.strip().upper()
    
    @validates('type', 'normal_balance')
    def validate_normal_balance(self, key: str, value: Any) -> Any:
        """Validate normal balance based on account type."""
        if key == 'type' and hasattr(self, 'normal_balance'):
            # Update normal balance based on account type if not set
            if value in (AccountType.ASSET, AccountType.EXPENSE, AccountType.LOSS):
                self.normal_balance = NormalBalance.DEBIT
            elif value in (AccountType.LIABILITY, AccountType.EQUITY, AccountType.REVENUE, AccountType.GAIN):
                self.normal_balance = NormalBalance.CREDIT
        return value
    
    def __repr__(self) -> str:
        return f"<Account(id={self.id}, code='{self.code}', name='{self.name}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert account to dictionary."""
        return {
            'id': str(self.id),
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'type': self.type.value,
            'normal_balance': self.normal_balance.value,
            'parent_id': str(self.parent_id) if self.parent_id else None,
            'path': self.path,
            'level': int(self.level) if self.level is not None else 0,
            'status': self.status.value,
            'is_contra': self.is_contra,
            'is_bank_account': self.is_bank_account,
            'is_cash_account': self.is_cash_account,
            'is_reconcilable': self.is_reconcilable,
            'currency_code': self.currency_code,
            'tax_code': self.tax_code,
            'metadata': self.metadata_ or {},
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': str(self.created_by) if self.created_by else None,
            'updated_by': str(self.updated_by) if self.updated_by else None,
        }
