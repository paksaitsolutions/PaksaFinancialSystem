from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class BaseCreateSchema(BaseSchema):
    pass

class BaseUpdateSchema(BaseSchema):
    pass

class AuditResponseSchema(BaseSchema):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_active: bool = True