"""
Fixed Assets models for asset management, depreciation, and disposal.
"""
from sqlalchemy import Column, Integer, String, Decimal, Date, DateTime, Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from app.core.db.base import BaseModel, AuditModel
import enum

class AssetStatus(enum.Enum):
    ACTIVE = "active"
    DISPOSED = "disposed"
    RETIRED = "retired"
    UNDER_CONSTRUCTION = "under_construction"

class DepreciationMethod(enum.Enum):
    STRAIGHT_LINE = "straight_line"
    DECLINING_BALANCE = "declining_balance"
    UNITS_OF_PRODUCTION = "units_of_production"

class Asset(AuditModel):
    __tablename__ = 'assets'
    
    asset_number = Column(String(50), unique=True, nullable=False)
    asset_name = Column(String(100), nullable=False)
    asset_category = Column(String(50), nullable=False)
    description = Column(Text)
    acquisition_date = Column(Date, nullable=False)
    acquisition_cost = Column(Decimal(15, 2), nullable=False)
    salvage_value = Column(Decimal(15, 2), default=0)
    useful_life_years = Column(Integer, nullable=False)
    depreciation_method = Column(Enum(DepreciationMethod), default=DepreciationMethod.STRAIGHT_LINE)
    accumulated_depreciation = Column(Decimal(15, 2), default=0)
    book_value = Column(Decimal(15, 2), nullable=False)
    status = Column(Enum(AssetStatus), default=AssetStatus.ACTIVE)
    location = Column(String(100))
    
    depreciation_schedules = relationship("DepreciationSchedule", back_populates="asset")
    maintenance_records = relationship("MaintenanceRecord", back_populates="asset")

class DepreciationSchedule(BaseModel):
    __tablename__ = 'depreciation_schedules'
    
    asset_id = Column(Integer, ForeignKey('assets.id'), nullable=False)
    period_date = Column(Date, nullable=False)
    depreciation_amount = Column(Decimal(15, 2), nullable=False)
    accumulated_depreciation = Column(Decimal(15, 2), nullable=False)
    book_value = Column(Decimal(15, 2), nullable=False)
    is_posted = Column(Boolean, default=False)
    
    asset = relationship("Asset", back_populates="depreciation_schedules")

class MaintenanceRecord(AuditModel):
    __tablename__ = 'maintenance_records'
    
    asset_id = Column(Integer, ForeignKey('assets.id'), nullable=False)
    maintenance_date = Column(Date, nullable=False)
    maintenance_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    cost = Column(Decimal(15, 2), default=0)
    vendor = Column(String(100))
    next_maintenance_date = Column(Date)
    
    asset = relationship("Asset", back_populates="maintenance_records")

class AssetDisposal(AuditModel):
    __tablename__ = 'asset_disposals'
    
    asset_id = Column(Integer, ForeignKey('assets.id'), nullable=False)
    disposal_date = Column(Date, nullable=False)
    disposal_method = Column(String(50), nullable=False)
    sale_proceeds = Column(Decimal(15, 2), default=0)
    disposal_cost = Column(Decimal(15, 2), default=0)
    gain_loss = Column(Decimal(15, 2), default=0)
    reason = Column(Text)