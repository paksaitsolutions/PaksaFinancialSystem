"""
RBAC (Role-Based Access Control) models.
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Text, Table
from sqlalchemy.orm import relationship

from .base import BaseModel, GUID


# Association tables for many-to-many relationships
user_roles = Table(
    'user_roles',
    BaseModel.metadata,
    Column('user_id', GUID(), ForeignKey('users.id'), primary_key=True),
    Column('role_id', GUID(), ForeignKey('roles.id'), primary_key=True)
)

role_permissions = Table(
    'role_permissions',
    BaseModel.metadata,
    Column('role_id', GUID(), ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', GUID(), ForeignKey('permissions.id'), primary_key=True)
)


class Permission(BaseModel):
    """
    Represents a permission in the system.
    """
    __tablename__ = "permissions"
    
    # Permission details
    name = Column(String(100), unique=True, nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    resource = Column(String(50), nullable=False)  # e.g., 'users', 'invoices', 'reports'
    action = Column(String(20), nullable=False)    # e.g., 'create', 'read', 'update', 'delete'
    
    # Relationships
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")
    
    def __repr__(self) -> str:
        return f"<Permission(code='{self.code}', resource='{self.resource}', action='{self.action}')>"


class Role(BaseModel):
    """
    Represents a role in the system.
    """
    __tablename__ = "roles"
    
    # Role details
    name = Column(String(100), unique=True, nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")
    
    def __repr__(self) -> str:
        return f"<Role(code='{self.code}', name='{self.name}')>"