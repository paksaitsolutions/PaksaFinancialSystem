from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, Integer
from sqlalchemy.types import DECIMAL as Decimal
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime

class InventoryItem(Base):
    __tablename__ = "inventory_items"
    
    id = Column(String, primary_key=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    item_code = Column(String(50), unique=True, nullable=False)
    item_name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100))
    unit_of_measure = Column(String(20))
    cost_price = Column(Decimal(15, 2))
    selling_price = Column(Decimal(15, 2))
    reorder_level = Column(Integer, default=0)
    maximum_level = Column(Integer)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class InventoryLocation(Base):
    __tablename__ = "inventory_locations"
    
    id = Column(String, primary_key=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    location_code = Column(String(20), unique=True, nullable=False)
    location_name = Column(String(255), nullable=False)
    address = Column(Text)
    location_type = Column(String(50))  # warehouse, store, depot
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class InventoryTransaction(Base):
    __tablename__ = "inventory_transactions"
    
    id = Column(String, primary_key=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    item_id = Column(String, ForeignKey("inventory_items.id"), nullable=False)
    location_id = Column(String, ForeignKey("inventory_locations.id"), nullable=False)
    transaction_type = Column(String(20), nullable=False)  # in, out, adjustment
    quantity = Column(Integer, nullable=False)
    unit_cost = Column(Decimal(15, 2))
    total_value = Column(Decimal(15, 2))
    reference = Column(String(100))
    notes = Column(Text)
    transaction_date = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String, ForeignKey("users.id"))

class InventoryAdjustment(Base):
    __tablename__ = "inventory_adjustments"
    
    id = Column(String, primary_key=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    adjustment_number = Column(String(50), nullable=False)
    adjustment_date = Column(DateTime, nullable=False)
    reason = Column(String(255))
    total_adjustment_value = Column(Decimal(15, 2), default=0)
    status = Column(String(20), default="draft")
    created_by = Column(String, ForeignKey("users.id"))
    approved_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

class FixedAsset(Base):
    __tablename__ = "fixed_assets"
    
    id = Column(String, primary_key=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    asset_number = Column(String(50), unique=True, nullable=False)
    asset_name = Column(String(255), nullable=False)
    asset_category = Column(String(100))
    purchase_date = Column(DateTime, nullable=False)
    purchase_cost = Column(Decimal(15, 2), nullable=False)
    accumulated_depreciation = Column(Decimal(15, 2), default=0)
    current_value = Column(Decimal(15, 2))
    depreciation_method = Column(String(50))
    useful_life_years = Column(Integer)
    salvage_value = Column(Decimal(15, 2))
    location = Column(String(255))
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)

class AssetDepreciation(Base):
    __tablename__ = "asset_depreciation"
    
    id = Column(String, primary_key=True)
    asset_id = Column(String, ForeignKey("fixed_assets.id"), nullable=False)
    depreciation_date = Column(DateTime, nullable=False)
    depreciation_amount = Column(Decimal(15, 2), nullable=False)
    accumulated_depreciation = Column(Decimal(15, 2), nullable=False)
    book_value = Column(Decimal(15, 2), nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class AssetMaintenance(Base):
    __tablename__ = "asset_maintenance"
    
    id = Column(String, primary_key=True)
    asset_id = Column(String, ForeignKey("fixed_assets.id"), nullable=False)
    maintenance_date = Column(DateTime, nullable=False)
    maintenance_type = Column(String(100))
    description = Column(Text)
    cost = Column(Decimal(15, 2))
    vendor = Column(String(255))
    next_maintenance_date = Column(DateTime)
    created_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)