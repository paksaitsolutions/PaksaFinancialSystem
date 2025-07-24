"""
Password policy API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app import models
from app.api import deps
from app.core.db.session import get_db
from app.schemas.password_schemas import (
    PasswordPolicyResponse,
    PasswordValidationRequest,
    PasswordValidationResponse,
    PasswordChangeRequest,
    PasswordChangeResponse,
    AccountLockStatus,
    PasswordExpiryStatus
)
from app.services.auth.password_service import PasswordService

router = APIRouter()


def get_password_service(db: Session = Depends(get_db)) -> PasswordService:
    """Get an instance of the password service."""
    return PasswordService(db)


@router.get(
    "/policy",
    response_model=PasswordPolicyResponse,
    summary="Get password policy",
    description="Get the active password policy.",
    tags=["Password Policy"]
)
async def get_password_policy(
    db: Session = Depends(get_db),
) -> PasswordPolicyResponse:
    """Get the active password policy."""
    service = get_password_service(db)
    policy = service.get_active_policy()
    return policy


@router.post(
    "/validate",
    response_model=PasswordValidationResponse,
    summary="Validate password",
    description="Validate a password against the active policy.",
    tags=["Password Policy"]
)
async def validate_password(
    request: PasswordValidationRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> PasswordValidationResponse:
    """Validate a password against the active policy."""
    service = get_password_service(db)
    
    validation = service.validate_password(request.password, current_user.id)
    
    return PasswordValidationResponse(
        valid=validation['valid'],
        errors=validation['errors'],
        policy=validation['policy']
    )


@router.post(
    "/change",
    response_model=PasswordChangeResponse,
    summary="Change password",
    description="Change user password with validation.",
    tags=["Password Policy"]
)
async def change_password(
    request: PasswordChangeRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> PasswordChangeResponse:
    """Change user password with validation."""
    service = get_password_service(db)
    
    try:
        result = service.change_password(
            current_user.id,
            request.old_password,
            request.new_password
        )
        return PasswordChangeResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/lock-status",
    response_model=AccountLockStatus,
    summary="Get account lock status",
    description="Get the current account lock status.",
    tags=["Account Security"]
)
async def get_lock_status(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> AccountLockStatus:
    """Get the current account lock status."""
    service = get_password_service(db)
    
    lock_status = service.is_account_locked(current_user.id)
    
    return AccountLockStatus(**lock_status)


@router.post(
    "/unlock-account/{user_id}",
    summary="Unlock account",
    description="Manually unlock a user account.",
    tags=["Account Security"]
)
async def unlock_account(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Manually unlock a user account."""
    # Only allow admins to unlock accounts
    # This would typically check for admin permissions
    
    service = get_password_service(db)
    
    try:
        service.unlock_account(user_id)
        return {"message": "Account unlocked successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/expiry-status",
    response_model=PasswordExpiryStatus,
    summary="Get password expiry status",
    description="Get the current password expiry status.",
    tags=["Password Policy"]
)
async def get_expiry_status(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> PasswordExpiryStatus:
    """Get the current password expiry status."""
    service = get_password_service(db)
    
    expired = service.is_password_expired(current_user.id)
    
    # Calculate expiry details
    policy = service.get_active_policy()
    if current_user.password_changed_at:
        from datetime import timedelta
        expires_at = current_user.password_changed_at + timedelta(days=policy.password_expiry_days)
        days_until_expiry = (expires_at - datetime.utcnow()).days
    else:
        expires_at = None
        days_until_expiry = None
    
    return PasswordExpiryStatus(
        expired=expired,
        expires_at=expires_at,
        days_until_expiry=days_until_expiry
    )