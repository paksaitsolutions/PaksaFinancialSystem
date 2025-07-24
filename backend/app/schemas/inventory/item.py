"""
Schemas for inventory item API endpoints.
"""
from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel

from app.models.enums import InventoryStatus, ValuationMethod

class InventoryItemBase(BaseModel):
    """Base schema for inventory item."""
    sku: str
    barcode: Optional[str] = None
    name: str
    description: Optional[str] = None
    category_id: Optional[UUID] = None
    status: InventoryStatus = InventoryStatus.ACTIVE
    is_tracked: bool = True
    reorder_point: Decimal = 0
    reorder_quantity: Decimal = 0
    valuation_method: ValuationMethod = ValuationMethod.AVERAGE
    unit_cost: Decimal = 0
    standard_cost: Decimal = 0
    unit_of_measure: str = "EA"
    weight: Optional[Decimal] = None
    dimensions: Optional[str] = None
    default_location_id: Optional[UUID] = None

class InventoryItemCreate(InventoryItemBase):
    """Schema for creating an inventory item."""
    pass

class InventoryItemUpdate(BaseModel):
    """Schema for updating an inventory item."""
    sku: Optional[str] = None
    barcode: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[UUID] = None
    status: Optional[InventoryStatus] = None
    is_tracked: Optional[bool] = None
    reorder_point: Optional[Decimal] = None
    reorder_quantity: Optional[Decimal] = None
    valuation_method: Optional[ValuationMethod] = None
    unit_cost: Optional[Decimal] = None
    standard_cost: Optional[Decimal] = None
    unit_of_measure: Optional[str] = None
    weight: Optional[Decimal] = None
    dimensions: Optional[str] = None
    default_location_id: Optional[UUID] = None

class InventoryItemResponse(InventoryItemBase):
    """Schema for inventory item response."""
    id: UUID
    quantity_on_hand: Decimal
    quantity_available: Decimal
    quantity_committed: Decimal

    class Config:
        orm_mode = True