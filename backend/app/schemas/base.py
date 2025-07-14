"""
Base Pydantic schemas for API validation and serialization.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class BaseCreateSchema(BaseSchema):
    pass

class BaseUpdateSchema(BaseSchema):
    pass

class BaseResponseSchema(BaseSchema):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool = True

class AuditResponseSchema(BaseResponseSchema):
    version: int = 1
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    is_deleted: bool = False