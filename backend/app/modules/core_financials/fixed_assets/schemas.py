<<<<<<< HEAD
"""
Fixed Assets Module - Pydantic Schemas
"""
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional, Dict, Any, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator, HttpUrl, condecimal
from pydantic.types import conint, constr

from app.core.schemas import BaseResponse, PaginatedResponse
from .models import (
    AssetStatus, 
    AssetCondition, 
    DepreciationMethod,
    Asset as AssetModel,
    AssetCategory as AssetCategoryModel,
    MaintenanceRecord as MaintenanceRecordModel,
    DepreciationSchedule as DepreciationScheduleModel,
    AssetTransfer as AssetTransferModel
)

# Shared schemas
class AssetBase(BaseModel):
    """Base schema for asset operations."""
    name: str = Field(..., max_length=200, description="Name of the asset")
    asset_number: Optional[str] = Field(None, max_length=50, description="Internal asset ID")
    serial_number: Optional[str] = Field(None, max_length=100, description="Manufacturer's serial number")
    barcode: Optional[str] = Field(None, max_length=100, description="Barcode/UPC")
    description: Optional[str] = Field(None, description="Detailed description of the asset")
    model: Optional[str] = Field(None, max_length=100, description="Model name/number")
    manufacturer: Optional[str] = Field(None, max_length=100, description="Manufacturer name")
    purchase_order: Optional[str] = Field(None, max_length=50, description="Purchase order number")
    
    # Acquisition details
    purchase_date: date = Field(..., description="Date when the asset was acquired")
    purchase_price: Decimal = Field(0, ge=0, max_digits=19, decimal_places=4, description="Actual price paid for the asset")
    sales_tax: Decimal = Field(0, ge=0, max_digits=19, decimal_places=4, description="Sales tax amount")
    shipping_cost: Decimal = Field(0, ge=0, max_digits=19, decimal_places=4, description="Shipping and handling costs")
    installation_cost: Decimal = Field(0, ge=0, max_digits=19, decimal_places=4, description="Installation costs")
    other_costs: Decimal = Field(0, ge=0, max_digits=19, decimal_places=4, description="Other acquisition costs")
    
    # Depreciation details
    depreciation_method: DepreciationMethod = Field(
        DepreciationMethod.STRAIGHT_LINE,
        description="Method used to calculate depreciation"
    )
    useful_life_years: Optional[int] = Field(None, ge=1, description="Useful life in years")
    useful_life_units: Optional[int] = Field(None, ge=1, description="Total units of production for units of production method")
    salvage_value: Decimal = Field(0, ge=0, max_digits=19, decimal_places=4, description="Estimated salvage value at end of useful life")
    start_depreciation_date: Optional[date] = Field(None, description="Date when depreciation begins")
    
    # Current status
    status: AssetStatus = Field(AssetStatus.ACTIVE, description="Current status of the asset")
    condition: Optional[AssetCondition] = Field(None, description="Physical condition of the asset")
    location: Optional[str] = Field(None, max_length=200, description="Current physical location")
    
    # Insurance
    insured: bool = Field(False, description="Whether the asset is insured")
    insurance_policy_number: Optional[str] = Field(None, max_length=100, description="Insurance policy number")
    insurance_value: Optional[Decimal] = Field(None, ge=0, max_digits=19, decimal_places=4, description="Insured value")
    insurance_expiry: Optional[date] = Field(None, description="Insurance expiration date")
    
    # Warranty
    under_warranty: bool = Field(False, description="Whether the asset is under warranty")
    warranty_expiry: Optional[date] = Field(None, description="Warranty expiration date")
    warranty_notes: Optional[str] = Field(None, description="Warranty terms and conditions")
    
    # Accounting integration
    asset_account_id: Optional[UUID] = Field(None, description="GL account for the asset")
    accumulated_depreciation_account_id: Optional[UUID] = Field(None, description="GL account for accumulated depreciation")
    depreciation_expense_account_id: Optional[UUID] = Field(None, description="GL account for depreciation expense")
    gain_loss_account_id: Optional[UUID] = Field(None, description="GL account for gain/loss on disposal")
    
    # Relationships
    category_id: UUID = Field(..., description="ID of the asset category")
    
    # Metadata
    tags: Optional[List[str]] = Field(None, description="Tags for categorization and filtering")
    custom_fields: Optional[Dict[str, Any]] = Field(None, description="Custom fields for extensibility")
    
    class Config:
        orm_mode = True
        json_encoders = {
            Decimal: lambda v: str(v)  # Convert Decimal to string for JSON serialization
        }
    
    @validator('start_depreciation_date', pre=True, always=True)
    def set_start_depreciation_date(cls, v, values):
        """Set default start_depreciation_date to purchase_date if not provided."""
        if v is None and 'purchase_date' in values:
            return values['purchase_date']
        return v
    
    @validator('useful_life_years', pre=True, always=True)
    def validate_useful_life(cls, v, values):
        """Validate useful life based on depreciation method."""
        if v is None and values.get('depreciation_method') != DepreciationMethod.UNITS_OF_PRODUCTION:
            raise ValueError("useful_life_years is required for this depreciation method")
        return v


class AssetCreate(AssetBase):
    """Schema for creating a new asset."""
    pass


class AssetUpdate(BaseModel):
    """Schema for updating an existing asset."""
    name: Optional[str] = Field(None, max_length=200, description="Name of the asset")
    description: Optional[str] = Field(None, description="Detailed description of the asset")
    status: Optional[AssetStatus] = Field(None, description="Current status of the asset")
    condition: Optional[AssetCondition] = Field(None, description="Physical condition of the asset")
    location: Optional[str] = Field(None, max_length=200, description="Current physical location")
    tags: Optional[List[str]] = Field(None, description="Tags for categorization and filtering")
    custom_fields: Optional[Dict[str, Any]] = Field(None, description="Custom fields for extensibility")
    
    class Config:
        orm_mode = True
        json_encoders = {
            Decimal: lambda v: str(v)
        }


class AssetResponse(AssetBase, BaseResponse):
    """Schema for returning asset data in API responses."""
    id: UUID
    total_cost: Decimal = Field(..., description="Total capitalized cost of the asset")
    current_book_value: Decimal = Field(..., description="Current book value (cost - accumulated depreciation)")
    months_depreciated: int = Field(..., description="Number of months the asset has been depreciated")
    months_remaining: int = Field(..., description="Number of months remaining in useful life")
    created_at: datetime
    updated_at: datetime


class AssetListResponse(PaginatedResponse):
    """Schema for returning a paginated list of assets."""
    data: List[AssetResponse]


# Asset Category Schemas
class AssetCategoryBase(BaseModel):
    """Base schema for asset categories."""
    name: str = Field(..., max_length=100, description="Name of the category")
    description: Optional[str] = Field(None, description="Description of the category")
    
    # Default accounting settings
    default_asset_account_id: Optional[UUID] = Field(None, description="Default GL account for assets in this category")
    default_depreciation_expense_account_id: Optional[UUID] = Field(
        None, 
        description="Default GL account for depreciation expense"
    )
    default_accumulated_depreciation_account_id: Optional[UUID] = Field(
        None, 
        description="Default GL account for accumulated depreciation"
    )
    default_gain_loss_account_id: Optional[UUID] = Field(
        None, 
        description="Default GL account for gain/loss on disposal"
    )
    default_depreciation_method: DepreciationMethod = Field(
        DepreciationMethod.STRAIGHT_LINE,
        description="Default depreciation method for this category"
    )
    default_useful_life_years: Optional[int] = Field(
        None, 
        ge=1, 
        description="Default useful life in years for this category"
    )
    
    class Config:
        orm_mode = True


class AssetCategoryCreate(AssetCategoryBase):
    """Schema for creating a new asset category."""
    pass


class AssetCategoryUpdate(BaseModel):
    """Schema for updating an existing asset category."""
    name: Optional[str] = Field(None, max_length=100, description="Name of the category")
    description: Optional[str] = Field(None, description="Description of the category")
    default_asset_account_id: Optional[UUID] = Field(None, description="Default GL account for assets in this category")
    default_depreciation_expense_account_id: Optional[UUID] = Field(
        None, 
        description="Default GL account for depreciation expense"
    )
    default_accumulated_depreciation_account_id: Optional[UUID] = Field(
        None, 
        description="Default GL account for accumulated depreciation"
    )
    default_gain_loss_account_id: Optional[UUID] = Field(
        None, 
        description="Default GL account for gain/loss on disposal"
    )
    default_depreciation_method: Optional[DepreciationMethod] = Field(
        None,
        description="Default depreciation method for this category"
    )
    default_useful_life_years: Optional[int] = Field(
        None, 
        ge=1, 
        description="Default useful life in years for this category"
    )
    
    class Config:
        orm_mode = True


class AssetCategoryResponse(AssetCategoryBase, BaseResponse):
    """Schema for returning asset category data in API responses."""
    id: UUID
    created_at: datetime
    updated_at: datetime


class AssetCategoryListResponse(PaginatedResponse):
    """Schema for returning a paginated list of asset categories."""
    data: List[AssetCategoryResponse]


# Maintenance Record Schemas
class MaintenanceRecordBase(BaseModel):
    """Base schema for maintenance records."""
    maintenance_date: date = Field(..., description="Date when maintenance was performed")
    maintenance_type: str = Field(..., max_length=50, description="Type of maintenance performed")
    summary: str = Field(..., max_length=200, description="Brief summary of the maintenance")
    description: Optional[str] = Field(None, description="Detailed description of the maintenance")
    service_provider: Optional[str] = Field(None, max_length=100, description="Name of the service provider")
    service_contact: Optional[str] = Field(None, max_length=100, description="Contact person for the service")
    service_phone: Optional[str] = Field(None, max_length=20, description="Contact phone number")
    service_email: Optional[str] = Field(None, max_length=100, description="Contact email")
    labor_cost: Decimal = Field(0, ge=0, max_digits=19, decimal_places=4, description="Cost of labor")
    parts_cost: Decimal = Field(0, ge=0, max_digits=19, decimal_places=4, description="Cost of parts")
    start_time: Optional[datetime] = Field(None, description="When the maintenance started")
    end_time: Optional[datetime] = Field(None, description="When the maintenance was completed")
    next_maintenance_date: Optional[date] = Field(None, description="Recommended date for next maintenance")
    status: str = Field("completed", description="Status of the maintenance")
    document_reference: Optional[str] = Field(None, max_length=200, description="Reference to related documents")
    
    class Config:
        orm_mode = True
        json_encoders = {
            Decimal: lambda v: str(v)
        }


class MaintenanceRecordCreate(MaintenanceRecordBase):
    """Schema for creating a new maintenance record."""
    asset_id: UUID = Field(..., description="ID of the asset being maintained")


class MaintenanceRecordUpdate(BaseModel):
    """Schema for updating an existing maintenance record."""
    maintenance_date: Optional[date] = Field(None, description="Date when maintenance was performed")
    maintenance_type: Optional[str] = Field(None, max_length=50, description="Type of maintenance performed")
    summary: Optional[str] = Field(None, max_length=200, description="Brief summary of the maintenance")
    description: Optional[str] = Field(None, description="Detailed description of the maintenance")
    service_provider: Optional[str] = Field(None, max_length=100, description="Name of the service provider")
    labor_cost: Optional[Decimal] = Field(None, ge=0, max_digits=19, decimal_places=4, description="Cost of labor")
    parts_cost: Optional[Decimal] = Field(None, ge=0, max_digits=19, decimal_places=4, description="Cost of parts")
    status: Optional[str] = Field(None, description="Status of the maintenance")
    
    class Config:
        orm_mode = True
        json_encoders = {
            Decimal: lambda v: str(v)
        }


class MaintenanceRecordResponse(MaintenanceRecordBase, BaseResponse):
    """Schema for returning maintenance record data in API responses."""
    id: UUID
    asset_id: UUID
    total_cost: Decimal = Field(..., description="Total cost of maintenance (labor + parts)")
    created_at: datetime
    updated_at: datetime


class MaintenanceRecordListResponse(PaginatedResponse):
    """Schema for returning a paginated list of maintenance records."""
    data: List[MaintenanceRecordResponse]


# Depreciation Schedule Schemas
class DepreciationScheduleBase(BaseModel):
    """Base schema for depreciation schedules."""
    fiscal_year: int = Field(..., ge=1900, le=2100, description="Fiscal year")
    period: int = Field(..., ge=1, le=12, description="Accounting period (1-12)")
    start_date: date = Field(..., description="Start date of the period")
    end_date: date = Field(..., description="End date of the period")
    depreciation_amount: Decimal = Field(..., ge=0, max_digits=19, decimal_places=4, description="Depreciation amount for the period")
    accumulated_depreciation: Decimal = Field(..., ge=0, max_digits=19, decimal_places=4, description="Accumulated depreciation as of the end of the period")
    book_value: Decimal = Field(..., ge=0, max_digits=19, decimal_places=4, description="Book value as of the end of the period")
    is_posted: bool = Field(False, description="Whether the depreciation has been posted to the GL")
    
    class Config:
        orm_mode = True
        json_encoders = {
            Decimal: lambda v: str(v)
        }


class DepreciationScheduleResponse(DepreciationScheduleBase, BaseResponse):
    """Schema for returning depreciation schedule data in API responses."""
    id: UUID
    asset_id: UUID
    posted_date: Optional[date] = Field(None, description="Date when the depreciation was posted to the GL")
    created_at: datetime
    updated_at: datetime


class DepreciationScheduleListResponse(PaginatedResponse):
    """Schema for returning a paginated list of depreciation schedules."""
    data: List[DepreciationScheduleResponse]


# Asset Transfer Schemas
class AssetTransferBase(BaseModel):
    """Base schema for asset transfers."""
    transfer_date: date = Field(..., description="Date when the transfer occurred")
    transfer_reason: Optional[str] = Field(None, max_length=200, description="Reason for the transfer")
    transfer_notes: Optional[str] = Field(None, description="Additional notes about the transfer")
    from_location: Optional[str] = Field(None, max_length=200, description="Previous location of the asset")
    to_location: str = Field(..., max_length=200, description="New location of the asset")
    from_department: Optional[str] = Field(None, max_length=100, description="Previous department")
    to_department: Optional[str] = Field(None, max_length=100, description="New department")
    
    class Config:
        orm_mode = True


class AssetTransferCreate(AssetTransferBase):
    """Schema for creating a new asset transfer."""
    asset_id: UUID = Field(..., description="ID of the asset being transferred")


class AssetTransferResponse(AssetTransferBase, BaseResponse):
    """Schema for returning asset transfer data in API responses."""
    id: UUID
    asset_id: UUID
    transferred_by_id: Optional[UUID] = Field(None, description="ID of the user who initiated the transfer")
    received_by_id: Optional[UUID] = Field(None, description="ID of the user who received the asset")
    created_at: datetime
    updated_at: datetime


class AssetTransferListResponse(PaginatedResponse):
    """Schema for returning a paginated list of asset transfers."""
    data: List[AssetTransferResponse]


# Report Schemas
class DepreciationReportRequest(BaseModel):
    """Schema for requesting a depreciation report."""
    start_date: date = Field(..., description="Start date of the report period")
    end_date: date = Field(..., description="End date of the report period")
    category_id: Optional[UUID] = Field(None, description="Filter by asset category")
    department: Optional[str] = Field(None, description="Filter by department")
    location: Optional[str] = Field(None, description="Filter by location")
    status: Optional[AssetStatus] = Field(None, description="Filter by asset status")


class MaintenanceReportRequest(BaseModel):
    """Schema for requesting a maintenance report."""
    start_date: date = Field(..., description="Start date of the report period")
    end_date: date = Field(..., description="End date of the report period")
    category_id: Optional[UUID] = Field(None, description="Filter by asset category")
    maintenance_type: Optional[str] = Field(None, description="Filter by maintenance type")
    status: Optional[str] = Field(None, description="Filter by maintenance status")


class AssetValuationReportRequest(BaseModel):
    """Schema for requesting an asset valuation report."""
    as_of_date: date = Field(..., description="Valuation date")
    category_id: Optional[UUID] = Field(None, description="Filter by asset category")
    department: Optional[str] = Field(None, description="Filter by department")
    location: Optional[str] = Field(None, description="Filter by location")
=======
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
>>>>>>> e96df7278ce4216131b6c65d411c0723f4de7f91
