from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl, validator

from app.schemas.base import BaseSchema


class AttachmentType(str, Enum):
    RECEIPT = "receipt"
    INVOICE = "invoice"
    FORM = "form"
    CERTIFICATE = "certificate"
    SUPPORTING_DOC = "supporting_document"
    OTHER = "other"


class TaxAttachmentBase(BaseModel):
    file_name: str = Field(..., max_length=255, description="Original name of the file")
    file_path: str = Field(..., max_length=512, description="Path to the file in storage")
    file_type: str = Field(..., max_length=100, description="MIME type of the file")
    file_size: int = Field(..., ge=0, description="Size of the file in bytes")
    attachment_type: AttachmentType = Field(AttachmentType.OTHER, description="Type of attachment")
    description: Optional[str] = Field(None, max_length=500, description="Optional description of the attachment")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata for the attachment")

    @validator('file_size')
    def validate_file_size(cls, v):
        max_size = 10 * 1024 * 1024  # 10MB
        if v > max_size:
            raise ValueError(f'File size cannot exceed {max_size} bytes')
        return v


class TaxAttachmentCreate(TaxAttachmentBase):
    tax_return_id: UUID
    uploaded_by: UUID


class TaxAttachmentUpdate(BaseModel):
    description: Optional[str] = Field(None, max_length=500)
    attachment_type: Optional[AttachmentType] = None
    metadata: Optional[Dict[str, Any]] = None


class TaxAttachmentInDB(TaxAttachmentBase):
    id: UUID
    tax_return_id: UUID
    uploaded_by: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class TaxAttachmentResponse(BaseSchema):
    success: bool = True
    data: TaxAttachmentInDB


class TaxAttachmentListResponse(BaseSchema):
    success: bool = True
    data: List[TaxAttachmentInDB]
    total: int
    page: int
    limit: int


class TaxAttachmentUploadRequest(BaseModel):
    file_name: str = Field(..., max_length=255)
    file_type: str = Field(..., max_length=100)
    file_size: int = Field(..., ge=1)
    attachment_type: AttachmentType = AttachmentType.OTHER
    description: Optional[str] = None


class TaxAttachmentUploadResponse(BaseSchema):
    success: bool = True
    upload_url: HttpUrl
    file_id: UUID
    fields: Dict[str, str]
    expires_in: int  # seconds until URL expires


class TaxAttachmentFilter(BaseModel):
    tax_return_id: Optional[UUID] = None
    attachment_type: Optional[AttachmentType] = None
    uploaded_by: Optional[UUID] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    search: Optional[str] = None
