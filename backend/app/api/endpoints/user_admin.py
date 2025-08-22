"""
User administration API endpoints.
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models
from app.api import deps
from app.core.db.session import get_db
from app.services.admin.user_admin_service import UserAdminService

router = APIRouter()


@router.post(
    "/users/{user_id}/provision",
    summary="Provision user",
    description="Provision a user for a company.",
    tags=["User Administration"]
)
async def provision_user(
    user_id: UUID,
    company_id: UUID,
    provision_type: str = "manual",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Provision a user for a company."""
    service = UserAdminService(db)
    
    provision = service.provision_user(
        user_id=user_id,
        company_id=company_id,
        provisioned_by=current_user.id,
        provision_type=provision_type
    )
    
    return provision


@router.post(
    "/users/{user_id}/deactivate",
    summary="Deactivate user",
    description="Deactivate a user.",
    tags=["User Administration"]
)
async def deactivate_user(
    user_id: UUID,
    company_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Deactivate a user."""
    service = UserAdminService(db)
    
    success = service.deactivate_user(user_id, company_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User provision not found"
        )
    
    return {"message": "User deactivated successfully"}


@router.post(
    "/settings",
    summary="Set system setting",
    description="Set a system setting.",
    tags=["System Settings"]
)
async def set_system_setting(
    key: str,
    value: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Set system setting."""
    service = UserAdminService(db)
    
    setting = service.set_system_setting(key, value)
    
    return setting


@router.get(
    "/settings/{key}",
    summary="Get system setting",
    description="Get a system setting.",
    tags=["System Settings"]
)
async def get_system_setting(
    key: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Get system setting."""
    service = UserAdminService(db)
    
    setting = service.get_system_setting(key)
    
    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Setting not found"
        )
    
    return setting