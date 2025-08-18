"""
Paksa Financial System - Encryption API Endpoints
Version: 1.0.0
Copyright (c) 2025 Paksa IT Solutions. All rights reserved.

This software is the proprietary information of Paksa IT Solutions.
Use is subject to license terms and restrictions.

API endpoints for encryption and key management operations.
"""

from typing import Dict, Any, Optional, List, Union
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Body, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

from ....core.security import get_current_active_admin, get_current_active_user
from ....db.session import get_db
from ....schemas.user import UserInDB
from .. import models, schemas, exceptions
from ..services import EncryptionService, AuditService

# Create router with dependencies
router = APIRouter(
    dependencies=[Depends(get_current_active_user)],
    responses={404: {"description": "Not found"}},
)

# Security scheme for API key authentication
api_key_scheme = HTTPBearer()

def paksa_get_encryption_service(db=Depends(get_db)) -> EncryptionService:
    """Dependency to get an instance of EncryptionService."""
    return EncryptionService(db)

def paksa_get_audit_service(db=Depends(get_db)) -> AuditService:
    """Dependency to get an instance of AuditService."""
    return AuditService(db)

class PaksaEncryptRequest(BaseModel):
    """Request model for encrypting data."""
    plaintext: str = Field(..., description="The plaintext data to encrypt")
    key_id: Optional[UUID] = Field(None, description="Optional key ID to use for encryption")
    context: Optional[Dict[str, str]] = Field(
        None, 
        description="Additional context for key derivation"
    )

class PaksaEncryptResponse(BaseModel):
    """Response model for encryption operations."""
    ciphertext: str = Field(..., description="The encrypted data")
    key_id: UUID = Field(..., description="The ID of the key used for encryption")
    algorithm: str = Field(..., description="The encryption algorithm used")
    iv: Optional[str] = Field(None, description="Initialization vector, if applicable")
    auth_tag: Optional[str] = Field(None, description="Authentication tag, if applicable")
    context: Optional[Dict[str, str]] = Field(None, description="Additional context")

class PaksaDecryptRequest(BaseModel):
    """Request model for decrypting data."""
    ciphertext: str = Field(..., description="The encrypted data to decrypt")
    key_id: Optional[UUID] = Field(None, description="The ID of the key to use for decryption")
    iv: Optional[str] = Field(None, description="Initialization vector, if applicable")
    auth_tag: Optional[str] = Field(None, description="Authentication tag, if applicable")
    context: Optional[Dict[str, str]] = Field(
        None, 
        description="Additional context for key derivation"
    )

class PaksaDecryptResponse(BaseModel):
    """Response model for decryption operations."""
    plaintext: str = Field(..., description="The decrypted data")
    key_id: UUID = Field(..., description="The ID of the key used for decryption")

@router.post("/encrypt", response_model=PaksaEncryptResponse)
async def paksa_encrypt_data(
    request: PaksaEncryptRequest,
    db=Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Encrypt data using the encryption service.
    
    Requires authentication and appropriate permissions.
    """
    try:
        encryption_service = EncryptionService(db)
        audit_service = AuditService(db)
        
        # Encrypt the data
        result = encryption_service.encrypt(
            plaintext=request.plaintext,
            key_id=str(request.key_id) if request.key_id else None,
            context=request.context
        )
        
        # Log the encryption operation
        audit_service.create_audit_log(
            action=models.AuditActionType.ENCRYPT,
            resource_type="EncryptionKey",
            resource_id=str(result['key_id']),
            user_id=current_user.id,
            username=current_user.username,
            details={
                "algorithm": result['algorithm'],
                "context_keys": list(request.context.keys()) if request.context else []
            }
        )
        
        return PaksaEncryptResponse(**result)
        
    except exceptions.EncryptionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to encrypt data: {str(e)}"
        )

@router.post("/decrypt", response_model=PaksaDecryptResponse)
async def paksa_decrypt_data(
    request: PaksaDecryptRequest,
    db=Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Decrypt data using the encryption service.
    
    Requires authentication and appropriate permissions.
    """
    try:
        encryption_service = EncryptionService(db)
        audit_service = AuditService(db)
        
        # Decrypt the data
        result = encryption_service.decrypt(
            ciphertext=request.ciphertext,
            key_id=str(request.key_id) if request.key_id else None,
            iv=request.iv,
            auth_tag=request.auth_tag,
            context=request.context
        )
        
        # Log the decryption operation
        audit_service.create_audit_log(
            action=models.AuditActionType.DECRYPT,
            resource_type="EncryptionKey",
            resource_id=result['key_id'],
            user_id=current_user.id,
            username=current_user.username,
            details={
                "context_keys": list(request.context.keys()) if request.context else []
            }
        )
        
        return PaksaDecryptResponse(**result)
        
    except exceptions.DecryptionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to decrypt data: {str(e)}"
        )

@router.post("/keys/generate", response_model=schemas.EncryptionKey)
async def paksa_generate_encryption_key(
    key_data: schemas.EncryptionKeyCreate,
    db=Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_admin)
):
    """
    Generate a new encryption key.
    
    Only accessible by administrators.
    """
    try:
        encryption_service = EncryptionService(db)
        audit_service = AuditService(db)
        
        # Generate the key
        key = encryption_service.generate_key(
            name=key_data.name,
            description=key_data.description,
            algorithm=key_data.algorithm,
            key_size=key_data.key_size,
            is_active=key_data.is_active,
            tags=key_data.tags,
            created_by=current_user.id
        )
        
        # Log the key generation
        audit_service.create_audit_log(
            action=models.AuditActionType.CREATE,
            resource_type="EncryptionKey",
            resource_id=str(key.id),
            user_id=current_user.id,
            username=current_user.username,
            details={
                "algorithm": key.algorithm,
                "key_size": key.key_size,
                "is_active": key.is_active
            }
        )
        
        return key
        
    except exceptions.EncryptionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate encryption key: {str(e)}"
        )

@router.get("/keys", response_model=List[schemas.EncryptionKey])
async def paksa_list_encryption_keys(
    is_active: Optional[bool] = None,
    algorithm: Optional[str] = None,
    tag: Optional[str] = None,
    db=Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_admin)
):
    """
    List all encryption keys with optional filtering.
    
    Only accessible by administrators.
    """
    try:
        encryption_service = EncryptionService(db)
        keys = encryption_service.list_keys(
            is_active=is_active,
            algorithm=algorithm,
            tag=tag
        )
        return keys
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to list encryption keys: {str(e)}"
        )

@router.get("/keys/{key_id}", response_model=schemas.EncryptionKey)
async def paksa_get_encryption_key(
    key_id: UUID,
    db=Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_admin)
):
    """
    Retrieve a specific encryption key by ID.
    
    Only accessible by administrators. The actual key material is not returned.
    """
    try:
        encryption_service = EncryptionService(db)
        key = encryption_service.get_key(key_id)
        return key
    except exceptions.KeyNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to fetch encryption key: {str(e)}"
        )

@router.put("/keys/{key_id}/rotate", response_model=schemas.EncryptionKey)
async def paksa_rotate_encryption_key(
    key_id: UUID,
    db=Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_admin)
):
    """
    Rotate an encryption key (generate a new version).
    
    Only accessible by administrators.
    """
    try:
        encryption_service = EncryptionService(db)
        audit_service = AuditService(db)
        
        # Rotate the key
        key = encryption_service.rotate_key(key_id, rotated_by=current_user.id)
        
        # Log the key rotation
        audit_service.create_audit_log(
            action=models.AuditActionType.UPDATE,
            resource_type="EncryptionKey",
            resource_id=str(key_id),
            user_id=current_user.id,
            username=current_user.username,
            details={
                "action": "rotated",
                "new_version": key.version,
                "algorithm": key.algorithm
            }
        )
        
        return key
        
    except exceptions.KeyNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except exceptions.EncryptionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to rotate encryption key: {str(e)}"
        )

@router.post("/keys/{key_id}/enable", response_model=schemas.EncryptionKey)
async def paksa_enable_encryption_key(
    key_id: UUID,
    db=Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_admin)
):
    """
    Enable an encryption key.
    
    Only accessible by administrators.
    """
    try:
        encryption_service = EncryptionService(db)
        audit_service = AuditService(db)
        
        # Enable the key
        key = encryption_service.enable_key(key_id, updated_by=current_user.id)
        
        # Log the key enablement
        audit_service.create_audit_log(
            action=models.AuditActionType.UPDATE,
            resource_type="EncryptionKey",
            resource_id=str(key_id),
            user_id=current_user.id,
            username=current_user.username,
            details={
                "action": "enabled",
                "algorithm": key.algorithm,
                "version": key.version
            }
        )
        
        return key
        
    except exceptions.KeyNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except exceptions.EncryptionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enable encryption key: {str(e)}"
        )

@router.post("/keys/{key_id}/disable", response_model=schemas.EncryptionKey)
async def paksa_disable_encryption_key(
    key_id: UUID,
    db=Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_admin)
):
    """
    Disable an encryption key.
    
    Only accessible by administrators. System keys cannot be disabled.
    """
    try:
        encryption_service = EncryptionService(db)
        audit_service = AuditService(db)
        
        # Disable the key
        key = encryption_service.disable_key(key_id, updated_by=current_user.id)
        
        # Log the key disablement
        audit_service.create_audit_log(
            action=models.AuditActionType.UPDATE,
            resource_type="EncryptionKey",
            resource_id=str(key_id),
            user_id=current_user.id,
            username=current_user.username,
            details={
                "action": "disabled",
                "algorithm": key.algorithm,
                "version": key.version
            }
        )
        
        return key
        
    except exceptions.KeyNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except exceptions.EncryptionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to disable encryption key: {str(e)}"
        )

@router.post("/hash", response_model=Dict[str, str])
async def paksa_generate_hash(
    plaintext: str = Body(..., embed=True),
    algorithm: str = "sha256",
    salt: Optional[str] = None,
    iterations: int = 100000,
    db=Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Generate a cryptographic hash of the provided data.
    
    Requires authentication. The hash is one-way and cannot be reversed.
    """
    try:
        encryption_service = EncryptionService(db)
        
        # Generate the hash
        result = encryption_service.generate_hash(
            plaintext=plaintext,
            algorithm=algorithm,
            salt=salt,
            iterations=iterations
        )
        
        # Note: We don't log hashing operations as they're not security-sensitive
        
        return {
            "hash": result,
            "algorithm": algorithm,
            "iterations": iterations,
            "salt_used": salt is not None
        }
        
    except exceptions.EncryptionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate hash: {str(e)}"
        )

@router.post("/verify-hash", response_model=bool)
async def paksa_verify_hash(
    plaintext: str = Body(..., embed=True),
    hashed_value: str = Body(..., embed=True),
    algorithm: str = "sha256",
    salt: Optional[str] = None,
    iterations: int = 100000,
    db=Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Verify if a plaintext value matches a hashed value.
    
    Requires authentication.
    """
    try:
        encryption_service = EncryptionService(db)
        
        # Verify the hash
        is_valid = encryption_service.verify_hash(
            plaintext=plaintext,
            hashed_value=hashed_value,
            algorithm=algorithm,
            salt=salt,
            iterations=iterations
        )
        
        return is_valid
        
    except exceptions.EncryptionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify hash: {str(e)}"
        )
