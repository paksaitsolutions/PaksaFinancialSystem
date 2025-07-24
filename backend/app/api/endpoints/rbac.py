"""
RBAC API endpoints.
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models
from app.api import deps
from app.core.db.session import get_db
from app.core.security.permissions import require_permission
from app.schemas.rbac_schemas import (
    PermissionCreate,
    PermissionResponse,
    RoleCreate,
    RoleUpdate,
    RoleResponse,
    UserRoleAssignment,
    PermissionCheck,
    PermissionCheckResponse
)
from app.services.rbac.rbac_service import RBACService

router = APIRouter()


def get_rbac_service(db: Session = Depends(get_db)) -> RBACService:
    """Get an instance of the RBAC service."""
    return RBACService(db)


@router.post(
    "/permissions",
    response_model=PermissionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create permission",
    description="Create a new permission.",
    tags=["Permissions"]
)
@require_permission("roles", "manage")
async def create_permission(
    permission: PermissionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> PermissionResponse:
    """Create a new permission."""
    service = get_rbac_service(db)
    
    try:
        return service.create_permission(permission.dict(), current_user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/permissions",
    response_model=List[PermissionResponse],
    summary="List permissions",
    description="List all permissions.",
    tags=["Permissions"]
)
@require_permission("roles", "manage")
async def list_permissions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> List[PermissionResponse]:
    """List all permissions."""
    service = get_rbac_service(db)
    return service.list_permissions(skip=skip, limit=limit)


@router.post(
    "/roles",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create role",
    description="Create a new role.",
    tags=["Roles"]
)
@require_permission("roles", "manage")
async def create_role(
    role: RoleCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> RoleResponse:
    """Create a new role."""
    service = get_rbac_service(db)
    
    try:
        created_role = service.create_role(role.dict(exclude={'permission_ids'}), current_user.id)
        
        # Assign permissions to role
        for permission_id in role.permission_ids:
            service.assign_permission_to_role(created_role.id, permission_id)
        
        return service.get_role(created_role.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/roles",
    response_model=List[RoleResponse],
    summary="List roles",
    description="List all roles.",
    tags=["Roles"]
)
@require_permission("roles", "manage")
async def list_roles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> List[RoleResponse]:
    """List all roles."""
    service = get_rbac_service(db)
    return service.list_roles(skip=skip, limit=limit)


@router.post(
    "/users/assign-roles",
    summary="Assign roles to user",
    description="Assign roles to a user.",
    tags=["User Roles"]
)
@require_permission("users", "update")
async def assign_roles_to_user(
    assignment: UserRoleAssignment,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Assign roles to a user."""
    service = get_rbac_service(db)
    
    try:
        for role_id in assignment.role_ids:
            service.assign_role_to_user(assignment.user_id, role_id)
        
        return {"message": "Roles assigned successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/check-permission",
    response_model=PermissionCheckResponse,
    summary="Check permission",
    description="Check if current user has a specific permission.",
    tags=["Permissions"]
)
async def check_permission(
    permission_check: PermissionCheck,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> PermissionCheckResponse:
    """Check if current user has a specific permission."""
    service = get_rbac_service(db)
    
    has_permission = service.check_permission(
        current_user.id,
        permission_check.resource,
        permission_check.action
    )
    
    return PermissionCheckResponse(
        has_permission=has_permission,
        resource=permission_check.resource,
        action=permission_check.action
    )


@router.post(
    "/initialize",
    summary="Initialize RBAC",
    description="Initialize default permissions and roles.",
    tags=["System"]
)
@require_permission("roles", "manage")
async def initialize_rbac(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Initialize default permissions and roles."""
    service = get_rbac_service(db)
    
    try:
        service.initialize_default_permissions()
        service.initialize_default_roles()
        
        return {"message": "RBAC initialized successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )