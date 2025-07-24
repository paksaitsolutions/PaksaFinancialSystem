"""
Schemas for inventory transaction API endpoints.
"""
from typing import Optional
from uuid import UUID
from datetime import date
from decimal import Decimal
from pydantic import BaseModel

from app.models.enums import TransactionType

class InventoryTransactionResponse(BaseModel):
    """Schema for inventory transaction response."""
    id: UUID
    item_id: UUID
    location_id: UUID
    transaction_type: TransactionType
    transaction_date: date
    reference: Optional[str] = None
    quantity: Decimal
    unit_cost: Decimal
    total_cost: Decimal
    quantity_before: Decimal
    quantity_after: Decimal
    notes: Optional[str] = None
    item_sku: Optional[str] = None
    item_name: Optional[str] = None
    location_name: Optional[str] = None

    class Config:
        orm_mode = True