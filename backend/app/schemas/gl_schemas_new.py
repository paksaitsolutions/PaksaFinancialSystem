from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime
from enum import Enum

# Enums
class AccountType(str, Enum):
    ASSET = "ASSET"
    LIABILITY = "LIABILITY"
    EQUITY = "EQUITY"
    REVENUE = "REVENUE"
    EXPENSE = "EXPENSE"

class JournalEntryStatus(str, Enum):
    DRAFT = "DRAFT"
    POSTED = "POSTED"
    REVERSED = "REVERSED"

# Base Schemas
class GLAccountBase(BaseModel):
    account_code: str = Field(..., max_length=20, example="1000")
    account_name: str = Field(..., max_length=100, example="Cash and Cash Equivalents")
    account_type: AccountType
    parent_id: Optional[int] = None
    is_active: bool = True

class GLAccountCreate(GLAccountBase):
    pass

class GLAccountUpdate(BaseModel):
    account_name: Optional[str] = None
    account_type: Optional[AccountType] = None
    parent_id: Optional[int] = None
    is_active: Optional[bool] = None

class GLAccountInDB(GLAccountBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

# Journal Entry Schemas
class JournalEntryLineBase(BaseModel):
    account_id: int
    line_number: int
    debit_amount: float = 0.0
    credit_amount: float = 0.0
    description: Optional[str] = None

class JournalEntryLineCreate(JournalEntryLineBase):
    pass

class JournalEntryLineInDB(JournalEntryLineBase):
    id: int
    journal_entry_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class JournalEntryBase(BaseModel):
    entry_number: str
    entry_date: date
    reference: Optional[str] = None
    description: Optional[str] = None
    status: JournalEntryStatus = JournalEntryStatus.DRAFT

class JournalEntryCreate(JournalEntryBase):
    lines: List[JournalEntryLineCreate]

class JournalEntryUpdate(BaseModel):
    reference: Optional[str] = None
    description: Optional[str] = None
    status: Optional[JournalEntryStatus] = None

class JournalEntryInDB(JournalEntryBase):
    id: int
    created_at: datetime
    lines: List[JournalEntryLineInDB] = []

    class Config:
        orm_mode = True

# Accounting Period Schemas
class AccountingPeriodBase(BaseModel):
    period_name: str
    start_date: date
    end_date: date
    is_closed: bool = False

class AccountingPeriodCreate(AccountingPeriodBase):
    pass

class AccountingPeriodUpdate(BaseModel):
    is_closed: Optional[bool] = None

class AccountingPeriodInDB(AccountingPeriodBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

# Trial Balance Schemas
class TrialBalanceAccount(BaseModel):
    account_code: str
    account_name: str
    debit: float
    credit: float

class TrialBalance(BaseModel):
    as_of_date: date
    accounts: List[TrialBalanceAccount]
    total_debits: float
    total_credits: float
