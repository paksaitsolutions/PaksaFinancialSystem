from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal
from datetime import date
from uuid import UUID
from enum import Enum

class InvoiceStatus(str, Enum):
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"

class InvoiceLineItem(BaseModel):
    description: str
    quantity: Decimal
    unit_price: Decimal
    amount: Decimal

class InvoiceBase(BaseModel):
    customer_id: UUID
    invoice_date: date
    due_date: date
    reference: Optional[str] = None
    notes: Optional[str] = None
    line_items: List[InvoiceLineItem]

class InvoiceCreate(InvoiceBase):
    pass

class Invoice(InvoiceBase):
    id: UUID
    invoice_number: str
    status: InvoiceStatus
    subtotal: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    paid_amount: Decimal = Decimal("0.00")
    balance: Decimal
    
    class Config:
        from_attributes = True