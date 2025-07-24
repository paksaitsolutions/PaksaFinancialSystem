"""
RBAC service for managing roles, permissions, and access control.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.rbac import Role, Permission, user_roles, role_permissions
from app.models.user import User
from app.core.exceptions import NotFoundException, ValidationException


class RBACService:
    """Service for managing RBAC operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_permission(self, permission_data: Dict[str, Any], created_by: UUID) -> Permission:
        """Create a new permission."""
        permission = Permission(
            name=permission_data['name'],
            code=permission_data['code'],
            description=permission_data.get('description'),
            resource=permission_data['resource'],
            action=permission_data['action'],
            created_by=created_by,
            updated_by=created_by
        )
        
        self.db.add(permission)
        self.db.commit()
        self.db.refresh(permission)
        
        return permission
    
    def create_role(self, role_data: Dict[str, Any], created_by: UUID) -> Role:
        """Create a new role."""
        role = Role(
            name=role_data['name'],
            code=role_data['code'],
            description=role_data.get('description'),
            is_active=role_data.get('is_active', True),
            created_by=created_by,
            updated_by=created_by
        )
        
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        
        return role
    
    def assign_permission_to_role(self, role_id: UUID, permission_id: UUID) -> Role:
        """Assign a permission to a role."""
        role = self.get_role(role_id)
        permission = self.get_permission(permission_id)
        
        if not role:
            raise NotFoundException(f"Role {role_id} not found")
        if not permission:
            raise NotFoundException(f"Permission {permission_id} not found")
        
        if permission not in role.permissions:
            role.permissions.append(permission)
            self.db.commit()
        
        return role
    
    def assign_role_to_user(self, user_id: UUID, role_id: UUID) -> User:
        """Assign a role to a user."""
        user = self.db.query(User).filter(User.id == user_id).first()
        role = self.get_role(role_id)
        
        if not user:
            raise NotFoundException(f"User {user_id} not found")
        if not role:
            raise NotFoundException(f"Role {role_id} not found")
        
        if role not in user.roles:
            user.roles.append(role)
            self.db.commit()
        
        return user
    
    def check_permission(self, user_id: UUID, resource: str, action: str) -> bool:
        """Check if a user has permission for a specific resource and action."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        for role in user.roles:
            if not role.is_active:
                continue
                
            for permission in role.permissions:
                if permission.resource == resource and permission.action == action:
                    return True
        
        return False
    
    def get_user_permissions(self, user_id: UUID) -> List[Permission]:
        """Get all permissions for a user."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return []
        
        permissions = []
        for role in user.roles:
            if role.is_active:
                permissions.extend(role.permissions)
        
        return list(set(permissions))
    
    def get_role(self, role_id: UUID) -> Optional[Role]:
        """Get a role by ID."""
        return self.db.query(Role).filter(Role.id == role_id).first()
    
    def get_permission(self, permission_id: UUID) -> Optional[Permission]:
        """Get a permission by ID."""
        return self.db.query(Permission).filter(Permission.id == permission_id).first()
    
    def list_roles(self, skip: int = 0, limit: int = 100) -> List[Role]:
        """List all roles."""
        return self.db.query(Role).offset(skip).limit(limit).all()
    
    def list_permissions(self, skip: int = 0, limit: int = 100) -> List[Permission]:
        """List all permissions."""
        return self.db.query(Permission).offset(skip).limit(limit).all()
    
    def initialize_default_permissions(self):
        """Initialize default permissions for the system."""
        default_permissions = [
            {'name': 'Create Users', 'code': 'users.create', 'resource': 'users', 'action': 'create'},
            {'name': 'View Users', 'code': 'users.read', 'resource': 'users', 'action': 'read'},
            {'name': 'Update Users', 'code': 'users.update', 'resource': 'users', 'action': 'update'},
            {'name': 'Delete Users', 'code': 'users.delete', 'resource': 'users', 'action': 'delete'},
            {'name': 'Manage Roles', 'code': 'roles.manage', 'resource': 'roles', 'action': 'manage'},
            {'name': 'View GL', 'code': 'gl.read', 'resource': 'gl', 'action': 'read'},
            {'name': 'Manage GL', 'code': 'gl.manage', 'resource': 'gl', 'action': 'manage'},
            {'name': 'View AP', 'code': 'ap.read', 'resource': 'ap', 'action': 'read'},
            {'name': 'Manage AP', 'code': 'ap.manage', 'resource': 'ap', 'action': 'manage'},
            {'name': 'View AR', 'code': 'ar.read', 'resource': 'ar', 'action': 'read'},
            {'name': 'Manage AR', 'code': 'ar.manage', 'resource': 'ar', 'action': 'manage'},
            {'name': 'View Payroll', 'code': 'payroll.read', 'resource': 'payroll', 'action': 'read'},
            {'name': 'Manage Payroll', 'code': 'payroll.manage', 'resource': 'payroll', 'action': 'manage'},
            {'name': 'View Reports', 'code': 'reports.read', 'resource': 'reports', 'action': 'read'},
            {'name': 'Create Reports', 'code': 'reports.create', 'resource': 'reports', 'action': 'create'},
        ]
        
        for perm_data in default_permissions:
            existing = self.db.query(Permission).filter(Permission.code == perm_data['code']).first()
            if not existing:
                permission = Permission(
                    name=perm_data['name'],
                    code=perm_data['code'],
                    resource=perm_data['resource'],
                    action=perm_data['action']
                )
                self.db.add(permission)
        
        self.db.commit()
    
    def initialize_default_roles(self):
        """Initialize default roles for the system."""
        default_roles = [
            {
                'name': 'Super Admin',
                'code': 'super_admin',
                'description': 'Full system access',
                'permissions': ['users.create', 'users.read', 'users.update', 'users.delete', 'roles.manage',
                              'gl.manage', 'ap.manage', 'ar.manage', 'payroll.manage', 'reports.create']
            },
            {
                'name': 'Finance Manager',
                'code': 'finance_manager',
                'description': 'Full financial module access',
                'permissions': ['gl.manage', 'ap.manage', 'ar.manage', 'reports.create']
            },
            {
                'name': 'Accountant',
                'code': 'accountant',
                'description': 'Basic accounting access',
                'permissions': ['gl.read', 'ap.read', 'ar.read', 'reports.read']
            },
            {
                'name': 'Payroll Manager',
                'code': 'payroll_manager',
                'description': 'Payroll management access',
                'permissions': ['payroll.manage', 'reports.read']
            },
            {
                'name': 'Viewer',
                'code': 'viewer',
                'description': 'Read-only access',
                'permissions': ['gl.read', 'ap.read', 'ar.read', 'payroll.read', 'reports.read']
            }
        ]
        
        for role_data in default_roles:
            existing = self.db.query(Role).filter(Role.code == role_data['code']).first()
            if not existing:
                role = Role(
                    name=role_data['name'],
                    code=role_data['code'],
                    description=role_data['description']
                )
                self.db.add(role)
                self.db.flush()
                
                for perm_code in role_data['permissions']:
                    permission = self.db.query(Permission).filter(Permission.code == perm_code).first()
                    if permission:
                        role.permissions.append(permission)
        
        self.db.commit()