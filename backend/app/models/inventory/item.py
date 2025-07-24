"""
Inventory item model.
"""
import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, Text, Enum, Numeric, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.enums import InventoryStatus, ValuationMethod

class InventoryItem(Base):
    """Inventory item model."""
    
    __tablename__ = "inventory_item"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sku = Column(String(50), unique=True, nullable=False, index=True)
    barcode = Column(String(100), unique=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    category_id = Column(UUID(as_uuid=True), ForeignKey("inventory_category.id"))
    
    # Status and tracking
    status = Column(Enum(InventoryStatus), default=InventoryStatus.ACTIVE, nullable=False, index=True)
    is_tracked = Column(Boolean, default=True)
    
    # Quantities
    quantity_on_hand = Column(Numeric(precision=18, scale=4), default=0)
    quantity_available = Column(Numeric(precision=18, scale=4), default=0)
    quantity_committed = Column(Numeric(precision=18, scale=4), default=0)
    reorder_point = Column(Numeric(precision=18, scale=4), default=0)
    reorder_quantity = Column(Numeric(precision=18, scale=4), default=0)
    
    # Costing
    valuation_method = Column(Enum(ValuationMethod), default=ValuationMethod.AVERAGE)
    unit_cost = Column(Numeric(precision=18, scale=4), default=0)
    standard_cost = Column(Numeric(precision=18, scale=4), default=0)
    
    # Physical attributes
    unit_of_measure = Column(String(20), default="EA")
    weight = Column(Numeric(precision=18, scale=4))
    dimensions = Column(String(100))
    
    # Locations
    default_location_id = Column(UUID(as_uuid=True), ForeignKey("inventory_location.id"))
    
    # Relationships
    category = relationship("InventoryCategory")
    default_location = relationship("InventoryLocation")
    transactions = relationship("InventoryTransaction", back_populates="item")
    
    def __repr__(self):
        return f"<InventoryItem {self.sku}: {self.name}>"


class InventoryCategory(Base):
    """Inventory category model."""
    
    __tablename__ = "inventory_category"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("inventory_category.id"))
    
    # Relationships
    parent = relationship("InventoryCategory", remote_side=[id])
    items = relationship("InventoryItem", back_populates="category")
    
    def __repr__(self):
        return f"<InventoryCategory {self.code}: {self.name}>"


class InventoryLocation(Base):
    """Inventory location/warehouse model."""
    
    __tablename__ = "inventory_location"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    
    # Address
    address_line1 = Column(String(100))
    address_line2 = Column(String(100))
    city = Column(String(50))
    state = Column(String(50))
    postal_code = Column(String(20))
    country = Column(String(50))
    
    # Relationships
    items = relationship("InventoryItem", back_populates="default_location")
    
    def __repr__(self):
        return f"<InventoryLocation {self.code}: {self.name}>"