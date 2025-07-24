"""
Schemas for credit memo API endpoints.
"""
from typing import List, Optional
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field, validator

from app.models.enums import CreditMemoStatus

class CreditApplicationBase(BaseModel):
    """Base schema for credit application."""
    invoice_id: UUID
    amount: Decimal = Field(gt=0)
    notes: Optional[str] = None

class CreditApplicationCreate(CreditApplicationBase):
    """Schema for creating a credit application."""
    pass

class CreditApplicationResponse(CreditApplicationBase):
    """Schema for credit application response."""
    id: UUID
    credit_memo_id: UUID
    application_date: date
    invoice_number: str
    invoice_total: Decimal

    class Config:
        orm_mode = True

class CreditMemoBase(BaseModel):
    """Base schema for credit memo."""
    vendor_id: UUID
    credit_date: date
    amount: Decimal = Field(gt=0)
    description: Optional[str] = None
    reference: Optional[str] = None
    original_invoice_id: Optional[UUID] = None

class CreditMemoCreate(CreditMemoBase):
    """Schema for creating a credit memo."""
    pass

class CreditMemoUpdate(BaseModel):
    """Schema for updating a credit memo."""
    credit_date: Optional[date] = None
    description: Optional[str] = None
    reference: Optional[str] = None

class CreditMemoResponse(CreditMemoBase):
    """Schema for credit memo response."""
    id: UUID
    credit_memo_number: str
    status: CreditMemoStatus
    applied_amount: Decimal
    remaining_amount: Decimal
    created_at: datetime
    updated_at: datetime
    applications: List[CreditApplicationResponse] = []

    class Config:
        orm_mode = True

class CreditMemoListResponse(BaseModel):
    """Schema for credit memo list response."""
    items: List[CreditMemoResponse]
    total: int
    page: int
    page_size: int
    pages: int

class CreditMemoApplicationRequest(BaseModel):
    """Schema for applying credit to invoices."""
    applications: List[CreditApplicationCreate]
    
    @validator('applications')
    def validate_applications(cls, v):
        """Validate that there is at least one application."""
        if not v:
            raise ValueError("At least one application is required")
        return v

class CreditMemoVoidRequest(BaseModel):
    """Schema for voiding a credit memo."""
    reason: str