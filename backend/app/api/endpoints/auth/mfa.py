"""
MFA API endpoints.
"""
import json
from typing import Any, List
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.session import get_db
from app.core.api_response import success_response, error_response
from app.crud.auth.mfa import mfa_crud
from app.schemas.auth.mfa import (
    MFASetupRequest, MFASetupResponse, MFAVerifyRequest, 
    MFALoginRequest, MFAStatusResponse, MFADeviceResponse
)

router = APIRouter()

@router.post("/setup", response_model=MFASetupResponse)
async def setup_mfa(
    *,
    db: AsyncSession = Depends(get_db),
    request: Request,
    mfa_request: MFASetupRequest,
) -> Any:
    """Setup MFA device for user."""
    # Mock user ID - in real app, get from JWT token
    user_id = UUID("12345678-1234-5678-9012-123456789012")
    user_email = "user@example.com"
    
    try:
        device = await mfa_crud.create_device(
            db, user_id=user_id, device_data=mfa_request
        )
        
        response_data = {
            "device_id": device.id,
            "backup_codes": json.loads(device.backup_codes) if device.backup_codes else []
        }
        
        # Generate QR code for TOTP
        if device.device_type == "totp":
            response_data["secret_key"] = device.secret_key
            response_data["qr_code"] = await mfa_crud.generate_qr_code(device, user_email)
        
        return success_response(
            data=response_data,
            message="MFA device setup initiated",
            status_code=status.HTTP_201_CREATED
        )
    except Exception as e:
        return error_response(
            message=f"Failed to setup MFA: {str(e)}",
            status_code=status.HTTP_400_BAD_REQUEST
        )

@router.post("/verify")
async def verify_mfa_setup(
    *,
    db: AsyncSession = Depends(get_db),
    request: Request,
    verify_request: MFAVerifyRequest,
) -> Any:
    """Verify MFA device setup."""
    device = await mfa_crud.get_device(db, verify_request.device_id)
    if not device:
        return error_response(
            message="MFA device not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    # Verify code based on device type
    is_valid = False
    if device.device_type == "totp":
        is_valid = await mfa_crud.verify_totp_code(device, verify_request.code)
    
    # Log attempt
    await mfa_crud.log_attempt(
        db,
        user_id=device.user_id,
        device_id=device.id,
        attempt_type=device.device_type,
        code=verify_request.code,
        success=is_valid,
        ip_address=request.client.host
    )
    
    if is_valid:
        await mfa_crud.verify_device(db, device.id)
        return success_response(message="MFA device verified successfully")
    else:
        return error_response(
            message="Invalid verification code",
            status_code=status.HTTP_400_BAD_REQUEST
        )

@router.post("/authenticate")
async def authenticate_mfa(
    *,
    db: AsyncSession = Depends(get_db),
    request: Request,
    auth_request: MFALoginRequest,
) -> Any:
    """Authenticate with MFA during login."""
    devices = await mfa_crud.get_user_devices(db, auth_request.user_id)
    if not devices:
        return error_response(
            message="No MFA devices found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    # Try to verify code with any active device
    for device in devices:
        if not device.is_verified:
            continue
            
        is_valid = False
        attempt_type = device.device_type
        
        if device.device_type == "totp":
            is_valid = await mfa_crud.verify_totp_code(device, auth_request.code)
        
        # Try backup code if TOTP fails
        if not is_valid:
            is_valid = await mfa_crud.verify_backup_code(db, device, auth_request.code)
            attempt_type = "backup"
        
        # Log attempt
        await mfa_crud.log_attempt(
            db,
            user_id=device.user_id,
            device_id=device.id,
            attempt_type=attempt_type,
            code=auth_request.code,
            success=is_valid,
            ip_address=request.client.host
        )
        
        if is_valid:
            # Update last used
            device.last_used = datetime.utcnow()
            await db.commit()
            
            return success_response(
                data={"authenticated": True},
                message="MFA authentication successful"
            )
    
    return error_response(
        message="Invalid MFA code",
        status_code=status.HTTP_401_UNAUTHORIZED
    )

@router.get("/status", response_model=MFAStatusResponse)
async def get_mfa_status(
    *,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get user's MFA status."""
    # Mock user ID
    user_id = UUID("12345678-1234-5678-9012-123456789012")
    
    devices = await mfa_crud.get_user_devices(db, user_id)
    
    # Count remaining backup codes
    backup_codes_remaining = 0
    for device in devices:
        if device.backup_codes:
            backup_codes_remaining += len(json.loads(device.backup_codes))
    
    return success_response(
        data={
            "is_enabled": len(devices) > 0,
            "devices": devices,
            "backup_codes_remaining": backup_codes_remaining
        }
    )

@router.delete("/device/{device_id}")
async def disable_mfa_device(
    *,
    db: AsyncSession = Depends(get_db),
    device_id: UUID,
) -> Any:
    """Disable MFA device."""
    success = await mfa_crud.disable_device(db, device_id)
    if success:
        return success_response(message="MFA device disabled successfully")
    else:
        return error_response(
            message="MFA device not found",
            status_code=status.HTTP_404_NOT_FOUND
        )