"""
Enhanced user management API endpoints.
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models
from app.api import deps
from app.core.db.session import get_db
from app.services.user.user_activity_service import UserActivityService

router = APIRouter()


def get_user_activity_service(db: Session = Depends(get_db)) -> UserActivityService:
    """Get user activity service instance."""
    return UserActivityService(db)


@router.get(
    "/{user_id}/login-history",
    summary="Get login history",
    description="Get login history for a user.",
    tags=["User Management"]
)
async def get_user_login_history(
    user_id: UUID,
    company_id: Optional[UUID] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Get login history for a user."""
    service = get_user_activity_service(db)
    
    history = service.get_login_history(user_id, company_id, limit)
    return history


@router.post(
    "/{user_id}/cross-company-access",
    summary="Grant cross-company access",
    description="Grant cross-company access to a user.",
    tags=["User Management"]
)
async def grant_cross_company_access(
    user_id: UUID,
    target_company_id: UUID,
    access_type: str = "read_only",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Grant cross-company access to a user."""
    service = get_user_activity_service(db)
    
    # Mock source company ID - in real implementation, get from current user context
    source_company_id = UUID("12345678-1234-5678-9012-123456789012")
    
    access = service.grant_cross_company_access(
        user_id=user_id,
        source_company_id=source_company_id,
        target_company_id=target_company_id,
        access_type=access_type,
        approved_by=current_user.id
    )
    
    return access


@router.post(
    "/companies/{company_id}/password-policy",
    summary="Create password policy",
    description="Create password policy for a company.",
    tags=["Password Policy"]
)
async def create_password_policy(
    company_id: UUID,
    policy_data: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Create password policy for a company."""
    service = get_user_activity_service(db)
    
    policy = service.create_password_policy(company_id, policy_data)
    return policy