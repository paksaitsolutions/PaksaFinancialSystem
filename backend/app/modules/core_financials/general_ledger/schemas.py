"""
General Ledger Pydantic schemas for API validation.
"""
from datetime import date
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.base import BaseSchema, BaseCreateSchema, BaseUpdateSchema, AuditResponseSchema
from app.modules.core_financials.general_ledger.models import AccountType

class AccountCreate(BaseCreateSchema):
    account_code: str = Field(..., max_length=20)
    account_name: str = Field(..., max_length=100)
    account_type: AccountType
    parent_account_id: Optional[int] = None
    description: Optional[str] = None

class AccountUpdate(BaseUpdateSchema):
    account_name: Optional[str] = Field(None, max_length=100)
    parent_account_id: Optional[int] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class AccountResponse(AuditResponseSchema):
    account_code: str
    account_name: str
    account_type: AccountType
    parent_account_id: Optional[int] = None
    description: Optional[str] = None

class JournalEntryLineCreate(BaseSchema):
    account_id: int
    description: Optional[str] = None
    debit_amount: Decimal = Field(default=0, ge=0)
    credit_amount: Decimal = Field(default=0, ge=0)

class JournalEntryCreate(BaseCreateSchema):
    entry_date: date
    description: str
    reference: Optional[str] = None
    lines: List[JournalEntryLineCreate]

class JournalEntryLineResponse(BaseSchema):
    id: int
    account_id: int
    description: Optional[str] = None
    debit_amount: Decimal
    credit_amount: Decimal

class JournalEntryResponse(AuditResponseSchema):
    entry_number: str
    entry_date: date
    description: str
    reference: Optional[str] = None
    total_debit: Decimal
    total_credit: Decimal
    status: str
    lines: List[JournalEntryLineResponse]

class TrialBalanceItem(BaseSchema):
    account_code: str
    account_name: str
    debit_balance: Decimal
    credit_balance: Decimal

class TrialBalanceResponse(BaseSchema):
    as_of_date: date
    accounts: List[TrialBalanceItem]
    total_debits: Decimal
    total_credits: Decimal