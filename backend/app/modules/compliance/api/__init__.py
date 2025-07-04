"""
Paksa Financial System - Compliance API
Version: 1.0.0
Copyright (c) 2025 Paksa IT Solutions. All rights reserved.

This software is the proprietary information of Paksa IT Solutions.
Use is subject to license terms and restrictions.

API endpoints for compliance and security operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, TypeVar, Generic, Type, Any, Dict
from uuid import UUID
from pydantic.generics import GenericModel

from ....core.security import get_current_active_user, get_current_active_admin
from ....db.session import get_db
from ....schemas.user import UserInDB
from .. import schemas

# Create main router for all compliance endpoints
paksa_compliance_router = APIRouter()

# Include sub-routers
from . import audit, data_subject, security_policy, security_event, encryption  # noqa

# Register sub-routers with appropriate prefixes and tags
paksa_compliance_router.include_router(
    audit.router,
    prefix="/audit",
    tags=["audit"],
    dependencies=[Depends(get_current_active_admin)]
)

paksa_compliance_router.include_router(
    data_subject.router,
    prefix="/data-subject",
    tags=["data-subject"],
    dependencies=[Depends(get_current_active_user)]
)

paksa_compliance_router.include_router(
    security_policy.router,
    prefix="/security-policy",
    tags=["security-policy"],
    dependencies=[Depends(get_current_active_admin)]
)

paksa_compliance_router.include_router(
    security_event.router,
    prefix="/security-event",
    tags=["security-event"],
    dependencies=[Depends(get_current_active_admin)]
)

paksa_compliance_router.include_router(
    encryption.router,
    prefix="/encryption",
    tags=["encryption"],
    dependencies=[Depends(get_current_active_user)]
)

# Generic type variable for list responses
T = TypeVar('T')

class PaksaListResponse(GenericModel, Generic[T]):
    """Standardized list response model for Paksa API endpoints."""
    items: List[T]
    total: int
    skip: int = 0
    limit: int = 100
    has_more: bool = False
    
    def __init__(self, items: List[T], total: int, skip: int = 0, limit: int = 100):
        has_more = (skip + len(items)) < total if total > 0 else False
        super().__init__(
            items=items,
            total=total,
            skip=skip,
            limit=limit,
            has_more=has_more
        )
    
    @classmethod
    def from_list(
        cls, 
        items: List[T], 
        total: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> 'PaksaListResponse[T]':
        """Create a PaksaListResponse from a list of items."""
        return cls(items=items, total=total, skip=skip, limit=limit)

# Helper function to get the current user with required permissions
def paksa_get_current_user_with_permissions(
    required_permissions: List[str],
    current_user: UserInDB = Depends(get_current_active_user)
) -> UserInDB:
    """
    Check if the current user has the required permissions.
    
    Args:
        required_permissions: List of permission strings required
        current_user: The authenticated user
        
    Returns:
        The authenticated user if they have the required permissions
        
    Raises:
        HTTPException: If the user doesn't have the required permissions
    """
    # Get user's permissions (implementation depends on your permission system)
    user_permissions = getattr(current_user, "permissions", [])
    
    # Check if user has all required permissions
    if not all(perm in user_permissions for perm in required_permissions):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to access this resource",
        )
    return current_user

# Helper function to handle common error responses
def paksa_handle_error_response(
    error: Exception, 
    status_code: int = 400,
    context: Optional[Dict[str, Any]] = None
) -> HTTPException:
    """
    Create a standardized error response.
    
    Args:
        error: The exception that was raised
        status_code: HTTP status code to return
        context: Additional context to include in the error response
        
    Returns:
        HTTPException with standardized error format
    """
    error_detail = {
        "code": error.__class__.__name__,
        "message": str(error),
        "status": "error"
    }
    
    # Add additional error details if available
    if hasattr(error, 'details'):
        error_detail["details"] = error.details
    
    # Add context if provided
    if context:
        error_detail["context"] = context
    
    return HTTPException(
        status_code=status_code,
        detail=error_detail
    )

# Export all routers
__all__ = [
    'paksa_compliance_router',
    'PaksaListResponse',
    'paksa_get_current_user_with_permissions',
    'paksa_handle_error_response'
]
