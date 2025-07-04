from sqlalchemy import Column, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship

from .base import BaseModel, GUID

class UserPermission(BaseModel):
    ""
    Model representing permissions assigned directly to users.
    This allows for granting specific permissions to users outside of their role.
    """
    __tablename__ = "user_permissions"
    
    user_id = Column(GUID(), ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    permission_name = Column(String(100), ForeignKey('permissions.name', ondelete='CASCADE'), primary_key=True)
    
    # Additional metadata
    granted_by = Column(GUID(), ForeignKey('users.id'))
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    permission = relationship("Permission", foreign_keys=[permission_name])
    granter = relationship("User", foreign_keys=[granted_by])
    
    @property
    def is_active(self) -> bool:
        ""Check if the permission is currently active.""
        if self.expires_at:
            from datetime import datetime
            return datetime.utcnow() < self.expires_at
        return True
    
    def __repr__(self) -> str:
        return f"<UserPermission(user_id={self.user_id}, permission='{self.permission_name}')>"

class RolePermission(BaseModel):
    ""
    Model representing permissions associated with roles.
    This creates a many-to-many relationship between roles and permissions.
    """
    __tablename__ = "role_permissions"
    
    role_id = Column(GUID(), ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)
    permission_name = Column(String(100), ForeignKey('permissions.name', ondelete='CASCADE'), primary_key=True)
    
    # Relationships
    role = relationship("Role", back_populates="permissions")
    permission = relationship("Permission", back_populates="roles")
    
    def __repr__(self) -> str:
        return f"<RolePermission(role_id={self.role_id}, permission='{self.permission_name}')>"

class Permission(BaseModel):
    ""
    Model representing individual permissions in the system.
    Permissions are granular actions that can be performed.
    """
    __tablename__ = "permissions"
    
    # Core permission identifier
    name = Column(String(100), primary_key=True)
    
    # Human-readable information
    description = Column(String(255), nullable=True)
    category = Column(String(50), nullable=False)  # e.g., 'user', 'finance', 'reporting'
    
    # Relationships
    users = relationship("UserPermission", back_populates="permission")
    roles = relationship("RolePermission", back_populates="permission")
    
    # System flag for built-in permissions
    is_system = Column(Boolean, default=False, nullable=False)
    
    @classmethod
    async def ensure_exists(cls, session, name: str, description: str, category: str, is_system: bool = False):
        ""Ensure a permission exists, create if it doesn't."""
        from sqlalchemy import select
        
        result = await session.execute(select(cls).where(cls.name == name))
        permission = result.scalars().first()
        
        if not permission:
            permission = cls(
                name=name,
                description=description,
                category=category,
                is_system=is_system
            )
            session.add(permission)
            await session.commit()
        
        return permission
    
    def __repr__(self) -> str:
        return f"<Permission(name='{self.name}', category='{self.category}')>"

# Permission categories and their descriptions
PERMISSION_CATEGORIES = {
    'system': 'System administration permissions',
    'user': 'User management permissions',
    'role': 'Role management permissions',
    'finance': 'Financial operations',
    'reporting': 'Reporting and analytics',
    'settings': 'System settings',
    'audit': 'Audit logs and history',
}

# System permissions that should always exist
SYSTEM_PERMISSIONS = [
    # System permissions
    ('system.admin', 'Full system access', 'system', True),
    ('system.settings.view', 'View system settings', 'system', False),
    ('system.settings.edit', 'Edit system settings', 'system', False),
    
    # User permissions
    ('user.create', 'Create users', 'user', False),
    ('user.read', 'View users', 'user', False),
    ('user.update', 'Edit users', 'user', False),
    ('user.delete', 'Delete users', 'user', False),
    ('user.impersonate', 'Impersonate users', 'user', False),
    
    # Role permissions
    ('role.create', 'Create roles', 'role', False),
    ('role.read', 'View roles', 'role', False),
    ('role.update', 'Edit roles', 'role', False),
    ('role.delete', 'Delete roles', 'role', False),
    ('role.assign', 'Assign roles to users', 'role', False),
    
    # Finance permissions
    ('finance.transaction.create', 'Create transactions', 'finance', False),
    ('finance.transaction.approve', 'Approve transactions', 'finance', False),
    ('finance.transaction.void', 'Void transactions', 'finance', False),
    ('finance.report.view', 'View financial reports', 'finance', False),
    ('finance.report.export', 'Export financial data', 'finance', False),
    
    # Audit permissions
    ('audit.logs.view', 'View audit logs', 'audit', False),
    ('audit.logs.export', 'Export audit logs', 'audit', False),
]
