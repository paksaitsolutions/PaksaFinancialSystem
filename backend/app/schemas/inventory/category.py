"""
Schemas for inventory category API endpoints.
"""
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel

class InventoryCategoryBase(BaseModel):
    """Base schema for inventory category."""
    code: str
    name: str
    description: Optional[str] = None
    parent_id: Optional[UUID] = None

class InventoryCategoryCreate(InventoryCategoryBase):
    """Schema for creating an inventory category."""
    pass

class InventoryCategoryUpdate(BaseModel):
    """Schema for updating an inventory category."""
    code: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[UUID] = None

class InventoryCategoryResponse(InventoryCategoryBase):
    """Schema for inventory category response."""
    id: UUID
    item_count: Optional[int] = 0

    class Config:
        orm_mode = True