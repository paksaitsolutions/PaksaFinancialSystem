from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

# Base schemas
class InventoryItemBase(BaseModel):
    item_code: str = Field(..., max_length=50)
    item_name: str = Field(..., max_length=255)
    description: Optional[str] = None
    category_id: Optional[str] = None
    unit_of_measure: Optional[str] = Field(None, max_length=20)
    cost_price: Optional[Decimal] = None
    selling_price: Optional[Decimal] = None
    reorder_level: Optional[int] = 0
    maximum_level: Optional[int] = None
    is_active: bool = True
    barcode: Optional[str] = None

class InventoryItemCreate(InventoryItemBase):
    pass

class InventoryItemUpdate(BaseModel):
    item_name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[str] = None
    unit_of_measure: Optional[str] = None
    cost_price: Optional[Decimal] = None
    selling_price: Optional[Decimal] = None
    reorder_level: Optional[int] = None
    maximum_level: Optional[int] = None
    is_active: Optional[bool] = None
    barcode: Optional[str] = None

class InventoryItemResponse(InventoryItemBase):
    id: str
    company_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Category schemas
class InventoryCategoryBase(BaseModel):
    code: str = Field(..., max_length=20)
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    parent_id: Optional[str] = None
    is_active: bool = True

class InventoryCategoryCreate(InventoryCategoryBase):
    pass

class InventoryCategoryResponse(InventoryCategoryBase):
    id: str
    company_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Location schemas
class InventoryLocationBase(BaseModel):
    location_code: str = Field(..., max_length=20)
    location_name: str = Field(..., max_length=255)
    address: Optional[str] = None
    location_type: Optional[str] = None
    is_active: bool = True

class InventoryLocationCreate(InventoryLocationBase):
    pass

class InventoryLocationResponse(InventoryLocationBase):
    id: str
    company_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Transaction schemas
class InventoryTransactionBase(BaseModel):
    item_id: str
    location_id: str
    transaction_type: str = Field(..., pattern="^(in|out|adjustment)$")
    quantity: int
    unit_cost: Optional[Decimal] = None
    total_value: Optional[Decimal] = None
    reference: Optional[str] = None
    notes: Optional[str] = None
    transaction_date: Optional[datetime] = None

class InventoryTransactionCreate(InventoryTransactionBase):
    pass

class InventoryTransactionResponse(InventoryTransactionBase):
    id: str
    company_id: str
    created_by: Optional[str] = None
    
    class Config:
        from_attributes = True

# Adjustment schemas
class InventoryAdjustmentBase(BaseModel):
    adjustment_number: str = Field(..., max_length=50)
    adjustment_date: datetime
    reason: Optional[str] = None
    total_adjustment_value: Optional[Decimal] = 0
    status: str = "draft"

class InventoryAdjustmentCreate(InventoryAdjustmentBase):
    pass

class InventoryAdjustmentResponse(InventoryAdjustmentBase):
    id: str
    company_id: str
    created_by: Optional[str] = None
    approved_by: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True