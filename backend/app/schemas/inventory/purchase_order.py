"""
Schemas for purchase order API endpoints.
"""
from typing import List, Optional
from uuid import UUID
from datetime import date
from decimal import Decimal
from pydantic import BaseModel, Field

from app.models.enums import PurchaseOrderStatus

class PurchaseOrderLineItemBase(BaseModel):
    """Base schema for purchase order line item."""
    item_id: UUID
    quantity_ordered: Decimal = Field(gt=0)
    unit_cost: Decimal = Field(ge=0)

class PurchaseOrderLineItemCreate(PurchaseOrderLineItemBase):
    """Schema for creating a purchase order line item."""
    pass

class PurchaseOrderLineItemResponse(PurchaseOrderLineItemBase):
    """Schema for purchase order line item response."""
    id: UUID
    quantity_received: Decimal
    line_total: Decimal
    item_name: Optional[str] = None
    item_sku: Optional[str] = None

    class Config:
        orm_mode = True

class PurchaseOrderBase(BaseModel):
    """Base schema for purchase order."""
    vendor_id: UUID
    order_date: date = Field(default_factory=date.today)
    expected_date: Optional[date] = None
    notes: Optional[str] = None

class PurchaseOrderCreate(PurchaseOrderBase):
    """Schema for creating a purchase order."""
    line_items: List[PurchaseOrderLineItemCreate]

class PurchaseOrderUpdate(BaseModel):
    """Schema for updating a purchase order."""
    expected_date: Optional[date] = None
    notes: Optional[str] = None
    status: Optional[PurchaseOrderStatus] = None

class PurchaseOrderResponse(PurchaseOrderBase):
    """Schema for purchase order response."""
    id: UUID
    po_number: str
    status: PurchaseOrderStatus
    subtotal: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    line_items: List[PurchaseOrderLineItemResponse] = []

    class Config:
        orm_mode = True

class PurchaseOrderReceiptCreate(BaseModel):
    """Schema for creating a purchase order receipt."""
    purchase_order_id: UUID
    receipt_date: date = Field(default_factory=date.today)
    received_by: Optional[str] = None
    notes: Optional[str] = None
    line_items: List[dict]  # {po_line_item_id, quantity_received, unit_cost}