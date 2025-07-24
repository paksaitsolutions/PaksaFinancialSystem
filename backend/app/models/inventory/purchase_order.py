"""
Purchase order model for inventory integration.
"""
import uuid
from datetime import date
from sqlalchemy import Column, String, Boolean, ForeignKey, Text, Date, Enum, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.enums import PurchaseOrderStatus

class PurchaseOrder(Base):
    """Purchase order model."""
    
    __tablename__ = "purchase_order"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    po_number = Column(String(50), unique=True, nullable=False, index=True)
    vendor_id = Column(UUID(as_uuid=True), ForeignKey("vendor.id"), nullable=False, index=True)
    
    # Order details
    order_date = Column(Date, nullable=False, default=date.today, index=True)
    expected_date = Column(Date)
    status = Column(Enum(PurchaseOrderStatus), default=PurchaseOrderStatus.DRAFT, nullable=False, index=True)
    
    # Totals
    subtotal = Column(Numeric(precision=18, scale=2), default=0)
    tax_amount = Column(Numeric(precision=18, scale=2), default=0)
    total_amount = Column(Numeric(precision=18, scale=2), default=0)
    
    # Notes
    notes = Column(Text)
    
    # Relationships
    vendor = relationship("Vendor")
    line_items = relationship("PurchaseOrderLineItem", back_populates="purchase_order", cascade="all, delete-orphan")
    receipts = relationship("PurchaseOrderReceipt", back_populates="purchase_order")
    
    def __repr__(self):
        return f"<PurchaseOrder {self.po_number}: {self.total_amount}>"


class PurchaseOrderLineItem(Base):
    """Purchase order line item model."""
    
    __tablename__ = "purchase_order_line_item"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    purchase_order_id = Column(UUID(as_uuid=True), ForeignKey("purchase_order.id"), nullable=False)
    item_id = Column(UUID(as_uuid=True), ForeignKey("inventory_item.id"), nullable=False)
    
    # Line details
    quantity_ordered = Column(Numeric(precision=18, scale=4), nullable=False)
    quantity_received = Column(Numeric(precision=18, scale=4), default=0)
    unit_cost = Column(Numeric(precision=18, scale=4), nullable=False)
    line_total = Column(Numeric(precision=18, scale=2), nullable=False)
    
    # Relationships
    purchase_order = relationship("PurchaseOrder", back_populates="line_items")
    item = relationship("InventoryItem")
    
    def __repr__(self):
        return f"<PurchaseOrderLineItem: {self.quantity_ordered} x {self.unit_cost}>"


class PurchaseOrderReceipt(Base):
    """Purchase order receipt model."""
    
    __tablename__ = "purchase_order_receipt"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    purchase_order_id = Column(UUID(as_uuid=True), ForeignKey("purchase_order.id"), nullable=False)
    receipt_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Receipt details
    receipt_date = Column(Date, nullable=False, default=date.today)
    received_by = Column(String(100))
    notes = Column(Text)
    
    # Relationships
    purchase_order = relationship("PurchaseOrder", back_populates="receipts")
    line_items = relationship("PurchaseOrderReceiptLineItem", back_populates="receipt", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<PurchaseOrderReceipt {self.receipt_number}>"


class PurchaseOrderReceiptLineItem(Base):
    """Purchase order receipt line item model."""
    
    __tablename__ = "purchase_order_receipt_line_item"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    receipt_id = Column(UUID(as_uuid=True), ForeignKey("purchase_order_receipt.id"), nullable=False)
    po_line_item_id = Column(UUID(as_uuid=True), ForeignKey("purchase_order_line_item.id"), nullable=False)
    
    # Receipt line details
    quantity_received = Column(Numeric(precision=18, scale=4), nullable=False)
    unit_cost = Column(Numeric(precision=18, scale=4), nullable=False)
    
    # Relationships
    receipt = relationship("PurchaseOrderReceipt", back_populates="line_items")
    po_line_item = relationship("PurchaseOrderLineItem")
    
    def __repr__(self):
        return f"<PurchaseOrderReceiptLineItem: {self.quantity_received}>"