"""
Procurement schemas.
"""
from typing import List, Optional
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel

class VendorBase(BaseModel):
    """Base vendor schema."""
    vendor_code: str
    vendor_name: str
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    tax_id: Optional[str] = None
    payment_terms: str = "Net 30"
    currency_code: str = "USD"
    is_active: bool = True
    notes: Optional[str] = None

class VendorCreate(VendorBase):
    """Create vendor schema."""
    pass

class VendorUpdate(BaseModel):
    """Update vendor schema."""
    vendor_name: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None
    is_approved: Optional[bool] = None

class VendorResponse(VendorBase):
    """Vendor response schema."""
    id: UUID
    tenant_id: UUID
    is_approved: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class PurchaseOrderItemBase(BaseModel):
    """Base purchase order item schema."""
    item_description: str
    quantity: Decimal
    unit_price: Decimal
    total_price: Decimal
    inventory_item_id: Optional[UUID] = None

class PurchaseOrderItemCreate(PurchaseOrderItemBase):
    """Create purchase order item schema."""
    pass

class PurchaseOrderItemResponse(PurchaseOrderItemBase):
    """Purchase order item response schema."""
    id: UUID
    purchase_order_id: UUID
    quantity_received: Decimal

    class Config:
        orm_mode = True

class PurchaseOrderBase(BaseModel):
    """Base purchase order schema."""
    vendor_id: UUID
    order_date: date
    expected_delivery_date: Optional[date] = None
    subtotal: Decimal
    tax_amount: Decimal = 0
    total_amount: Decimal
    notes: Optional[str] = None
    terms: Optional[str] = None

class PurchaseOrderCreate(PurchaseOrderBase):
    """Create purchase order schema."""
    items: List[PurchaseOrderItemCreate]

class PurchaseOrderUpdate(BaseModel):
    """Update purchase order schema."""
    expected_delivery_date: Optional[date] = None
    status: Optional[str] = None
    approval_status: Optional[str] = None
    notes: Optional[str] = None

class PurchaseOrderResponse(PurchaseOrderBase):
    """Purchase order response schema."""
    id: UUID
    tenant_id: UUID
    po_number: str
    status: str
    approval_status: str
    approved_by: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    items: List[PurchaseOrderItemResponse]
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class VendorPaymentBase(BaseModel):
    """Base vendor payment schema."""
    vendor_id: UUID
    purchase_order_id: Optional[UUID] = None
    payment_date: date
    amount: Decimal
    payment_method: str
    reference: Optional[str] = None
    notes: Optional[str] = None

class VendorPaymentCreate(VendorPaymentBase):
    """Create vendor payment schema."""
    pass

class VendorPaymentResponse(VendorPaymentBase):
    """Vendor payment response schema."""
    id: UUID
    tenant_id: UUID
    payment_number: str
    created_by: UUID
    created_at: datetime

    class Config:
        orm_mode = True

class PurchaseAnalytics(BaseModel):
    """Purchase analytics schema."""
    total_orders: int
    total_amount: Decimal
    pending_approvals: int
    top_vendors: List[dict]
    monthly_spending: List[dict]