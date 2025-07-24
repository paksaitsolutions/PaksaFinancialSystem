"""
Schemas for inventory adjustment API endpoints.
"""
from typing import Optional
from uuid import UUID
from datetime import date
from decimal import Decimal
from pydantic import BaseModel, Field

class InventoryAdjustmentBase(BaseModel):
    """Base schema for inventory adjustment."""
    item_id: UUID
    location_id: UUID
    adjustment_date: date = Field(default_factory=date.today)
    quantity_adjustment: Decimal
    reason: str
    reference: Optional[str] = None
    notes: Optional[str] = None

class InventoryAdjustmentCreate(InventoryAdjustmentBase):
    """Schema for creating an inventory adjustment."""
    pass

class InventoryAdjustmentResponse(InventoryAdjustmentBase):
    """Schema for inventory adjustment response."""
    id: UUID
    quantity_before: Decimal
    quantity_after: Decimal
    unit_cost: Decimal
    total_cost_impact: Decimal

    class Config:
        orm_mode = True