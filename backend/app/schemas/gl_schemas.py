"""
Pydantic schemas for the General Ledger module.
"""
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, validator, condecimal

# Define enums instead of importing SQLAlchemy models
class AccountTypeEnum(str, Enum):
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    REVENUE = "revenue"
    EXPENSE = "expense"

class AccountSubTypeEnum(str, Enum):
    CURRENT_ASSET = "current_asset"
    FIXED_ASSET = "fixed_asset"
    CURRENT_LIABILITY = "current_liability"
    LONG_TERM_LIABILITY = "long_term_liability"

class AccountStatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    CLOSED = "closed"

class JournalEntryStatusEnum(str, Enum):
    DRAFT = "draft"
    POSTED = "posted"
    REVERSED = "reversed"

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
    account_type: AccountTypeEnum = Field(..., description="Type of account")
    account_subtype: Optional[AccountSubTypeEnum] = Field(None, description="Account sub-type")
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
    account_type: Optional[AccountTypeEnum] = Field(None, description="Type of account")
    account_subtype: Optional[AccountSubTypeEnum] = Field(None, description="Account sub-type")
    parent_id: Optional[UUID] = Field(None, description="Parent account ID")
    is_tax_related: Optional[bool] = Field(None, description="Whether this account is related to taxes")
    is_reconcilable: Optional[bool] = Field(None, description="Whether this account can be reconciled")
    currency_code: Optional[str] = Field(None, min_length=3, max_length=3, description="ISO 4217 currency code")
    status: Optional[AccountStatusEnum] = Field(None, description="Account status")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class AccountResponse(AccountBase):
    """Schema for account responses."""
    id: UUID
    status: AccountStatusEnum
    is_system_account: bool
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: UUID
    updated_by: Optional[UUID]
    
    model_config = {"from_attributes": True}

class AccountTreeResponse(AccountResponse):
    """Schema for account hierarchy responses."""
    children: List['AccountTreeResponse'] = []
    
    model_config = {"from_attributes": True}

class AccountBalanceResponse(BaseModel):
    """Schema for account balance responses."""
    account_id: UUID
    account_code: str
    account_name: str
    account_type: AccountTypeEnum
    currency_code: str
    balance: Decimal
    total_debit: Decimal
    total_credit: Decimal
    as_of_date: date
    children: Optional[List['AccountBalanceResponse']] = None
    
    model_config = {"from_attributes": True}

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
    
    model_config = {"from_attributes": True}

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

class JournalEntryCreate(JournalEntryBase):
    """Schema for creating a journal entry."""
    entry_number: Optional[str] = Field(None, description="Journal entry number (auto-generated if not provided)")
    status: JournalEntryStatusEnum = Field(JournalEntryStatusEnum.DRAFT, description="Entry status")
    lines: List[JournalEntryLineCreate] = Field(..., min_items=2, description="Journal entry lines")

class JournalEntryUpdate(BaseModel):
    """Schema for updating a journal entry."""
    entry_date: Optional[date] = Field(None, description="Accounting date")
    reference: Optional[str] = Field(None, max_length=100, description="External reference number")
    memo: Optional[str] = Field(None, description="Entry description or memo")
    is_adjusting: Optional[bool] = Field(None, description="Is this an adjusting entry?")
    currency_code: Optional[str] = Field(None, min_length=3, max_length=3, description="Transaction currency")
    exchange_rate: Optional[Decimal] = Field(None, gt=0, description="Exchange rate to base currency")
    status: Optional[JournalEntryStatusEnum] = Field(None, description="Entry status")
    lines: Optional[List[JournalEntryLineCreate]] = Field(None, min_items=2, description="Journal entry lines")

class JournalEntryResponse(JournalEntryBase):
    """Schema for journal entry responses."""
    id: UUID
    entry_number: str
    status: JournalEntryStatusEnum
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
    
    model_config = {"from_attributes": True}

# Search and filter schemas
class AccountSearch(PaginationParams):
    """Schema for searching accounts."""
    query: Optional[str] = Field(None, description="Search term for account name or code")
    account_type: Optional[AccountTypeEnum] = Field(None, description="Filter by account type")
    account_subtype: Optional[AccountSubTypeEnum] = Field(None, description="Filter by account sub-type")
    status: Optional[AccountStatusEnum] = Field(None, description="Filter by account status")
    parent_id: Optional[UUID] = Field(None, description="Filter by parent account ID")
    is_tax_related: Optional[bool] = Field(None, description="Filter by tax-related flag")
    is_reconcilable: Optional[bool] = Field(None, description="Filter by reconcilable flag")
    currency_code: Optional[str] = Field(None, min_length=3, max_length=3, description="Filter by currency code")
    sort_by: str = Field("code", description="Field to sort by")
    sort_order: SortOrder = Field(SortOrder.ASC, description="Sort order")

class JournalEntrySearch(PaginationParams):
    """Schema for searching journal entries."""
    status: Optional[JournalEntryStatusEnum] = Field(None, description="Filter by entry status")
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

# Financial Statement schemas
class FinancialStatementType(str, Enum):
    """Types of financial statements."""
    BALANCE_SHEET = "balance_sheet"
    INCOME_STATEMENT = "income_statement"
    CASH_FLOW = "cash_flow"
    RETAINED_EARNINGS = "retained_earnings"
    CHANGES_IN_EQUITY = "changes_in_equity"

class FinancialStatementCreate(BaseModel):
    """Schema for creating a financial statement."""
    name: str = Field(..., description="Statement name")
    statement_type: FinancialStatementType = Field(..., description="Type of statement")
    start_date: Optional[date] = Field(None, description="Start date for period statements")
    end_date: date = Field(..., description="End date")
    company_id: UUID = Field(..., description="Company ID")

class FinancialStatementLineCreate(BaseModel):
    """Schema for creating a financial statement line."""
    account_id: Optional[UUID] = Field(None, description="Account ID")
    description: str = Field(..., description="Line description")
    amount: Decimal = Field(Decimal('0'), description="Line amount")
    line_number: Optional[int] = Field(None, description="Line number")
    is_total: bool = Field(False, description="Is this a total line")
    parent_line_id: Optional[UUID] = Field(None, description="Parent line ID")

class FinancialStatementSectionCreate(BaseModel):
    """Schema for creating a financial statement section."""
    section_name: str = Field(..., description="Section name")
    section_order: int = Field(0, description="Section order")
    is_total_section: bool = Field(False, description="Is this a total section")

class FinancialStatementUpdate(BaseModel):
    """Schema for updating a financial statement."""
    name: Optional[str] = Field(None, description="Statement name")
    is_final: Optional[bool] = Field(None, description="Is statement final")

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
    
    model_config = {"from_attributes": True}

# Trial Balance schemas
class TrialBalanceEntry(BaseModel):
    """Schema for trial balance entry."""
    account_code: str = Field(..., description="Account code")
    account_name: str = Field(..., description="Account name")
    account_type: str = Field(..., description="Account type")
    opening_balance: Decimal = Field(Decimal('0'), description="Opening balance")
    period_activity: Decimal = Field(Decimal('0'), description="Period activity")
    ending_balance: Decimal = Field(Decimal('0'), description="Ending balance")
    debit_amount: Decimal = Field(Decimal('0'), description="Debit amount")
    credit_amount: Decimal = Field(Decimal('0'), description="Credit amount")
    
    model_config = {"from_attributes": True}

class TrialBalance(BaseModel):
    """Schema for trial balance."""
    start_date: date = Field(..., description="Start date")
    end_date: date = Field(..., description="End date")
    entries: List[TrialBalanceEntry] = Field([], description="Trial balance entries")
    total_debit: Decimal = Field(Decimal('0'), description="Total debit amount")
    total_credit: Decimal = Field(Decimal('0'), description="Total credit amount")
    difference: Decimal = Field(Decimal('0'), description="Difference between debits and credits")
    
    model_config = {"from_attributes": True}

# Update forward references for recursive models
AccountTreeResponse.model_rebuild()
AccountBalanceResponse.model_rebuild()