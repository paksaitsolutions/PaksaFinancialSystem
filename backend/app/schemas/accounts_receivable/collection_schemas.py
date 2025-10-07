from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from uuid import UUID
from decimal import Decimal


class CollectionBase(BaseModel):
    customer_id: UUID
    invoice_id: UUID
    amount_due: Decimal = Field(..., ge=0)
    amount_collected: Decimal = Field(default=0, ge=0)
    days_overdue: Optional[str] = None
    status: str = Field(default="pending", pattern="^(pending|in_progress|collected|written_off)$")
    priority: str = Field(default="medium", pattern="^(low|medium|high|urgent)$")
    collection_method: Optional[str] = None
    notes: Optional[str] = None
    assigned_to: Optional[UUID] = None
    next_action_date: Optional[datetime] = None


class CollectionCreate(CollectionBase):
    pass


class CollectionUpdate(BaseModel):
    amount_collected: Optional[Decimal] = Field(None, ge=0)
    status: Optional[str] = Field(None, pattern="^(pending|in_progress|collected|written_off)$")
    priority: Optional[str] = Field(None, pattern="^(low|medium|high|urgent)$")
    collection_method: Optional[str] = None
    notes: Optional[str] = None
    assigned_to: Optional[UUID] = None
    next_action_date: Optional[datetime] = None


class CollectionResponse(CollectionBase):
    id: UUID
    collection_date: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool

    model_config = {"from_attributes": True}


class CollectionActivityBase(BaseModel):
    collection_id: UUID
    activity_type: str = Field(..., pattern="^(call|email|letter|payment|note)$")
    description: Optional[str] = None
    amount: Optional[Decimal] = Field(None, ge=0)
    performed_by: Optional[UUID] = None


class CollectionActivityCreate(CollectionActivityBase):
    pass


class CollectionActivityResponse(CollectionActivityBase):
    id: UUID
    activity_date: datetime
    created_at: datetime

    model_config = {"from_attributes": True}