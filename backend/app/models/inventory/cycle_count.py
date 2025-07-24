"""
Cycle count model for inventory management.
"""
import uuid
from datetime import date
from sqlalchemy import Column, String, Boolean, ForeignKey, Text, Date, Enum, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.enums import CycleCountStatus

class CycleCount(Base):
    """Cycle count model."""
    
    __tablename__ = "cycle_count"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    count_number = Column(String(50), unique=True, nullable=False, index=True)
    location_id = Column(UUID(as_uuid=True), ForeignKey("inventory_location.id"), nullable=False, index=True)
    
    # Count details
    count_date = Column(Date, nullable=False, default=date.today, index=True)
    status = Column(Enum(CycleCountStatus), default=CycleCountStatus.PENDING, nullable=False, index=True)
    counted_by = Column(String(100))
    
    # Notes
    notes = Column(Text)
    
    # Relationships
    location = relationship("InventoryLocation")
    line_items = relationship("CycleCountLineItem", back_populates="cycle_count", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<CycleCount {self.count_number}: {self.status}>"


class CycleCountLineItem(Base):
    """Cycle count line item model."""
    
    __tablename__ = "cycle_count_line_item"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cycle_count_id = Column(UUID(as_uuid=True), ForeignKey("cycle_count.id"), nullable=False)
    item_id = Column(UUID(as_uuid=True), ForeignKey("inventory_item.id"), nullable=False)
    
    # Count details
    system_quantity = Column(Numeric(precision=18, scale=4), nullable=False)
    counted_quantity = Column(Numeric(precision=18, scale=4))
    variance = Column(Numeric(precision=18, scale=4), default=0)
    is_counted = Column(Boolean, default=False)
    
    # Notes
    notes = Column(Text)
    
    # Relationships
    cycle_count = relationship("CycleCount", back_populates="line_items")
    item = relationship("InventoryItem")
    
    def __repr__(self):
        return f"<CycleCountLineItem {self.item.sku}: {self.counted_quantity}>"