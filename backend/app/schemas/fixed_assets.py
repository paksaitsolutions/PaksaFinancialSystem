from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date
from decimal import Decimal

# Base schemas
class FixedAssetBase(BaseModel):
    asset_number: str = Field(..., max_length=50)
    asset_name: str = Field(..., max_length=255)
    asset_category: Optional[str] = Field(None, max_length=100)
    purchase_date: date
    purchase_cost: Decimal = Field(..., gt=0)
    salvage_value: Optional[Decimal] = Field(None, ge=0)
    useful_life_years: Optional[int] = Field(None, gt=0)
    depreciation_method: Optional[str] = Field(None, max_length=50)
    location: Optional[str] = Field(None, max_length=255)
    status: str = Field(default="active", max_length=20)

class FixedAssetCreate(FixedAssetBase):
    accumulated_depreciation: Optional[Decimal] = Field(default=0, ge=0)

class FixedAssetUpdate(BaseModel):
    asset_name: Optional[str] = None
    asset_category: Optional[str] = None
    purchase_cost: Optional[Decimal] = None
    salvage_value: Optional[Decimal] = None
    useful_life_years: Optional[int] = None
    depreciation_method: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None
    accumulated_depreciation: Optional[Decimal] = None

class FixedAssetResponse(FixedAssetBase):
    id: str
    company_id: str
    accumulated_depreciation: Optional[Decimal] = None
    current_value: Optional[Decimal] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Depreciation schemas
class AssetDepreciationBase(BaseModel):
    depreciation_date: date
    depreciation_amount: Decimal = Field(..., gt=0)
    accumulated_depreciation: Decimal = Field(..., ge=0)
    book_value: Decimal = Field(..., ge=0)
    notes: Optional[str] = None

class AssetDepreciationCreate(AssetDepreciationBase):
    pass

class AssetDepreciationResponse(AssetDepreciationBase):
    id: str
    asset_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Maintenance schemas
class AssetMaintenanceBase(BaseModel):
    asset_id: str
    maintenance_date: date
    maintenance_type: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    cost: Optional[Decimal] = Field(None, ge=0)
    vendor: Optional[str] = Field(None, max_length=255)
    next_maintenance_date: Optional[date] = None

class AssetMaintenanceCreate(AssetMaintenanceBase):
    pass

class AssetMaintenanceUpdate(BaseModel):
    maintenance_date: Optional[date] = None
    maintenance_type: Optional[str] = None
    description: Optional[str] = None
    cost: Optional[Decimal] = None
    vendor: Optional[str] = None
    next_maintenance_date: Optional[date] = None

class AssetMaintenanceResponse(AssetMaintenanceBase):
    id: str
    created_by: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Statistics schema
class AssetStatsResponse(BaseModel):
    total_assets: int
    total_cost: Decimal
    total_accumulated_depreciation: Decimal
    total_current_value: Decimal
    monthly_depreciation: Decimal
    maintenance_due: int

# Disposal schema
class AssetDisposalRequest(BaseModel):
    disposal_date: date
    disposal_amount: Decimal = Field(..., ge=0)
    disposal_reason: str = Field(..., max_length=255)