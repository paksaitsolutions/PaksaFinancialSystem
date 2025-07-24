"""
Schemas for inventory location API endpoints.
"""
from typing import Optional
from uuid import UUID
from pydantic import BaseModel

class InventoryLocationBase(BaseModel):
    """Base schema for inventory location."""
    code: str
    name: str
    description: Optional[str] = None
    is_active: bool = True
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None

class InventoryLocationCreate(InventoryLocationBase):
    """Schema for creating an inventory location."""
    pass

class InventoryLocationUpdate(BaseModel):
    """Schema for updating an inventory location."""
    code: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None

class InventoryLocationResponse(InventoryLocationBase):
    """Schema for inventory location response."""
    id: UUID
    item_count: Optional[int] = 0

    class Config:
        orm_mode = True