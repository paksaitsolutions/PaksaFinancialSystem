from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator, HttpUrl
from enum import Enum

# Enums
class RequisitionStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    CONVERTED_TO_PO = "converted_to_po"

class RequisitionPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class RequisitionItemStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ORDERED = "ordered"
    RECEIVED = "received"
    CANCELLED = "cancelled"

# Base Schemas
class RequisitionItemBase(BaseModel):
    item_name: str = Field(..., max_length=255)
    description: Optional[str] = None
    quantity: float = Field(1.0, gt=0)
    unit_price: float = Field(..., gt=0)
    currency: str = Field("USD", max_length=3)
    item_code: Optional[str] = Field(None, max_length=100)
    category_id: Optional[int] = None
    project_id: Optional[int] = None
    gl_account_id: Optional[int] = None
    status: RequisitionItemStatus = RequisitionItemStatus.PENDING
    
    @validator('total_price', always=True)
    def calculate_total_price(cls, v, values):
        return values['quantity'] * values['unit_price']
    
    class Config:
        orm_mode = True
        use_enum_values = True

class PurchaseRequisitionBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    requisition_date: datetime = Field(default_factory=datetime.utcnow)
    required_date: Optional[datetime] = None
    priority: RequisitionPriority = RequisitionPriority.MEDIUM
    department_id: Optional[int] = None
    notes: Optional[str] = None
    metadata_: Optional[Dict[str, Any]] = Field(None, alias="metadata")
    
    class Config:
        orm_mode = True
        use_enum_values = True
        allow_population_by_field_name = True

# Create/Update Schemas
class RequisitionItemCreate(RequisitionItemBase):
    pass

class RequisitionItemUpdate(RequisitionItemBase):
    item_name: Optional[str] = None
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    currency: Optional[str] = None

class PurchaseRequisitionCreate(PurchaseRequisitionBase):
    items: List[RequisitionItemCreate] = Field(..., min_items=1)

class PurchaseRequisitionUpdate(PurchaseRequisitionBase):
    title: Optional[str] = None
    status: Optional[RequisitionStatus] = None
    items: Optional[List[RequisitionItemUpdate]] = None

# Response Schemas
class RequisitionItemResponse(RequisitionItemBase):
    id: int
    requisition_id: int
    total_price: float
    created_at: datetime
    updated_at: datetime

class PurchaseRequisitionResponse(PurchaseRequisitionBase):
    id: int
    requisition_number: str
    status: RequisitionStatus
    total_amount: float
    currency: str
    requester_id: int
    approver_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    created_by_id: int
    updated_by_id: Optional[int] = None
    items: List[RequisitionItemResponse] = []
    
    class Config:
        orm_mode = True

# List and Detail Schemas
class PurchaseRequisitionList(BaseModel):
    id: int
    requisition_number: str
    title: str
    status: RequisitionStatus
    total_amount: float
    currency: str
    requisition_date: datetime
    required_date: Optional[datetime]
    priority: RequisitionPriority
    requester_id: int
    requester_name: str
    department_name: Optional[str]
    
    class Config:
        orm_mode = True

# Approval Schemas
class RequisitionApproval(BaseModel):
    approved: bool
    notes: Optional[str] = None
    
    class Config:
        orm_mode = True

# Search and Filter Schemas
class RequisitionFilter(BaseModel):
    status: Optional[RequisitionStatus] = None
    priority: Optional[RequisitionPriority] = None
    requester_id: Optional[int] = None
    department_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    search: Optional[str] = None
    
    class Config:
        orm_mode = True
        use_enum_values = True
