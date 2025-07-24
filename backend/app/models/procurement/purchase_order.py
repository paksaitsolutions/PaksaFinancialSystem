"""
Purchase order models.
"""
import uuid
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import Column, String, Boolean, ForeignKey, Date, DateTime, Numeric, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base

class PurchaseOrder(Base):
    """Purchase order model."""
    
    __tablename__ = "purchase_order"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    po_number = Column(String(50), nullable=False, index=True)
    vendor_id = Column(UUID(as_uuid=True), ForeignKey("vendor.id"), nullable=False)
    
    order_date = Column(Date, nullable=False, default=date.today)
    expected_delivery_date = Column(Date)
    
    subtotal = Column(Numeric(precision=18, scale=2), nullable=False)
    tax_amount = Column(Numeric(precision=18, scale=2), default=0)
    total_amount = Column(Numeric(precision=18, scale=2), nullable=False)
    
    status = Column(String(20), default="draft", index=True)  # draft, pending_approval, approved, sent, received, cancelled
    
    # Approval workflow
    approval_status = Column(String(20), default="pending")  # pending, approved, rejected
    approved_by = Column(UUID(as_uuid=True))
    approved_at = Column(DateTime)
    
    notes = Column(Text)
    terms = Column(Text)
    
    created_by = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    vendor = relationship("Vendor", back_populates="purchase_orders")
    items = relationship("PurchaseOrderItem", back_populates="purchase_order")
    receipts = relationship("PurchaseReceipt", back_populates="purchase_order")

class PurchaseOrderItem(Base):
    """Purchase order item model."""
    
    __tablename__ = "purchase_order_item"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    purchase_order_id = Column(UUID(as_uuid=True), ForeignKey("purchase_order.id"), nullable=False)
    
    item_description = Column(String(500), nullable=False)
    quantity = Column(Numeric(precision=10, scale=2), nullable=False)
    unit_price = Column(Numeric(precision=18, scale=2), nullable=False)
    total_price = Column(Numeric(precision=18, scale=2), nullable=False)
    
    # Inventory integration
    inventory_item_id = Column(UUID(as_uuid=True))
    
    # Receiving tracking
    quantity_received = Column(Numeric(precision=10, scale=2), default=0)
    
    # Relationships
    purchase_order = relationship("PurchaseOrder", back_populates="items")

class PurchaseReceipt(Base):
    """Purchase receipt model."""
    
    __tablename__ = "purchase_receipt"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    purchase_order_id = Column(UUID(as_uuid=True), ForeignKey("purchase_order.id"), nullable=False)
    
    receipt_number = Column(String(50), nullable=False, index=True)
    receipt_date = Column(Date, nullable=False, default=date.today)
    
    notes = Column(Text)
    
    received_by = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    purchase_order = relationship("PurchaseOrder", back_populates="receipts")
    items = relationship("PurchaseReceiptItem", back_populates="receipt")

class PurchaseReceiptItem(Base):
    """Purchase receipt item model."""
    
    __tablename__ = "purchase_receipt_item"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    receipt_id = Column(UUID(as_uuid=True), ForeignKey("purchase_receipt.id"), nullable=False)
    po_item_id = Column(UUID(as_uuid=True), ForeignKey("purchase_order_item.id"), nullable=False)
    
    quantity_received = Column(Numeric(precision=10, scale=2), nullable=False)
    
    # Relationships
    receipt = relationship("PurchaseReceipt", back_populates="items")

class VendorPayment(Base):
    """Vendor payment model."""
    
    __tablename__ = "vendor_payment"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    payment_number = Column(String(50), nullable=False, index=True)
    vendor_id = Column(UUID(as_uuid=True), ForeignKey("vendor.id"), nullable=False)
    purchase_order_id = Column(UUID(as_uuid=True), ForeignKey("purchase_order.id"))
    
    payment_date = Column(Date, nullable=False, default=date.today)
    amount = Column(Numeric(precision=18, scale=2), nullable=False)
    payment_method = Column(String(50), nullable=False)
    reference = Column(String(100))
    
    notes = Column(Text)
    
    created_by = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)