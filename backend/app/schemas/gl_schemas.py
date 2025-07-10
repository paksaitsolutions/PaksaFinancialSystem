"""
Pydantic schemas for the General Ledger module.
"""
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, validator, condecimal

from app.models.gl_models import AccountType, AccountSubType, AccountStatus, JournalEntryStatus

# Shared schemas
class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints."""
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")

class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"

# Account schemas
class AccountBase(BaseModel):
    """Base account schema with common fields."""
    name: str = Field(..., max_length=200, description="Account name")
    code: str = Field(..., max_length=50, description="Account code (e.g., 1000, 2000)")
    description: Optional[str] = Field(None, description="Account description")
    account_type: AccountType = Field(..., description="Type of account")
    account_subtype: Optional[AccountSubType] = Field(None, description="Account sub-type")
    parent_id: Optional[UUID] = Field(None, description="Parent account ID")
    company_id: UUID = Field(..., description="Company this account belongs to")
    is_tax_related: bool = Field(False, description="Whether this account is related to taxes")
    is_reconcilable: bool = Field(False, description="Whether this account can be reconciled")
    currency_code: str = Field("USD", min_length=3, max_length=3, description="ISO 4217 currency code")
    opening_balance: Decimal = Field(Decimal('0'), description="Opening balance")
    opening_balance_date: Optional[date] = Field(None, description="Date of the opening balance")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    @validator('code')
    def validate_code(cls, v):
        """Validate account code format."""
        if not v or not v.strip():
            raise ValueError("Account code cannot be empty")
        # Add any additional validation rules for account codes
        return v.upper()
    
    @validator('opening_balance')
    def validate_opening_balance(cls, v):
        """Validate opening balance precision."""
        if abs(v.as_tuple().exponent) > 6:
            raise ValueError("Opening balance cannot have more than 6 decimal places")
        return v

class AccountCreate(AccountBase):
    """Schema for creating a new account."""
    pass

class AccountUpdate(BaseModel):
    """Schema for updating an existing account."""
    name: Optional[str] = Field(None, max_length=200, description="Account name")
    code: Optional[str] = Field(None, max_length=50, description="Account code")
    description: Optional[str] = Field(None, description="Account description")
    account_type: Optional[AccountType] = Field(None, description="Type of account")
    account_subtype: Optional[AccountSubType] = Field(None, description="Account sub-type")
    parent_id: Optional[UUID] = Field(None, description="Parent account ID")
    is_tax_related: Optional[bool] = Field(None, description="Whether this account is related to taxes")
    is_reconcilable: Optional[bool] = Field(None, description="Whether this account can be reconciled")
    currency_code: Optional[str] = Field(None, min_length=3, max_length=3, description="ISO 4217 currency code")
    status: Optional[AccountStatus] = Field(None, description="Account status")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class AccountResponse(AccountBase):
    """Schema for account responses."""
    id: UUID
    status: AccountStatus
    is_system_account: bool
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: UUID
    updated_by: Optional[UUID]
    
    class Config:
        orm_mode = True

class AccountTreeResponse(AccountResponse):
    """Schema for account hierarchy responses."""
    children: List['AccountTreeResponse'] = []
    
    class Config:
        orm_mode = True

class AccountBalanceResponse(BaseModel):
    """Schema for account balance responses."""
    account_id: UUID
    account_code: str
    account_name: str
    account_type: AccountType
    currency_code: str
    balance: Decimal
    total_debit: Decimal
    total_credit: Decimal
    as_of_date: date
    children: Optional[List['AccountBalanceResponse']] = None
    
    class Config:
        orm_mode = True

# Journal Entry schemas
class JournalEntryLineBase(BaseModel):
    """Base schema for journal entry lines."""
    account_id: UUID = Field(..., description="Account ID")
    description: Optional[str] = Field(None, description="Line item description")
    reference: Optional[str] = Field(None, max_length=100, description="External reference")
    tracking_category_id: Optional[UUID] = Field(None, description="Tracking category ID")

class JournalEntryLineCreate(JournalEntryLineBase):
    """Schema for creating a journal entry line."""
    debit: Decimal = Field(Decimal('0'), ge=0, description="Debit amount")
    credit: Decimal = Field(Decimal('0'), ge=0, description="Credit amount")
    
    @validator('debit', 'credit')
    def validate_amounts(cls, v, field):
        """Validate that amounts are non-negative and have proper precision."""
        if v < 0:
            raise ValueError(f"{field.name} cannot be negative")
        if abs(v.as_tuple().exponent) > 6:
            raise ValueError(f"{field.name} cannot have more than 6 decimal places")
        return v
    
    @validator('debit', 'credit', pre=True, always=True)
    def validate_debit_credit(cls, v, values, **kwargs):
        """Ensure at least one of debit or credit is provided, but not both."""
        if 'debit' in values and 'credit' in values:
            if values['debit'] > 0 and values['credit'] > 0:
                raise ValueError("Cannot have both debit and credit amounts on the same line")
            if values['debit'] == 0 and values['credit'] == 0:
                raise ValueError("Must provide either a debit or credit amount")
        return v

class JournalEntryLineResponse(JournalEntryLineBase):
    """Schema for journal entry line responses."""
    id: UUID
    journal_entry_id: UUID
    line_number: int
    debit: Decimal
    credit: Decimal
    currency_code: str
    exchange_rate: Decimal
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: UUID
    updated_by: Optional[UUID]
    
    class Config:
        orm_mode = True

class JournalEntryBase(BaseModel):
    """Base schema for journal entries."""
    entry_date: date = Field(..., description="Accounting date")
    reference: Optional[str] = Field(None, max_length=100, description="External reference number")
    memo: Optional[str] = Field(None, description="Entry description or memo")
    company_id: UUID = Field(..., description="Company this entry belongs to")
    is_adjusting: bool = Field(False, description="Is this an adjusting entry?")
    is_reversing: bool = Field(False, description="Is this a reversing entry?")
    currency_code: str = Field("USD", min_length=3, max_length=3, description="Transaction currency")
    exchange_rate: Decimal = Field(Decimal('1.0'), gt=0, description="Exchange rate to base currency")
    
    @validator('exchange_rate')
    def validate_exchange_rate(cls, v):
        """Validate exchange rate precision."""
        if abs(v.as_tuple().exponent) > 6:
            raise ValueError("Exchange rate cannot have more than 6 decimal places")
        return v

class JournalEntryCreate(JournalEntryBase):
    """Schema for creating a journal entry."""
    entry_number: Optional[str] = Field(None, description="Journal entry number (auto-generated if not provided)")
    status: JournalEntryStatus = Field(JournalEntryStatus.DRAFT, description="Entry status")
    lines: List[JournalEntryLineCreate] = Field(..., min_items=2, description="Journal entry lines")
    
    @validator('lines')
    def validate_lines(cls, v):
        """Validate that the entry balances (debits = credits)."""
        total_debit = sum(line.debit for line in v)
        total_credit = sum(line.credit for line in v)
        
        if total_debit != total_credit:
            raise ValueError(f"Journal entry does not balance. Debits: {total_debit}, Credits: {total_credit}")
        
        return v

class JournalEntryUpdate(BaseModel):
    """Schema for updating a journal entry."""
    entry_date: Optional[date] = Field(None, description="Accounting date")
    reference: Optional[str] = Field(None, max_length=100, description="External reference number")
    memo: Optional[str] = Field(None, description="Entry description or memo")
    is_adjusting: Optional[bool] = Field(None, description="Is this an adjusting entry?")
    currency_code: Optional[str] = Field(None, min_length=3, max_length=3, description="Transaction currency")
    exchange_rate: Optional[Decimal] = Field(None, gt=0, description="Exchange rate to base currency")
    status: Optional[JournalEntryStatus] = Field(None, description="Entry status")
    lines: Optional[List[JournalEntryLineCreate]] = Field(None, min_items=2, description="Journal entry lines")
    
    @validator('exchange_rate')
    def validate_exchange_rate(cls, v):
        """Validate exchange rate precision."""
        if v is not None and abs(v.as_tuple().exponent) > 6:
            raise ValueError("Exchange rate cannot have more than 6 decimal places")
        return v
    
    @validator('lines')
    def validate_lines(cls, v, values, **kwargs):
        """Validate that the entry balances (debits = credits)."""
        if v is not None:
            total_debit = sum(line.debit for line in v)
            total_credit = sum(line.credit for line in v)
            
            if total_debit != total_credit:
                raise ValueError(f"Journal entry does not balance. Debits: {total_debit}, Credits: {total_credit}")
        
        return v

class JournalEntryResponse(JournalEntryBase):
    """Schema for journal entry responses."""
    id: UUID
    entry_number: str
    status: JournalEntryStatus
    period_id: Optional[UUID]
    total_debit: Decimal
    total_credit: Decimal
    posting_date: Optional[date]
    reversed_entry_id: Optional[UUID]
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: UUID
    updated_by: Optional[UUID]
    approved_by: Optional[UUID]
    lines: List[JournalEntryLineResponse] = []
    
    class Config:
        orm_mode = True

# Search and filter schemas
class AccountSearch(PaginationParams):
    """Schema for searching accounts."""
    query: Optional[str] = Field(None, description="Search term for account name or code")
    account_type: Optional[AccountType] = Field(None, description="Filter by account type")
    account_subtype: Optional[AccountSubType] = Field(None, description="Filter by account sub-type")
    status: Optional[AccountStatus] = Field(None, description="Filter by account status")
    parent_id: Optional[UUID] = Field(None, description="Filter by parent account ID")
    is_tax_related: Optional[bool] = Field(None, description="Filter by tax-related flag")
    is_reconcilable: Optional[bool] = Field(None, description="Filter by reconcilable flag")
    currency_code: Optional[str] = Field(None, min_length=3, max_length=3, description="Filter by currency code")
    sort_by: str = Field("code", description="Field to sort by")
    sort_order: SortOrder = Field(SortOrder.ASC, description="Sort order")

class JournalEntrySearch(PaginationParams):
    """Schema for searching journal entries."""
    status: Optional[JournalEntryStatus] = Field(None, description="Filter by entry status")
    start_date: Optional[date] = Field(None, description="Filter by start date (inclusive)")
    end_date: Optional[date] = Field(None, description="Filter by end date (inclusive)")
    reference: Optional[str] = Field(None, description="Filter by reference number")
    memo: Optional[str] = Field(None, description="Filter by memo text")
    account_id: Optional[UUID] = Field(None, description="Filter by account ID")
    is_adjusting: Optional[bool] = Field(None, description="Filter by adjusting flag")
    is_reversing: Optional[bool] = Field(None, description="Filter by reversing flag")
    currency_code: Optional[str] = Field(None, min_length=3, max_length=3, description="Filter by currency code")
    created_by: Optional[UUID] = Field(None, description="Filter by creator user ID")
    approved_by: Optional[UUID] = Field(None, description="Filter by approver user ID")
    sort_by: str = Field("entry_date", description="Field to sort by")
    sort_order: SortOrder = Field(SortOrder.DESC, description="Sort order")
    
    @validator('end_date', always=True)
    def validate_dates(cls, v, values):
        """Validate that end_date is not before start_date."""
        if 'start_date' in values and values['start_date'] and v:
            if v < values['start_date']:
                raise ValueError("end_date cannot be before start_date")
        return v

# Accounting Period schemas
class AccountingPeriodBase(BaseModel):
    """Base schema for accounting periods."""
    name: str = Field(..., max_length=100, description="Period name (e.g., 'January 2023')")
    start_date: date = Field(..., description="Period start date (inclusive)")
    end_date: date = Field(..., description="Period end date (inclusive)")
    company_id: UUID = Field(..., description="Company this period belongs to")
    
    @validator('end_date')
    def validate_dates(cls, v, values):
        """Validate that end_date is after start_date."""
        if 'start_date' in values and values['start_date'] and v < values['start_date']:
            raise ValueError("end_date cannot be before start_date")
        return v

class AccountingPeriodCreate(AccountingPeriodBase):
    """Schema for creating an accounting period."""
    pass

class AccountingPeriodUpdate(BaseModel):
    """Schema for updating an accounting period."""
    name: Optional[str] = Field(None, max_length=100, description="Period name")
    is_closed: Optional[bool] = Field(None, description="Whether the period is closed")

class AccountingPeriodResponse(AccountingPeriodBase):
    """Schema for accounting period responses."""
    id: UUID
    is_closed: bool
    close_date: Optional[datetime]
    closed_by_id: Optional[UUID]
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: UUID
    updated_by: Optional[UUID]
    
    class Config:
        orm_mode = True

# Trial Balance schemas
class TrialBalanceAccountResponse(BaseModel):
    """Schema for trial balance account responses."""
    account_id: UUID
    account_code: str
    account_name: str
    account_type: AccountType
    debit_balance: Decimal
    credit_balance: Decimal
    net_balance: Decimal
    
    class Config:
        orm_mode = True

class TrialBalanceResponse(BaseModel):
    """Schema for trial balance responses."""
    id: UUID
    name: str
    as_of_date: date
    is_posted: bool
    posted_at: Optional[datetime]
    posted_by: Optional[UUID]
    company_id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    accounts: List[TrialBalanceAccountResponse] = []
    
    class Config:
        orm_mode = True

# Financial Statement schemas
class FinancialStatementType(str, Enum):
    """Types of financial statements."""
    BALANCE_SHEET = "balance_sheet"
    INCOME_STATEMENT = "income_statement"
    CASH_FLOW = "cash_flow"
    RETAINED_EARNINGS = "retained_earnings"
    CHANGES_IN_EQUITY = "changes_in_equity"

class FinancialStatementResponse(BaseModel):
    """Schema for financial statement responses."""
    id: UUID
    name: str
    statement_type: FinancialStatementType
    start_date: Optional[date]
    end_date: date
    is_final: bool
    generated_at: datetime
    generated_by: UUID
    company_id: UUID
    statement_data: Dict[str, Any]
    
    class Config:
        orm_mode = True

# Update forward references for recursive models
AccountTreeResponse.update_forward_refs()
AccountBalanceResponse.update_forward_refs()
