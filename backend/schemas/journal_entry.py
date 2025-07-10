from datetime import date, datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, validator, condecimal

class JournalEntryStatus(str, Enum):
    """Status of a journal entry."""
    DRAFT = "draft"
    POSTED = "posted"
    VOID = "void"

class JournalEntryItemBase(BaseModel):
    """Base schema for a journal entry line item."""
    account_code: str = Field(..., description="Account code for this line item")
    description: Optional[str] = Field(None, description="Description of the line item")
    amount: float = Field(..., gt=0, description="Amount for this line item (always positive)")
    side: str = Field(..., description="'debit' or 'credit'", regex="^(debit|credit)$")
    
    # Foreign currency information (optional)
    foreign_currency_code: Optional[str] = Field(
        None, 
        max_length=3, 
        description="ISO 4217 currency code for foreign currency"
    )
    foreign_amount: Optional[float] = Field(
        None, 
        gt=0, 
        description="Amount in foreign currency"
    )
    exchange_rate: Optional[float] = Field(
        None, 
        gt=0, 
        description="Exchange rate used (1 unit of foreign currency = X units of account currency)"
    )
    
    @validator('foreign_currency_code')
    def currency_code_uppercase(cls, v):
        if v is not None:
            return v.upper()
        return v
    
    @validator('foreign_amount', 'exchange_rate')
    def validate_foreign_fields(cls, v, values, **kwargs):
        # If any foreign currency field is provided, all must be provided
        if any(field in values for field in ['foreign_currency_code', 'foreign_amount', 'exchange_rate']):
            if not all(field in values for field in ['foreign_currency_code', 'foreign_amount', 'exchange_rate']):
                raise ValueError("All foreign currency fields must be provided together")
        return v

class JournalEntryItemCreate(JournalEntryItemBase):
    """Schema for creating a new journal entry line item."""
    pass

class JournalEntryItemUpdate(BaseModel):
    """Schema for updating a journal entry line item."""
    description: Optional[str] = Field(None, description="Description of the line item")
    amount: Optional[float] = Field(None, gt=0, description="Amount for this line item (always positive)")
    side: Optional[str] = Field(None, description="'debit' or 'credit'", regex="^(debit|credit)$")
    foreign_currency_code: Optional[str] = Field(None, max_length=3)
    foreign_amount: Optional[float] = Field(None, gt=0)
    exchange_rate: Optional[float] = Field(None, gt=0)
    
    @validator('foreign_currency_code')
    def currency_code_uppercase(cls, v):
        if v is not None:
            return v.upper()
        return v

class JournalEntryItem(JournalEntryItemBase):
    """Schema for returning a journal entry line item."""
    id: UUID
    journal_entry_id: UUID
    account_code: str
    account_name: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class JournalEntryBase(BaseModel):
    """Base schema for a journal entry."""
    date_posted: date = Field(default_factory=date.today, description="Accounting date")
    reference: Optional[str] = Field(
        None, 
        max_length=100, 
        description="External reference number or identifier"
    )
    memo: Optional[str] = Field(
        None, 
        description="Description or notes about the journal entry"
    )
    is_adjusting: bool = Field(
        False, 
        description="Whether this is an adjusting entry"
    )
    is_recurring: bool = Field(
        False, 
        description="Whether this is a recurring entry"
    )
    recurring_frequency: Optional[str] = Field(
        None, 
        description="Frequency of recurrence (e.g., 'monthly', 'quarterly')"
    )
    recurring_end_date: Optional[date] = Field(
        None, 
        description="End date for recurring entries"
    )
    
    @validator('recurring_frequency')
    def validate_recurring_frequency(cls, v, values):
        if values.get('is_recurring') and not v:
            raise ValueError("Recurring frequency is required for recurring entries")
        if v and v.lower() not in ['daily', 'weekly', 'monthly', 'quarterly', 'yearly']:
            raise ValueError("Invalid recurring frequency")
        return v.lower() if v else v
    
    @validator('recurring_end_date')
    def validate_recurring_end_date(cls, v, values):
        if values.get('is_recurring') and not v:
            raise ValueError("Recurring end date is required for recurring entries")
        return v

class JournalEntryCreate(JournalEntryBase):
    """Schema for creating a new journal entry."""
    items: List[JournalEntryItemCreate] = Field(
        ..., 
        min_items=2, 
        description="List of journal entry line items (at least 2 required)"
    )
    
    @validator('items')
    def validate_items_balance(cls, v):
        total_debits = sum(item.amount for item in v if item.side == 'debit')
        total_credits = sum(item.amount for item in v if item.side == 'credit')
        
        if abs(total_debits - total_credits) > 0.01:  # Allow for floating point rounding
            raise ValueError("Total debits must equal total credits")
        
        return v

class JournalEntryUpdate(JournalEntryBase):
    """Schema for updating a journal entry."""
    date_posted: Optional[date] = None
    reference: Optional[str] = None
    memo: Optional[str] = None
    is_adjusting: Optional[bool] = None
    is_recurring: Optional[bool] = None
    recurring_frequency: Optional[str] = None
    recurring_end_date: Optional[date] = None
    items: Optional[List[JournalEntryItemCreate]] = Field(
        None, 
        min_items=2, 
        description="Complete list of line items (replaces all existing items)"
    )
    
    @validator('items')
    def validate_items_balance(cls, v):
        if v is not None:
            total_debits = sum(item.amount for item in v if item.side == 'debit')
            total_credits = sum(item.amount for item in v if item.side == 'credit')
            
            if abs(total_debits - total_credits) > 0.01:  # Allow for floating point rounding
                raise ValueError("Total debits must equal total credits")
        
        return v

class JournalEntryInDBBase(JournalEntryBase):
    """Base schema for a journal entry in the database."""
    id: UUID
    entry_number: str
    status: JournalEntryStatus
    created_at: datetime
    updated_at: datetime
    created_by_id: Optional[UUID]
    posted_by_id: Optional[UUID]
    
    class Config:
        orm_mode = True

class JournalEntry(JournalEntryInDBBase):
    """Schema for returning a journal entry."""
    items: List[JournalEntryItem] = Field(default_factory=list)
    created_by_name: Optional[str] = None
    posted_by_name: Optional[str] = None

class JournalEntryWithBalance(JournalEntry):
    """Schema for returning a journal entry with running balances."""
    running_balance: Optional[float] = None

class JournalEntryFilter(BaseModel):
    """Schema for filtering journal entries."""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[JournalEntryStatus] = None
    account_code: Optional[str] = None
    reference: Optional[str] = None
    is_adjusting: Optional[bool] = None
    is_recurring: Optional[bool] = None
    created_by_id: Optional[UUID] = None
    
    class Config:
        use_enum_values = True

class JournalEntryBulkCreate(BaseModel):
    """Schema for bulk creating journal entries."""
    entries: List[JournalEntryCreate] = Field(..., description="List of journal entries to create")
