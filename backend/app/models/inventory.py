from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, Integer
from sqlalchemy.types import DECIMAL as Decimal
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime

class InventoryCategory(Base):
    __tablename__ = "inventory_categories"
    
    id = Column(String, primary_key=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    parent_id = Column(String, ForeignKey("inventory_categories.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    parent = relationship("InventoryCategory", remote_side=[id])
    items = relationship("InventoryItem", back_populates="category")

class InventoryItem(Base):
    __tablename__ = "inventory_items"
    
    id = Column(String, primary_key=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    item_code = Column(String(50), unique=True, nullable=False)
    item_name = Column(String(255), nullable=False)
    description = Column(Text)
    category_id = Column(String, ForeignKey("inventory_categories.id"))
    unit_of_measure = Column(String(20))
    cost_price = Column(Decimal(15, 2))
    selling_price = Column(Decimal(15, 2))
    reorder_level = Column(Integer, default=0)
    maximum_level = Column(Integer)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    category = relationship("InventoryCategory", back_populates="items")

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

class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"
    
    id = Column(String, primary_key=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    po_number = Column(String(50), unique=True, nullable=False)
    vendor_id = Column(String, ForeignKey("vendors.id"), nullable=False)
    order_date = Column(DateTime, nullable=False)
    expected_delivery_date = Column(DateTime)
    status = Column(String(20), default="draft")
    subtotal = Column(Decimal(15, 2), default=0)
    tax_amount = Column(Decimal(15, 2), default=0)
    total_amount = Column(Decimal(15, 2), default=0)
    notes = Column(Text)
    created_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

class PurchaseOrderLineItem(Base):
    __tablename__ = "purchase_order_line_items"
    
    id = Column(String, primary_key=True)
    purchase_order_id = Column(String, ForeignKey("purchase_orders.id"), nullable=False)
    item_id = Column(String, ForeignKey("inventory_items.id"), nullable=False)
    quantity_ordered = Column(Integer, nullable=False)
    unit_cost = Column(Decimal(15, 2), nullable=False)
    total_cost = Column(Decimal(15, 2), nullable=False)
    quantity_received = Column(Integer, default=0)
    notes = Column(Text)

class PurchaseOrderReceipt(Base):
    __tablename__ = "purchase_order_receipts"
    
    id = Column(String, primary_key=True)
    purchase_order_id = Column(String, ForeignKey("purchase_orders.id"), nullable=False)
    receipt_number = Column(String(50), unique=True, nullable=False)
    receipt_date = Column(DateTime, nullable=False)
    received_by = Column(String, ForeignKey("users.id"))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class PurchaseOrderReceiptLineItem(Base):
    __tablename__ = "purchase_order_receipt_line_items"
    
    id = Column(String, primary_key=True)
    receipt_id = Column(String, ForeignKey("purchase_order_receipts.id"), nullable=False)
    po_line_item_id = Column(String, ForeignKey("purchase_order_line_items.id"), nullable=False)
    quantity_received = Column(Integer, nullable=False)
    unit_cost = Column(Decimal(15, 2))
    condition = Column(String(20), default="good")
    notes = Column(Text)