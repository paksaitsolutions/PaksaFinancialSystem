"""
Encryption API endpoints.
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models
from app.api import deps
from app.core.db.session import get_db
from app.schemas.encryption_schemas import (
    EncryptedUserProfileResponse,
    EncryptedUserProfileCreate,
    EncryptionStatusResponse,
    EncryptDataRequest,
    EncryptDataResponse,
    DecryptDataRequest,
    DecryptDataResponse
)
from app.services.encryption.encryption_service import EncryptionManagementService

router = APIRouter()


def get_encryption_service(db: Session = Depends(get_db)) -> EncryptionManagementService:
    """Get an instance of the encryption service."""
    return EncryptionManagementService(db)


@router.post(
    "/user-profile/{user_id}",
    response_model=EncryptedUserProfileResponse,
    summary="Create/Update encrypted user profile",
    description="Create or update encrypted user profile with sensitive information.",
    tags=["Data Encryption"]
)
async def create_user_profile(
    user_id: str,
    profile: EncryptedUserProfileCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> EncryptedUserProfileResponse:
    """Create or update encrypted user profile."""
    service = get_encryption_service(db)
    
    try:
        encrypted_profile = service.encrypt_user_profile(user_id, profile.dict(exclude_unset=True))
        return encrypted_profile
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/user-profile/{user_id}",
    response_model=EncryptedUserProfileResponse,
    summary="Get encrypted user profile",
    description="Get decrypted user profile information.",
    tags=["Data Encryption"]
)
async def get_user_profile(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> EncryptedUserProfileResponse:
    """Get decrypted user profile."""
    service = get_encryption_service(db)
    
    profile = service.get_user_profile(user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )
    
    return profile


@router.get(
    "/status",
    response_model=EncryptionStatusResponse,
    summary="Get encryption status",
    description="Get current encryption status and statistics.",
    tags=["Data Encryption"]
)
async def get_encryption_status(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> EncryptionStatusResponse:
    """Get encryption status and statistics."""
    service = get_encryption_service(db)
    
    status_info = service.get_encryption_status()
    return EncryptionStatusResponse(**status_info)


@router.post(
    "/encrypt",
    response_model=EncryptDataResponse,
    summary="Encrypt data",
    description="Encrypt arbitrary data using the system encryption key.",
    tags=["Data Encryption"]
)
async def encrypt_data(
    request: EncryptDataRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> EncryptDataResponse:
    """Encrypt arbitrary data."""
    service = get_encryption_service(db)
    
    try:
        encrypted_data = service.encryption_service.encrypt(request.data)
        return EncryptDataResponse(encrypted_data=encrypted_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Encryption failed: {str(e)}"
        )


@router.post(
    "/decrypt",
    response_model=DecryptDataResponse,
    summary="Decrypt data",
    description="Decrypt data using the system encryption key.",
    tags=["Data Encryption"]
)
async def decrypt_data(
    request: DecryptDataRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> DecryptDataResponse:
    """Decrypt data."""
    service = get_encryption_service(db)
    
    try:
        decrypted_data = service.encryption_service.decrypt(request.encrypted_data)
        return DecryptDataResponse(decrypted_data=decrypted_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Decryption failed: {str(e)}"
        )