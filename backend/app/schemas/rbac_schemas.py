"""
Schemas for RBAC operations.
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field


class PermissionBase(BaseModel):
    """Base schema for permission operations."""
    name: str = Field(..., description="Permission name")
    code: str = Field(..., description="Permission code")
    description: Optional[str] = Field(None, description="Permission description")
    resource: str = Field(..., description="Resource name")
    action: str = Field(..., description="Action name")


class PermissionCreate(PermissionBase):
    """Schema for creating permissions."""
    pass


class PermissionResponse(PermissionBase):
    """Schema for permission response."""
    id: UUID = Field(..., description="Permission ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        orm_mode = True


class RoleBase(BaseModel):
    """Base schema for role operations."""
    name: str = Field(..., description="Role name")
    code: str = Field(..., description="Role code")
    description: Optional[str] = Field(None, description="Role description")
    is_active: bool = Field(True, description="Whether role is active")


class RoleCreate(RoleBase):
    """Schema for creating roles."""
    permission_ids: List[UUID] = Field([], description="List of permission IDs to assign")


class RoleUpdate(BaseModel):
    """Schema for updating roles."""
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class RoleResponse(RoleBase):
    """Schema for role response."""
    id: UUID = Field(..., description="Role ID")
    permissions: List[PermissionResponse] = Field([], description="Role permissions")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        orm_mode = True


class UserRoleAssignment(BaseModel):
    """Schema for assigning roles to users."""
    user_id: UUID = Field(..., description="User ID")
    role_ids: List[UUID] = Field(..., description="List of role IDs to assign")


class PermissionCheck(BaseModel):
    """Schema for permission check requests."""
    resource: str = Field(..., description="Resource name")
    action: str = Field(..., description="Action name")


class PermissionCheckResponse(BaseModel):
    """Schema for permission check response."""
    has_permission: bool = Field(..., description="Whether user has permission")
    resource: str = Field(..., description="Resource name")
    action: str = Field(..., description="Action name")