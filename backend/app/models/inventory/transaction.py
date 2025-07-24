"""
Inventory transaction model.
"""
import uuid
from datetime import date
from sqlalchemy import Column, String, ForeignKey, Text, Date, Enum, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.enums import TransactionType

class InventoryTransaction(Base):
    """Inventory transaction model."""
    
    __tablename__ = "inventory_transaction"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    item_id = Column(UUID(as_uuid=True), ForeignKey("inventory_item.id"), nullable=False, index=True)
    location_id = Column(UUID(as_uuid=True), ForeignKey("inventory_location.id"), nullable=False)
    
    # Transaction details
    transaction_type = Column(Enum(TransactionType), nullable=False, index=True)
    transaction_date = Column(Date, nullable=False, default=date.today, index=True)
    reference = Column(String(100))
    
    # Quantities and costs
    quantity = Column(Numeric(precision=18, scale=4), nullable=False)
    unit_cost = Column(Numeric(precision=18, scale=4), default=0)
    total_cost = Column(Numeric(precision=18, scale=4), default=0)
    
    # Running balances
    quantity_before = Column(Numeric(precision=18, scale=4), default=0)
    quantity_after = Column(Numeric(precision=18, scale=4), default=0)
    
    # Notes
    notes = Column(Text)
    
    # Relationships
    item = relationship("InventoryItem", back_populates="transactions")
    location = relationship("InventoryLocation")
    
    def __repr__(self):
        return f"<InventoryTransaction {self.transaction_type}: {self.quantity}>"