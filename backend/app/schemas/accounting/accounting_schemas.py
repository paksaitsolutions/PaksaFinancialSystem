"""
Accounting schemas.
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel

class ChartOfAccountsBase(BaseModel):
    """Base chart of accounts schema."""
    account_code: str
    account_name: str
    account_type: str
    parent_id: Optional[UUID] = None
    is_active: bool = True
    currency_code: str = "USD"

class ChartOfAccountsCreate(ChartOfAccountsBase):
    """Create chart of accounts schema."""
    pass

class ChartOfAccountsUpdate(BaseModel):
    """Update chart of accounts schema."""
    account_name: Optional[str] = None
    account_type: Optional[str] = None
    parent_id: Optional[UUID] = None
    is_active: Optional[bool] = None
    currency_code: Optional[str] = None

class ChartOfAccountsResponse(ChartOfAccountsBase):
    """Chart of accounts response schema."""
    id: UUID
    tenant_id: UUID
    level: int
    is_system: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class JournalEntryLineBase(BaseModel):
    """Base journal entry line schema."""
    account_id: UUID
    description: Optional[str] = None
    debit_amount: Decimal = 0
    credit_amount: Decimal = 0

class JournalEntryLineCreate(JournalEntryLineBase):
    """Create journal entry line schema."""
    pass

class JournalEntryLineResponse(JournalEntryLineBase):
    """Journal entry line response schema."""
    id: UUID
    journal_entry_id: UUID
    debit_amount_base: Decimal
    credit_amount_base: Decimal

    class Config:
        orm_mode = True

class JournalEntryBase(BaseModel):
    """Base journal entry schema."""
    entry_date: datetime
    reference: Optional[str] = None
    description: Optional[str] = None
    currency_code: str = "USD"
    exchange_rate: Decimal = 1.0
    source_company_id: Optional[UUID] = None
    target_company_id: Optional[UUID] = None

class JournalEntryCreate(JournalEntryBase):
    """Create journal entry schema."""
    lines: List[JournalEntryLineCreate]

class JournalEntryUpdate(BaseModel):
    """Update journal entry schema."""
    entry_date: Optional[datetime] = None
    reference: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class JournalEntryResponse(JournalEntryBase):
    """Journal entry response schema."""
    id: UUID
    tenant_id: UUID
    entry_number: str
    status: str
    posted_at: Optional[datetime] = None
    posted_by: Optional[UUID] = None
    lines: List[JournalEntryLineResponse]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class FinancialPeriodBase(BaseModel):
    """Base financial period schema."""
    period_name: str
    start_date: datetime
    end_date: datetime
    is_current: bool = False

class FinancialPeriodCreate(FinancialPeriodBase):
    """Create financial period schema."""
    pass

class FinancialPeriodResponse(FinancialPeriodBase):
    """Financial period response schema."""
    id: UUID
    tenant_id: UUID
    is_closed: bool
    created_at: datetime
    closed_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class AccountingRuleBase(BaseModel):
    """Base accounting rule schema."""
    rule_name: str
    trigger_event: str
    conditions: Optional[str] = None
    debit_account_id: UUID
    credit_account_id: UUID
    is_active: bool = True

class AccountingRuleCreate(AccountingRuleBase):
    """Create accounting rule schema."""
    pass

class AccountingRuleResponse(AccountingRuleBase):
    """Accounting rule response schema."""
    id: UUID
    tenant_id: UUID
    created_at: datetime

    class Config:
        orm_mode = True