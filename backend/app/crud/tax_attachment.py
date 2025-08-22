from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app import models, schemas
from app.crud.base import CRUDBase
from app.models.tax_return_attachment import TaxReturnAttachment
from app.schemas.tax_attachment import (
    AttachmentType,
    TaxAttachmentBase,
    TaxAttachmentCreate,
    TaxAttachmentUpdate,
)


class CRUDTaxAttachment(CRUDBase[TaxReturnAttachment, TaxAttachmentCreate, TaxAttachmentUpdate]):
    def get_multi_by_tax_return(
        self, db: Session, *, tax_return_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[TaxReturnAttachment]:
        """
        Retrieve all attachments for a specific tax return
        """
        return (
            db.query(self.model)
            .filter(TaxReturnAttachment.tax_return_id == tax_return_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_multi_by_type(
        self, db: Session, *, attachment_type: AttachmentType, skip: int = 0, limit: int = 100
    ) -> List[TaxReturnAttachment]:
        """
        Retrieve all attachments of a specific type
        """
        return (
            db.query(self.model)
            .filter(TaxReturnAttachment.attachment_type == attachment_type)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_multi_by_uploader(
        self, db: Session, *, uploaded_by: UUID, skip: int = 0, limit: int = 100
    ) -> List[TaxReturnAttachment]:
        """
        Retrieve all attachments uploaded by a specific user
        """
        return (
            db.query(self.model)
            .filter(TaxReturnAttachment.uploaded_by == uploaded_by)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_with_uploader(
        self, db: Session, *, obj_in: TaxAttachmentCreate, uploaded_by: UUID
    ) -> TaxReturnAttachment:
        """
        Create a new tax return attachment with the uploader information
        """
        db_obj = self.model(
            **obj_in.dict(exclude={"metadata"}),
            uploaded_by=uploaded_by,
            metadata=obj_in.metadata or {},
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_metadata(
        self, db: Session, *, db_obj: TaxReturnAttachment, metadata_updates: Dict[str, Any]
    ) -> TaxReturnAttachment:
        """
        Update the metadata of an attachment
        """
        current_metadata = db_obj.metadata or {}
        current_metadata.update(metadata_updates)
        return self.update(
            db, db_obj=db_obj, obj_in={"metadata": current_metadata, "updated_at": datetime.utcnow()}
        )

    def get_by_file_path(self, db: Session, *, file_path: str) -> Optional[TaxReturnAttachment]:
        """
        Get an attachment by its file path
        """
        return db.query(self.model).filter(TaxReturnAttachment.file_path == file_path).first()

    def get_attachments_summary(
        self, db: Session, *, tax_return_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Get summary statistics for attachments
        """
        query = db.query(
            TaxReturnAttachment.attachment_type,
            TaxReturnAttachment.file_type,
            TaxReturnAttachment.file_size,
        )

        if tax_return_id:
            query = query.filter(TaxReturnAttachment.tax_return_id == tax_return_id)

        attachments = query.all()

        summary = {
            "total_count": len(attachments),
            "total_size": sum(a.file_size for a in attachments if a.file_size is not None),
            "by_type": {},
            "by_file_type": {},
        }

        # Count by attachment type
        for attachment in attachments:
            # By attachment type
            a_type = attachment.attachment_type.value
            if a_type not in summary["by_type"]:
                summary["by_type"][a_type] = 0
            summary["by_type"][a_type] += 1

            # By file type
            file_type = attachment.file_type.split("/")[-1].upper()
            if file_type not in summary["by_file_type"]:
                summary["by_file_type"][file_type] = 0
            summary["by_file_type"][file_type] += 1

        return summary

    def validate_file_size(self, file_size: int, max_size_mb: int = 10) -> bool:
        """
        Validate that a file size is within the allowed limit
        """
        max_size_bytes = max_size_mb * 1024 * 1024  # Convert MB to bytes
        return file_size <= max_size_bytes

    def get_attachments_by_tax_return_ids(
        self, db: Session, *, tax_return_ids: List[UUID]
    ) -> List[TaxReturnAttachment]:
        """
        Get all attachments for a list of tax return IDs
        """
        return (
            db.query(self.model)
            .filter(TaxReturnAttachment.tax_return_id.in_(tax_return_ids))
            .all()
        )

    def update_attachment_type(
        self, db: Session, *, db_obj: TaxReturnAttachment, new_type: AttachmentType
    ) -> TaxReturnAttachment:
        """
        Update the type of an attachment
        """
        return self.update(
            db, db_obj=db_obj, obj_in={"attachment_type": new_type, "updated_at": datetime.utcnow()}
        )


# Initialize the CRUD operations for TaxReturnAttachment
tax_attachment = CRUDTaxAttachment(TaxReturnAttachment)
