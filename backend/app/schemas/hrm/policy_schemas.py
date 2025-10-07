from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID


class PolicyBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    content: str = Field(..., min_length=1)
    category: Optional[str] = None
    effective_date: Optional[datetime] = None
    status: str = Field(default="draft", pattern="^(draft|active|inactive|archived)$")


class PolicyCreate(PolicyBase):
    pass


class PolicyUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    content: Optional[str] = Field(None, min_length=1)
    category: Optional[str] = None
    effective_date: Optional[datetime] = None
    status: Optional[str] = Field(None, pattern="^(draft|active|inactive|archived)$")


class PolicyResponse(PolicyBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[UUID] = None
    is_active: bool

    model_config = {"from_attributes": True}