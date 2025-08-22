from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, Enum as SQLEnum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.core.db.base import Base
from app.models.mixins import TimestampMixin


class AttachmentType(str, Enum):
    RECEIPT = "receipt"
    INVOICE = "invoice"
    FORM = "form"
    CERTIFICATE = "certificate"
    SUPPORTING_DOC = "supporting_document"
    OTHER = "other"


class TaxReturnAttachment(Base, TimestampMixin):
    """Model for storing attachments related to tax returns"""
    __tablename__ = "tax_return_attachments"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    tax_return_id = Column(PG_UUID(as_uuid=True), ForeignKey("tax_returns.id"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)  # Path in storage (S3, local, etc.)
    file_type = Column(String(50), nullable=False)  # MIME type
    file_size = Column(Integer, nullable=False)  # Size in bytes
    attachment_type = Column(SQLEnum(AttachmentType), default=AttachmentType.OTHER, nullable=False)
    description = Column(String(500), nullable=True)
    uploaded_by = Column(PG_UUID(as_uuid=True), nullable=False)
    
    # Relationships
    tax_return = relationship("TaxReturn", back_populates="attachments")
    
    def __repr__(self):
        return f"<TaxReturnAttachment {self.file_name} ({self.attachment_type})>"


__all__ = ["TaxReturnAttachment", "AttachmentType"]
