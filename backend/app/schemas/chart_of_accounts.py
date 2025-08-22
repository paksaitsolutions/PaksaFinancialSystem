from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from uuid import UUID

class ChartOfAccountsBase(BaseModel):
    """Base schema for Chart of Accounts."""
    code: str = Field(..., max_length=50, description="Account code (e.g., '1010')")
    name: str = Field(..., max_length=255, description="Account name")
    description: Optional[str] = Field(None, description="Account description")
    category: str = Field(..., description="Account category (Asset, Liability, Equity, Revenue, Expense)")
    account_type: str = Field(..., description="Type of account (e.g., 'Current Asset', 'Expense')")
    parent_code: Optional[str] = Field(None, description="Parent account code")
    is_active: bool = Field(True, description="Whether the account is active")
    is_contra: bool = Field(False, description="Whether this is a contra-account")
    currency_code: str = Field("USD", max_length=3, description="ISO 4217 currency code")
    
    @validator('category')
    def validate_category(cls, v):
        valid_categories = {'Asset', 'Liability', 'Equity', 'Revenue', 'Expense'}
        if v not in valid_categories:
            raise ValueError(f"Category must be one of {valid_categories}")
        return v
    
    @validator('currency_code')
    def currency_code_uppercase(cls, v):
        return v.upper()

class ChartOfAccountsCreate(ChartOfAccountsBase):
    """Schema for creating a new Chart of Accounts entry."""
    pass

class ChartOfAccountsUpdate(BaseModel):
    """Schema for updating a Chart of Accounts entry."""
    name: Optional[str] = Field(None, max_length=255, description="Account name")
    description: Optional[str] = Field(None, description="Account description")
    is_active: Optional[bool] = Field(None, description="Whether the account is active")
    is_contra: Optional[bool] = Field(None, description="Whether this is a contra-account")
    currency_code: Optional[str] = Field(None, max_length=3, description="ISO 4217 currency code")
    
    @validator('currency_code')
    def currency_code_uppercase(cls, v):
        if v is not None:
            return v.upper()
        return v

class ChartOfAccountsInDBBase(ChartOfAccountsBase):
    """Base schema for Chart of Accounts in the database."""
    id: UUID
    level: int = Field(..., description="Hierarchy level (0 for root accounts)")
    full_code: str = Field(..., description="Full hierarchical account code")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class ChartOfAccounts(ChartOfAccountsInDBBase):
    """Schema for returning Chart of Accounts data."""
    pass

class ChartOfAccountsWithBalance(ChartOfAccountsInDBBase):
    """Schema for returning Chart of Accounts data with balance information."""
    balance: float = Field(..., description="Current account balance")
    balance_debit: float = Field(..., description="Total debits")
    balance_credit: float = Field(..., description="Total credits")
    
    class Config:
        orm_mode = True

class ChartOfAccountsTree(ChartOfAccountsWithBalance):
    """Schema for hierarchical Chart of Accounts with nested children."""
    children: List['ChartOfAccountsTree'] = Field(default_factory=list)

# Update forward reference for nested model
ChartOfAccountsTree.update_forward_refs()

class ChartOfAccountsBulkCreate(BaseModel):
    """Schema for bulk creating Chart of Accounts entries."""
    accounts: List[ChartOfAccountsCreate] = Field(..., description="List of accounts to create")
