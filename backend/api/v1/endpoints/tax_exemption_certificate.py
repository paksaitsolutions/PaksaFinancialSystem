"""
API endpoints for managing tax exemption certificates.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request, Response, BackgroundTasks
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import date, datetime
import logging
import io
import os
from pathlib import Path

from ....services.pdf_service import pdf_service
from ....core.config import settings
from ....core.security import get_current_active_user
from ....models.user import User
from ....models.tax_exemption_certificate import TaxExemptionCertificate
from ....schemas.tax_exemption_certificate import (
    TaxExemptionCertificateCreate,
    TaxExemptionCertificateUpdate,
    TaxExemptionCertificate as TaxExemptionCertificateSchema,
    TaxExemptionCertificateInDB,
    TaxExemptionCertificateSearchResults,
    JurisdictionBase
)
from ....crud.tax_exemption_certificate import tax_exemption_certificate as crud_tax_exemption_certificate
from ....db.session import get_db
from sqlalchemy.orm import Session

from ....core.security import get_current_active_user, role_required
from ....models.user import User
from ....models.tax_exemption_certificate import TaxExemptionCertificate
from ....schemas.tax_exemption_certificate import (
    TaxExemptionCertificateCreate,
    TaxExemptionCertificateUpdate,
    TaxExemptionCertificate as TaxExemptionCertificateSchema,
    TaxExemptionCertificateInDB,
    TaxExemptionCertificateSearchResults,
    JurisdictionBase
)
from ....core.config import settings
from ....crud.tax_exemption_certificate import tax_exemption_certificate as crud_tax_exemption_certificate
from ....db.session import get_db
from sqlalchemy.orm import Session

router = APIRouter()
logger = logging.getLogger(__name__)

# Helper function to convert model to schema
def convert_to_schema(cert: TaxExemptionCertificate) -> TaxExemptionCertificateSchema:
    """Convert a TaxExemptionCertificate model to a Pydantic schema."""
    return TaxExemptionCertificateSchema(
        id=cert.id,
        certificate_number=cert.certificate_number,
        customer_id=cert.customer_id,
        customer_tax_id=cert.customer_tax_id,
        customer_name=cert.customer_name,
        exemption_type=cert.exemption_type,
        issuing_jurisdiction=cert.issuing_jurisdiction,
        issue_date=cert.issue_date,
        expiry_date=cert.expiry_date,
        is_active=cert.is_active,
        tax_codes=cert.tax_codes or [],
        jurisdictions=cert.jurisdictions or [],
        document_reference=cert.document_reference,
        notes=cert.notes,
        created_by=cert.created_by,
        updated_by=cert.updated_by,
        created_at=cert.created_at,
        updated_at=cert.updated_at,
        metadata=cert.metadata or {}
    )

@router.post(
    "/certificates/",
    response_model=TaxExemptionCertificateSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new tax exemption certificate",
    description="Create a new tax exemption certificate for a customer.",
    response_description="The created tax exemption certificate"
)
async def create_certificate(
    *,
    db: Session = Depends(get_db),
    certificate_in: TaxExemptionCertificateCreate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Create a new tax exemption certificate.
    
    This endpoint allows creating a new tax exemption certificate with the provided details.
    The certificate can be associated with specific tax codes and jurisdictions.
    """
    # Check if certificate number already exists
    existing_cert = crud_tax_exemption_certificate.get_by_certificate_number(
        db, certificate_number=certificate_in.certificate_number
    )
    if existing_cert:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A certificate with this number already exists."
        )
    
    # Create the certificate
    cert_data = certificate_in.dict()
    cert_data["created_by"] = current_user.id
    
    try:
        certificate = crud_tax_exemption_certificate.create(db, obj_in=cert_data)
        return convert_to_schema(certificate)
    except Exception as e:
        logger.error(f"Error creating tax exemption certificate: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the tax exemption certificate."
        )

@router.get(
    "/certificates/",
    response_model=TaxExemptionCertificateSearchResults,
    summary="List tax exemption certificates",
    description="List all tax exemption certificates with optional filtering.",
    response_description="A list of tax exemption certificates"
)
async def list_certificates(
    *,
    db: Session = Depends(get_db),
    customer_id: Optional[UUID] = None,
    tax_code: Optional[str] = None,
    country_code: Optional[str] = None,
    state_code: Optional[str] = None,
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    List tax exemption certificates with optional filtering.
    
    This endpoint returns a paginated list of tax exemption certificates.
    Results can be filtered by customer, tax code, jurisdiction, and active status.
    """
    try:
        certificates = crud_tax_exemption_certificate.get_active(
            db,
            customer_id=customer_id,
            tax_code=tax_code,
            country_code=country_code,
            state_code=state_code,
            is_active=is_active,
            skip=skip,
            limit=limit
        )
        
        total = crud_tax_exemption_certificate.count(
            db,
            customer_id=customer_id,
            tax_code=tax_code,
            country_code=country_code,
            state_code=state_code,
            is_active=is_active
        )
        
        return {
            "results": [convert_to_schema(cert) for cert in certificates],
            "total": total,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Error listing tax exemption certificates: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving tax exemption certificates."
        )

@router.get(
    "/certificates/{certificate_id}",
    response_model=TaxExemptionCertificateSchema,
    summary="Get a tax exemption certificate by ID",
    description="Get detailed information about a specific tax exemption certificate.",
    response_description="The requested tax exemption certificate"
)
async def get_certificate(
    *,
    db: Session = Depends(get_db),
    certificate_id: UUID,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get a specific tax exemption certificate by ID.
    
    This endpoint returns detailed information about a specific tax exemption certificate,
    including its validity period, associated tax codes, and jurisdictions.
    """
    certificate = crud_tax_exemption_certificate.get(db, id=certificate_id)
    if not certificate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tax exemption certificate not found."
        )
    
    return convert_to_schema(certificate)

@router.put(
    "/certificates/{certificate_id}",
    response_model=TaxExemptionCertificateSchema,
    summary="Update a tax exemption certificate",
    description="Update an existing tax exemption certificate.",
    response_description="The updated tax exemption certificate"
)
@role_required(["admin", "accountant"])
async def update_certificate(
    *,
    db: Session = Depends(get_db),
    certificate_id: UUID,
    certificate_in: TaxExemptionCertificateUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Update a tax exemption certificate.
    
    This endpoint allows updating the details of an existing tax exemption certificate,
    such as its validity period, associated tax codes, and jurisdictions.
    """
    certificate = crud_tax_exemption_certificate.get(db, id=certificate_id)
    if not certificate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tax exemption certificate not found."
        )
    
    # Check if updating certificate number would cause a conflict
    if certificate_in.certificate_number and \
       certificate_in.certificate_number != certificate.certificate_number:
        existing_cert = crud_tax_exemption_certificate.get_by_certificate_number(
            db, certificate_number=certificate_in.certificate_number
        )
        if existing_cert and existing_cert.id != certificate_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A certificate with this number already exists."
            )
    
    # Update the certificate
    update_data = certificate_in.dict(exclude_unset=True)
    update_data["updated_by"] = current_user.id
    
    try:
        certificate = crud_tax_exemption_certificate.update(
            db, db_obj=certificate, obj_in=update_data
        )
        return convert_to_schema(certificate)
    except Exception as e:
        logger.error(f"Error updating tax exemption certificate: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the tax exemption certificate."
        )

@router.delete(
    "/certificates/{certificate_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a tax exemption certificate",
    description="Delete a tax exemption certificate by ID.",
    response_description="No content"
)
@role_required(["admin"])
async def delete_certificate(
    *,
    db: Session = Depends(get_db),
    certificate_id: UUID,
    current_user: User = Depends(get_current_active_user)
) -> None:
    """
    Delete a tax exemption certificate.
    
    This endpoint deletes a specific tax exemption certificate by ID.
    Note: This is a hard delete and cannot be undone.
    """
    certificate = crud_tax_exemption_certificate.get(db, id=certificate_id)
    if not certificate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tax exemption certificate not found."
        )
    
    try:
        crud_tax_exemption_certificate.remove(db, id=certificate_id)
        return None
    except Exception as e:
        logger.error(f"Error deleting tax exemption certificate: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the tax exemption certificate."
        )

@router.get(
    "/certificates/customer/{customer_id}",
    response_model=List[TaxExemptionCertificateSchema],
    summary="Get certificates for a customer",
    description="Get all tax exemption certificates for a specific customer.",
    response_description="List of tax exemption certificates for the customer"
)
async def get_customer_certificates(
    *,
    db: Session = Depends(get_db),
    customer_id: UUID,
    is_active: Optional[bool] = None,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get all tax exemption certificates for a specific customer.
    
    This endpoint returns all tax exemption certificates associated with a customer,
    with optional filtering by active status.
    """
    try:
        certificates = crud_tax_exemption_certificate.get_active(
            db,
            customer_id=customer_id,
            is_active=is_active
        )
        return [convert_to_schema(cert) for cert in certificates]
    except Exception as e:
        logger.error(f"Error retrieving customer certificates: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving customer certificates."
        )
