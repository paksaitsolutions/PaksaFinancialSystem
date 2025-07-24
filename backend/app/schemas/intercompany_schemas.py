"""
Schemas for intercompany transaction operations.
"""
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator


class IntercompanyTransactionType(str, Enum):
    SALE = "sale"
    PURCHASE = "purchase"
    LOAN = "loan"
    EXPENSE_ALLOCATION = "expense_allocation"
    REVENUE_SHARING = "revenue_sharing"
    TRANSFER = "transfer"


class IntercompanyTransactionStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    POSTED = "posted"
    RECONCILED = "reconciled"
    CANCELLED = "cancelled"


class IntercompanyTransactionBase(BaseModel):
    """Base schema for intercompany transaction operations."""
    transaction_type: IntercompanyTransactionType = Field(..., description="Type of intercompany transaction")
    source_company_id: UUID = Field(..., description="Source company ID")
    target_company_id: UUID = Field(..., description="Target company ID")
    amount: Decimal = Field(..., description="Transaction amount")
    currency_id: UUID = Field(..., description="Currency ID")
    transaction_date: date = Field(..., description="Transaction date")
    due_date: Optional[date] = Field(None, description="Due date")
    source_account_id: UUID = Field(..., description="Source account ID")
    target_account_id: UUID = Field(..., description="Target account ID")
    description: Optional[str] = Field(None, description="Transaction description")
    reference_number: Optional[str] = Field(None, description="Reference number")

    @validator('amount')
    def validate_amount(cls, v):
        """Validate transaction amount."""
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v

    @validator('source_company_id', 'target_company_id')
    def validate_companies(cls, v, values):
        """Validate that source and target companies are different."""
        if 'source_company_id' in values and v == values['source_company_id']:
            raise ValueError("Source and target companies must be different")
        return v


class IntercompanyTransactionCreate(IntercompanyTransactionBase):
    """Schema for creating a new intercompany transaction."""
    pass


class IntercompanyTransactionUpdate(BaseModel):
    """Schema for updating an existing intercompany transaction."""
    transaction_type: Optional[IntercompanyTransactionType] = None
    amount: Optional[Decimal] = None
    currency_id: Optional[UUID] = None
    transaction_date: Optional[date] = None
    due_date: Optional[date] = None
    source_account_id: Optional[UUID] = None
    target_account_id: Optional[UUID] = None
    description: Optional[str] = None
    reference_number: Optional[str] = None

    @validator('amount')
    def validate_amount(cls, v):
        """Validate transaction amount."""
        if v is not None and v <= 0:
            raise ValueError("Amount must be positive")
        return v


class IntercompanyTransactionResponse(BaseModel):
    """Schema for intercompany transaction response."""
    id: UUID = Field(..., description="Transaction ID")
    transaction_number: str = Field(..., description="Transaction number")
    transaction_type: IntercompanyTransactionType = Field(..., description="Transaction type")
    status: IntercompanyTransactionStatus = Field(..., description="Transaction status")
    source_company_id: UUID = Field(..., description="Source company ID")
    target_company_id: UUID = Field(..., description="Target company ID")
    amount: Decimal = Field(..., description="Transaction amount")
    currency_id: UUID = Field(..., description="Currency ID")
    transaction_date: date = Field(..., description="Transaction date")
    due_date: Optional[date] = Field(None, description="Due date")
    source_account_id: UUID = Field(..., description="Source account ID")
    target_account_id: UUID = Field(..., description="Target account ID")
    description: Optional[str] = Field(None, description="Transaction description")
    reference_number: Optional[str] = Field(None, description="Reference number")
    source_journal_entry_id: Optional[UUID] = Field(None, description="Source journal entry ID")
    target_journal_entry_id: Optional[UUID] = Field(None, description="Target journal entry ID")
    approved_by: Optional[UUID] = Field(None, description="Approved by user ID")
    approved_at: Optional[datetime] = Field(None, description="Approval timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        orm_mode = True


class IntercompanyReconciliationResponse(BaseModel):
    """Schema for intercompany reconciliation response."""
    id: UUID = Field(..., description="Reconciliation ID")
    reconciliation_number: str = Field(..., description="Reconciliation number")
    reconciliation_date: date = Field(..., description="Reconciliation date")
    company_a_id: UUID = Field(..., description="Company A ID")
    company_b_id: UUID = Field(..., description="Company B ID")
    period_start: date = Field(..., description="Period start date")
    period_end: date = Field(..., description="Period end date")
    status: str = Field(..., description="Reconciliation status")
    company_a_balance: Decimal = Field(..., description="Company A balance")
    company_b_balance: Decimal = Field(..., description="Company B balance")
    difference: Decimal = Field(..., description="Balance difference")
    notes: Optional[str] = Field(None, description="Reconciliation notes")
    reconciled_by: Optional[UUID] = Field(None, description="Reconciled by user ID")
    reconciled_at: Optional[datetime] = Field(None, description="Reconciliation timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        orm_mode = True