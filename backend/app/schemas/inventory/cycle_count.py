"""
Schemas for cycle count API endpoints.
"""
from typing import List, Optional
from uuid import UUID
from datetime import date
from decimal import Decimal
from pydantic import BaseModel, Field

from app.models.enums import CycleCountStatus

class CycleCountLineItemBase(BaseModel):
    """Base schema for cycle count line item."""
    item_id: UUID
    system_quantity: Decimal
    counted_quantity: Optional[Decimal] = None
    notes: Optional[str] = None

class CycleCountLineItemCreate(CycleCountLineItemBase):
    """Schema for creating a cycle count line item."""
    pass

class CycleCountLineItemUpdate(BaseModel):
    """Schema for updating a cycle count line item."""
    counted_quantity: Decimal
    notes: Optional[str] = None

class CycleCountLineItemResponse(CycleCountLineItemBase):
    """Schema for cycle count line item response."""
    id: UUID
    variance: Decimal
    is_counted: bool
    item_sku: Optional[str] = None
    item_name: Optional[str] = None

    class Config:
        orm_mode = True

class CycleCountBase(BaseModel):
    """Base schema for cycle count."""
    location_id: UUID
    count_date: date = Field(default_factory=date.today)
    counted_by: Optional[str] = None
    notes: Optional[str] = None

class CycleCountCreate(CycleCountBase):
    """Schema for creating a cycle count."""
    line_items: List[CycleCountLineItemCreate]

class CycleCountUpdate(BaseModel):
    """Schema for updating a cycle count."""
    status: Optional[CycleCountStatus] = None
    counted_by: Optional[str] = None
    notes: Optional[str] = None

class CycleCountResponse(CycleCountBase):
    """Schema for cycle count response."""
    id: UUID
    count_number: str
    status: CycleCountStatus
    line_items: List[CycleCountLineItemResponse] = []

    class Config:
        orm_mode = True