from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, ForeignKey, Text, Enum, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.db.base import BaseModel
import enum
from datetime import date, datetime
from decimal import Decimal

class AssetStatus(enum.Enum):
    ACTIVE = "active"
    DISPOSED = "disposed"
    UNDER_MAINTENANCE = "under_maintenance"
    RETIRED = "retired"

class DepreciationMethod(enum.Enum):
    STRAIGHT_LINE = "straight_line"
    DECLINING_BALANCE = "declining_balance"
    UNITS_OF_PRODUCTION = "units_of_production"

class MaintenanceStatus(enum.Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class FixedAsset(BaseModel):
    __tablename__ = 'fixed_assets'
    
    asset_number = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100), nullable=False)
    location = Column(String(255))
    
    # Financial details
    purchase_date = Column(Date, nullable=False)
    purchase_cost = Column(Numeric(15, 2), nullable=False)
    salvage_value = Column(Numeric(15, 2), default=0)
    useful_life_years = Column(Integer, nullable=False)
    
    # Depreciation
    depreciation_method = Column(Enum(DepreciationMethod), default=DepreciationMethod.STRAIGHT_LINE)
    accumulated_depreciation = Column(Numeric(15, 2), default=0)
    
    # Status and dates
    status = Column(Enum(AssetStatus), default=AssetStatus.ACTIVE)
    disposal_date = Column(Date)
    disposal_amount = Column(Numeric(15, 2))
    disposal_reason = Column(Text)
    
    # Vendor information
    vendor_name = Column(String(255))
    warranty_expiry = Column(Date)
    
    # Relationships
    depreciation_entries = relationship("DepreciationEntry", back_populates="asset")
    maintenance_records = relationship("MaintenanceRecord", back_populates="asset")

class DepreciationEntry(BaseModel):
    __tablename__ = 'depreciation_entries'
    
    asset_id = Column(Integer, ForeignKey('fixed_assets.id'), nullable=False)
    period_date = Column(Date, nullable=False)
    depreciation_amount = Column(Numeric(15, 2), nullable=False)
    accumulated_depreciation = Column(Numeric(15, 2), nullable=False)
    book_value = Column(Numeric(15, 2), nullable=False)
    
    # Relationships
    asset = relationship("FixedAsset", back_populates="depreciation_entries")

class MaintenanceRecord(BaseModel):
    __tablename__ = 'maintenance_records'
    
    asset_id = Column(Integer, ForeignKey('fixed_assets.id'), nullable=False)
    maintenance_type = Column(String(100), nullable=False)  # Preventive, Corrective, Emergency
    description = Column(Text, nullable=False)
    
    # Scheduling
    scheduled_date = Column(Date, nullable=False)
    completed_date = Column(Date)
    status = Column(Enum(MaintenanceStatus), default=MaintenanceStatus.SCHEDULED)
    
    # Cost and vendor
    estimated_cost = Column(Numeric(15, 2))
    actual_cost = Column(Numeric(15, 2))
    vendor_name = Column(String(255))
    
    # Notes and attachments
    notes = Column(Text)
    next_maintenance_date = Column(Date)
    
    # Relationships
    asset = relationship("FixedAsset", back_populates="maintenance_records")

class AssetCategory(BaseModel):
    __tablename__ = 'asset_categories'
    
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    default_useful_life = Column(Integer)
    default_depreciation_method = Column(Enum(DepreciationMethod), default=DepreciationMethod.STRAIGHT_LINE)
    default_salvage_rate = Column(Numeric(5, 4), default=0)  # Percentage of purchase cost