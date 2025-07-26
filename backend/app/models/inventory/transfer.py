"""
Multi-location transfer models.
"""
import uuid
from datetime import date, datetime
from sqlalchemy import Column, String, Boolean, ForeignKey, Date, DateTime, Numeric, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base

class LocationTransfer(Base):
    """Multi-location transfer model."""
    
    __tablename__ = "location_transfer"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    transfer_number = Column(String(50), nullable=False, unique=True, index=True)
    from_location_id = Column(UUID(as_uuid=True), ForeignKey("inventory_location.id"), nullable=False)
    to_location_id = Column(UUID(as_uuid=True), ForeignKey("inventory_location.id"), nullable=False)
    
    # Transfer details
    transfer_date = Column(Date, nullable=False, default=date.today)
    requested_by = Column(UUID(as_uuid=True), nullable=False)
    approved_by = Column(UUID(as_uuid=True))
    
    status = Column(String(20), default="pending")  # pending, approved, in_transit, completed, cancelled
    
    # Tracking
    shipped_date = Column(Date)
    received_date = Column(Date)
    tracking_number = Column(String(100))
    
    notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    from_location = relationship("InventoryLocation", foreign_keys=[from_location_id])
    to_location = relationship("InventoryLocation", foreign_keys=[to_location_id])
    items = relationship("TransferItem", back_populates="transfer")

class TransferItem(Base):
    """Transfer item details."""
    
    __tablename__ = "transfer_item"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transfer_id = Column(UUID(as_uuid=True), ForeignKey("location_transfer.id"), nullable=False)
    item_id = Column(UUID(as_uuid=True), ForeignKey("inventory_item.id"), nullable=False)
    
    # Quantities
    quantity_requested = Column(Numeric(precision=18, scale=4), nullable=False)
    quantity_shipped = Column(Numeric(precision=18, scale=4), default=0)
    quantity_received = Column(Numeric(precision=18, scale=4), default=0)
    
    # Costing
    unit_cost = Column(Numeric(precision=18, scale=4), default=0)
    total_cost = Column(Numeric(precision=18, scale=4), default=0)
    
    notes = Column(Text)
    
    # Relationships
    transfer = relationship("LocationTransfer", back_populates="items")
    item = relationship("InventoryItem")

class CycleCount(Base):
    """Cycle count model."""
    
    __tablename__ = "cycle_count"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    count_number = Column(String(50), nullable=False, unique=True, index=True)
    location_id = Column(UUID(as_uuid=True), ForeignKey("inventory_location.id"), nullable=False)
    
    # Count details
    count_date = Column(Date, nullable=False, default=date.today)
    count_type = Column(String(20), default="full")  # full, partial, abc_analysis
    
    status = Column(String(20), default="planned")  # planned, in_progress, completed, cancelled
    
    # Personnel
    counted_by = Column(UUID(as_uuid=True))
    reviewed_by = Column(UUID(as_uuid=True))
    approved_by = Column(UUID(as_uuid=True))
    
    # Results
    total_items_counted = Column(Integer, default=0)
    items_with_variances = Column(Integer, default=0)
    total_variance_value = Column(Numeric(precision=18, scale=2), default=0)
    
    notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    location = relationship("InventoryLocation")
    items = relationship("CycleCountItem", back_populates="cycle_count")

class CycleCountItem(Base):
    """Cycle count item details."""
    
    __tablename__ = "cycle_count_item"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cycle_count_id = Column(UUID(as_uuid=True), ForeignKey("cycle_count.id"), nullable=False)
    item_id = Column(UUID(as_uuid=True), ForeignKey("inventory_item.id"), nullable=False)
    
    # Count data
    system_quantity = Column(Numeric(precision=18, scale=4), nullable=False)
    counted_quantity = Column(Numeric(precision=18, scale=4))
    variance_quantity = Column(Numeric(precision=18, scale=4), default=0)
    
    # Costing
    unit_cost = Column(Numeric(precision=18, scale=4), default=0)
    variance_value = Column(Numeric(precision=18, scale=2), default=0)
    
    # Status
    is_counted = Column(Boolean, default=False)
    requires_recount = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=False)
    
    notes = Column(Text)
    
    # Relationships
    cycle_count = relationship("CycleCount", back_populates="items")
    item = relationship("InventoryItem")

class BarcodeMapping(Base):
    """Barcode mapping for items."""
    
    __tablename__ = "barcode_mapping"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    item_id = Column(UUID(as_uuid=True), ForeignKey("inventory_item.id"), nullable=False)
    barcode = Column(String(100), nullable=False, index=True)
    barcode_type = Column(String(20), default="UPC")  # UPC, EAN, Code128, QR
    
    is_primary = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    item = relationship("InventoryItem")