from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
from decimal import Decimal
from enum import Enum

class AssetStatusEnum(str, Enum):
    ACTIVE = "active"
    DISPOSED = "disposed"
    UNDER_MAINTENANCE = "under_maintenance"
    RETIRED = "retired"

class DepreciationMethodEnum(str, Enum):
    STRAIGHT_LINE = "straight_line"
    DECLINING_BALANCE = "declining_balance"
    UNITS_OF_PRODUCTION = "units_of_production"

class MaintenanceStatusEnum(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class FixedAssetBase(BaseModel):
    asset_number: str = Field(..., max_length=50)
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    category: str = Field(..., max_length=100)
    location: Optional[str] = Field(None, max_length=255)
    purchase_date: date
    purchase_cost: Decimal = Field(..., gt=0)
    salvage_value: Decimal = Field(default=0, ge=0)
    useful_life_years: int = Field(..., gt=0)
    depreciation_method: DepreciationMethodEnum = DepreciationMethodEnum.STRAIGHT_LINE
    vendor_name: Optional[str] = Field(None, max_length=255)
    warranty_expiry: Optional[date] = None

class FixedAssetCreate(FixedAssetBase):
    pass

class FixedAssetUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=255)
    salvage_value: Optional[Decimal] = Field(None, ge=0)
    useful_life_years: Optional[int] = Field(None, gt=0)
    depreciation_method: Optional[DepreciationMethodEnum] = None
    vendor_name: Optional[str] = Field(None, max_length=255)
    warranty_expiry: Optional[date] = None
    status: Optional[AssetStatusEnum] = None

class FixedAsset(FixedAssetBase):
    id: int
    status: AssetStatusEnum
    accumulated_depreciation: Decimal
    disposal_date: Optional[date] = None
    disposal_amount: Optional[Decimal] = None
    disposal_reason: Optional[str] = None
    
    class Config:
        from_attributes = True

class DepreciationEntryBase(BaseModel):
    period_date: date
    depreciation_amount: Decimal = Field(..., ge=0)
    accumulated_depreciation: Decimal = Field(..., ge=0)
    book_value: Decimal = Field(..., ge=0)

class DepreciationEntryCreate(DepreciationEntryBase):
    asset_id: int

class DepreciationEntry(DepreciationEntryBase):
    id: int
    asset_id: int
    
    class Config:
        from_attributes = True

class MaintenanceRecordBase(BaseModel):
    maintenance_type: str = Field(..., max_length=100)
    description: str
    scheduled_date: date
    estimated_cost: Optional[Decimal] = Field(None, ge=0)
    vendor_name: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = None

class MaintenanceRecordCreate(MaintenanceRecordBase):
    asset_id: int

class MaintenanceRecordUpdate(BaseModel):
    maintenance_type: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    scheduled_date: Optional[date] = None
    completed_date: Optional[date] = None
    status: Optional[MaintenanceStatusEnum] = None
    estimated_cost: Optional[Decimal] = Field(None, ge=0)
    actual_cost: Optional[Decimal] = Field(None, ge=0)
    vendor_name: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = None
    next_maintenance_date: Optional[date] = None

class MaintenanceRecord(MaintenanceRecordBase):
    id: int
    asset_id: int
    completed_date: Optional[date] = None
    status: MaintenanceStatusEnum
    actual_cost: Optional[Decimal] = None
    next_maintenance_date: Optional[date] = None
    
    class Config:
        from_attributes = True

class AssetCategoryBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    default_useful_life: Optional[int] = Field(None, gt=0)
    default_depreciation_method: DepreciationMethodEnum = DepreciationMethodEnum.STRAIGHT_LINE
    default_salvage_rate: Decimal = Field(default=0, ge=0, le=1)

class AssetCategoryCreate(AssetCategoryBase):
    pass

class AssetCategory(AssetCategoryBase):
    id: int
    
    class Config:
        from_attributes = True

class AssetDisposalRequest(BaseModel):
    disposal_date: date
    disposal_amount: Decimal = Field(..., ge=0)
    disposal_reason: str

class AssetReport(BaseModel):
    total_assets: int
    total_cost: Decimal
    total_accumulated_depreciation: Decimal
    total_book_value: Decimal
    assets_by_category: List[dict]
    assets_by_status: List[dict]

class AssetDisposalResult(BaseModel):
    asset_id: int
    book_value: Optional[Decimal] = None
    disposal_amount: Optional[Decimal] = None
    gain_loss: Optional[Decimal] = None
    disposal_date: Optional[date] = None
    status: str
    error: Optional[str] = None

class BulkAssetUpdate(BaseModel):
    category: Optional[str] = None
    location: Optional[str] = None
    status: Optional[AssetStatusEnum] = None

class BulkDepreciationRequest(BaseModel):
    period_date: date
    category: Optional[str] = None

class AssetTransferRequest(BaseModel):
    asset_ids: List[int]
    new_location: str
    transfer_date: date
    notes: Optional[str] = None