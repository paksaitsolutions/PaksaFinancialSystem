from typing import List, TYPE_CHECKING
from sqlalchemy import Column, String, Text, Boolean
from sqlalchemy.orm import relationship

from .base import BaseModel, GUID

# Avoid circular imports
if TYPE_CHECKING:
    from .user import User
    from .permission import RolePermission

class Role(BaseModel):
    """Role model for role-based access control (RBAC)."""
    __tablename__ = "roles"
    
    # Basic information
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Role settings
    is_default = Column(Boolean, default=False, nullable=False)
    is_system = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    users = relationship("User", back_populates="role")
    permissions = relationship("RolePermission", back_populates="role")
    
    @classmethod
    async def get_default_role(cls, db):
        """Get the default role."""
        from sqlalchemy import select
        result = await db.execute(select(cls).where(cls.is_default == True))
        return result.scalars().first()
    
    @classmethod
    async def get_system_roles(cls, db):
        """Get all system roles."""
        from sqlalchemy import select
        result = await db.execute(select(cls).where(cls.is_system == True))
        return result.scalars().all()
    
    def has_permission(self, permission_name: str) -> bool:
        """Check if the role has a specific permission."""
        return any(
            perm.permission.name == permission_name 
            for perm in self.permissions
        )
    
    def __repr__(self) -> str:
        return f"<Role(id={self.id}, name='{self.name}')>"

class Permission(BaseModel):
    """Permission model for fine-grained access control."""
    __tablename__ = "permissions"
    
    # Basic information
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Category for grouping related permissions
    category = Column(String(50), nullable=False, index=True)
    
    # Module/feature this permission belongs to
    module = Column(String(50), nullable=True, index=True)
    
    # Relationships
    role_permissions = relationship("RolePermission", back_populates="permission")
    user_permissions = relationship("UserPermission", back_populates="permission")
    
    @classmethod
    async def get_by_name(cls, db, name: str):
        """Get a permission by name."""
        from sqlalchemy import select
        result = await db.execute(select(cls).where(cls.name == name))
        return result.scalars().first()
    
    @classmethod
    async def get_by_module(cls, db, module: str):
        """Get all permissions for a module."""
        from sqlalchemy import select
        result = await db.execute(select(cls).where(cls.module == module))
        return result.scalars().all()
    
    def __repr__(self) -> str:
        return f"<Permission(id={self.id}, name='{self.name}')>"

class RolePermission(BaseModel):
    """Many-to-many relationship between roles and permissions."""
    __tablename__ = "role_permissions"
    
    role_id = Column(GUID(), ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)
    permission_id = Column(GUID(), ForeignKey('permissions.id', ondelete='CASCADE'), primary_key=True)
    
    # Additional metadata
    created_by = Column(GUID(), ForeignKey('users.id'), nullable=True)
    
    # Relationships
    role = relationship("Role", back_populates="permissions")
    permission = relationship("Permission", back_populates="role_permissions")
    
    def __repr__(self) -> str:
        return f"<RolePermission(role_id={self.role_id}, permission_id={self.permission_id})>"

class UserPermission(BaseModel):
    """Many-to-many relationship between users and permissions."""
    __tablename__ = "user_permissions"
    
    user_id = Column(GUID(), ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    permission_id = Column(GUID(), ForeignKey('permissions.id', ondelete='CASCADE'), primary_key=True)
    
    # Additional metadata
    granted_by = Column(GUID(), ForeignKey('users.id'), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="permissions", foreign_keys=[user_id])
    permission = relationship("Permission", back_populates="user_permissions")
    
    @property
    def is_expired(self) -> bool:
        """Check if the permission is expired."""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    def __repr__(self) -> str:
        return f"<UserPermission(user_id={self.user_id}, permission_id={self.permission_id})>"
