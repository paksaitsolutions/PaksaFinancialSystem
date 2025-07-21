from datetime import datetime
from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core.config import settings
from app.core.storage import get_storage_client
from app.schemas.tax_attachment import (
    AttachmentType,
    TaxAttachmentFilter,
    TaxAttachmentResponse,
    TaxAttachmentUploadRequest,
    TaxAttachmentUploadResponse,
)

router = APIRouter()


@router.post("/upload-url", response_model=TaxAttachmentUploadResponse)
def get_upload_url(
    *,
    db: Session = Depends(deps.get_db),
    upload_request: TaxAttachmentUploadRequest,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get a pre-signed URL for uploading a tax return attachment
    """
    # Validate file size
    if not crud.tax_attachment.validate_file_size(upload_request.file_size):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds the maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB",
        )

    # Generate a unique file path
    file_ext = upload_request.file_name.split(".")[-1] if "." in upload_request.file_name else ""
    file_name = f"tax_attachments/{datetime.utcnow().strftime('%Y/%m/%d')}/{UUID(int=current_user.id.int).hex[:8]}_{int(datetime.utcnow().timestamp())}.{file_ext}"
    
    # Generate pre-signed URL
    storage = get_storage_client()
    upload_url = storage.generate_presigned_url(
        file_name=file_name,
        content_type=upload_request.file_type,
        expires_in=3600,  # 1 hour expiration
    )
    
    # Create attachment record in database
    attachment_data = {
        "file_name": upload_request.file_name,
        "file_path": file_name,
        "file_type": upload_request.file_type,
        "file_size": upload_request.file_size,
        "attachment_type": upload_request.attachment_type,
        "description": upload_request.description,
        "uploaded_by": current_user.id,
    }
    
    attachment = crud.tax_attachment.create(db, obj_in=attachment_data)
    
    return {
        "upload_url": upload_url,
        "file_id": attachment.id,
        "fields": {},
        "expires_in": 3600,
    }


@router.post("/{attachment_id}/confirm", response_model=schemas.TaxAttachmentResponse)
def confirm_upload(
    *,
    db: Session = Depends(deps.get_db),
    attachment_id: UUID,
    tax_return_id: UUID = Query(..., description="The ID of the tax return to attach this file to"),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Confirm that a file has been uploaded and attach it to a tax return
    """
    # Get the attachment
    attachment = crud.tax_attachment.get(db, id=attachment_id)
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found",
        )
    
    # Verify the user has permission to attach to this tax return
    tax_return = crud.tax_return.get(db, id=tax_return_id)
    if not tax_return:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tax return not found",
        )
    
    # Update the attachment with the tax return ID
    updated_attachment = crud.tax_attachment.update(
        db,
        db_obj=attachment,
        obj_in={"tax_return_id": tax_return_id},
    )
    
    return {"data": updated_attachment}


@router.get("/{attachment_id}", response_model=schemas.TaxAttachmentResponse)
def get_attachment(
    *,
    db: Session = Depends(deps.get_db),
    attachment_id: UUID,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get a tax return attachment by ID
    """
    attachment = crud.tax_attachment.get(db, id=attachment_id)
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found",
        )
    
    # TODO: Add permission check to ensure user has access to this attachment
    
    return {"data": attachment}


@router.get("/{attachment_id}/download")
def download_attachment(
    *,
    db: Session = Depends(deps.get_db),
    attachment_id: UUID,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Download a tax return attachment
    """
    attachment = crud.tax_attachment.get(db, id=attachment_id)
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found",
        )
    
    # TODO: Add permission check to ensure user has access to this attachment
    
    # Get a download URL for the file
    storage = get_storage_client()
    download_url = storage.generate_presigned_url(
        file_name=attachment.file_path,
        expires_in=300,  # 5 minutes
        download=True,
        download_filename=attachment.file_name,
    )
    
    # Redirect to the download URL
    return JSONResponse(
        status_code=status.HTTP_307_TEMPORARY_REDIRECT,
        headers={"Location": download_url},
        content={"detail": "Redirecting to download URL"},
    )


@router.get("", response_model=schemas.TaxAttachmentListResponse)
def list_attachments(
    *,
    db: Session = Depends(deps.get_db),
    tax_return_id: UUID = None,
    attachment_type: AttachmentType = None,
    uploaded_by: UUID = None,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    List tax return attachments with optional filtering
    """
    # Build filter criteria
    filter_criteria = {}
    if tax_return_id:
        filter_criteria["tax_return_id"] = tax_return_id
    if attachment_type:
        filter_criteria["attachment_type"] = attachment_type
    if uploaded_by:
        filter_criteria["uploaded_by"] = uploaded_by
    
    # Get paginated results
    attachments = crud.tax_attachment.get_multi(
        db, 
        filter=filter_criteria,
        skip=skip, 
        limit=limit,
    )
    
    # Get total count
    total = crud.tax_attachment.count(db, **filter_criteria)
    
    return {
        "data": attachments,
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.put("/{attachment_id}", response_model=schemas.TaxAttachmentResponse)
def update_attachment(
    *,
    db: Session = Depends(deps.get_db),
    attachment_id: UUID,
    attachment_in: schemas.TaxAttachmentUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a tax return attachment
    """
    attachment = crud.tax_attachment.get(db, id=attachment_id)
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found",
        )
    
    # TODO: Add permission check to ensure user can update this attachment
    
    # Update the attachment
    updated_attachment = crud.tax_attachment.update(
        db, db_obj=attachment, obj_in=attachment_in
    )
    
    return {"data": updated_attachment}


@router.delete("/{attachment_id}", response_model=schemas.Msg)
def delete_attachment(
    *,
    db: Session = Depends(deps.get_db),
    attachment_id: UUID,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a tax return attachment
    """
    attachment = crud.tax_attachment.get(db, id=attachment_id)
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found",
        )
    
    # TODO: Add permission check to ensure user can delete this attachment
    
    # Delete the file from storage
    storage = get_storage_client()
    try:
        storage.delete_file(attachment.file_path)
    except Exception as e:
        # Log the error but continue with database deletion
        print(f"Error deleting file from storage: {str(e)}")
    
    # Delete the database record
    crud.tax_attachment.remove(db, id=attachment_id)
    
    return {"msg": "Attachment deleted successfully"}


@router.get("/summary", response_model=dict)
def get_attachments_summary(
    *,
    db: Session = Depends(deps.get_db),
    tax_return_id: UUID = None,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get summary statistics for tax return attachments
    """
    # TODO: Add permission check based on tax_return_id
    
    summary = crud.tax_attachment.get_attachments_summary(
        db, tax_return_id=tax_return_id
    )
    
    return summary
