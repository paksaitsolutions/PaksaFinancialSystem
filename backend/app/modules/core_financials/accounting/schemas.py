import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field

from .models import AccountStatus, AccountType, JournalEntryStatus, AccountSubType

# ================================================
#               Account Schemas
# ================================================

class AccountBase(BaseModel):
    """Base schema for account data."""
    code: str = Field(..., max_length=20, description="Unique code for the account.")
    name: str = Field(..., max_length=100, description="Name of the account.")
    description: Optional[str] = Field(None, description="Detailed description of the account.")
    type: AccountType = Field(..., description="The main type of the account (e.g., Asset, Liability).")
    subtype: Optional[AccountSubType] = Field(None, description="A more specific subtype for the account.")
    currency: str = Field('USD', max_length=3, description="Currency code for the account.")
    is_contra: bool = Field(False, description="Indicates if this is a contra account.")
    is_system_account: bool = Field(False, description="Indicates if this is a system-managed account.")
    status: AccountStatus = Field(AccountStatus.ACTIVE, description="The current status of the account.")

class AccountCreate(AccountBase):
    """Schema for creating a new account."""
    parent_id: Optional[uuid.UUID] = Field(None, description="The parent account ID for hierarchical structure.")

class AccountUpdate(BaseModel):
    """Schema for updating an existing account. All fields are optional."""
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    status: Optional[AccountStatus] = None

class Account(AccountBase):
    """Schema for representing an account, including read-only fields."""
    id: uuid.UUID
    parent_id: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime
    normal_balance: str = Field(..., description="The normal balance side (debit or credit).")

    class Config:
        orm_mode = True

class AccountTree(Account):
    """Represents an account with its children for a hierarchical view."""
    children: List['AccountTree'] = []

# Update forward reference
AccountTree.update_forward_refs()

# ================================================
#            Journal Entry Schemas
# ================================================

class JournalEntryLineBase(BaseModel):
    """Base schema for a journal entry line."""
    account_id: uuid.UUID = Field(..., description="The ID of the account to be debited or credited.")
    debit: Decimal = Field(Decimal(0), ge=0, description="The debit amount.")
    credit: Decimal = Field(Decimal(0), ge=0, description="The credit amount.")
    description: Optional[str] = Field(None, description="Description for the line item.")

class JournalEntryLineCreate(JournalEntryLineBase):
    """Schema for creating a new journal entry line within a journal entry."""
    pass

class JournalEntryLine(JournalEntryLineBase):
    """Schema for representing a journal entry line."""
    id: uuid.UUID
    line_number: int

    class Config:
        orm_mode = True

class JournalEntryBase(BaseModel):
    """Base schema for a journal entry."""
    entry_date: datetime = Field(..., description="The date the journal entry is recorded for.")
    reference: Optional[str] = Field(None, max_length=100, description="External reference for the entry.")
    description: Optional[str] = Field(None, description="Overall description of the journal entry.")
    status: JournalEntryStatus = Field(JournalEntryStatus.DRAFT, description="The status of the entry.")

class JournalEntryCreate(JournalEntryBase):
    """Schema for creating a new journal entry with its lines."""
    lines: List[JournalEntryLineCreate] = Field(..., min_items=2, description="List of debit/credit lines.")

class JournalEntryUpdate(BaseModel):
    """Schema for updating an existing journal entry. All fields are optional."""
    entry_date: Optional[datetime] = None
    reference: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    status: Optional[JournalEntryStatus] = None

class JournalEntry(JournalEntryBase):
    """Schema for representing a full journal entry, including read-only fields."""
    id: uuid.UUID
    entry_number: str
    total_debit: Decimal
    total_credit: Decimal
    posted_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    lines: List[JournalEntryLine]

    class Config:
        orm_mode = True
