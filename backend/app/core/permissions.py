"""
Permission system for API endpoints.
"""
from enum import Enum
from typing import List, Optional
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

class Permission(str, Enum):
    """System permissions."""
    # General
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"
    
    # Accounts Payable
    AP_READ = "ap:read"
    AP_WRITE = "ap:write"
    AP_DELETE = "ap:delete"
    AP_ADMIN = "ap:admin"
    
    # Accounts Receivable
    AR_READ = "ar:read"
    AR_WRITE = "ar:write"
    AR_DELETE = "ar:delete"
    AR_ADMIN = "ar:admin"
    
    # General Ledger
    GL_READ = "gl:read"
    GL_WRITE = "gl:write"
    GL_DELETE = "gl:delete"
    GL_ADMIN = "gl:admin"
    
    # Payroll
    PAYROLL_READ = "payroll:read"
    PAYROLL_WRITE = "payroll:write"
    PAYROLL_DELETE = "payroll:delete"
    PAYROLL_ADMIN = "payroll:admin"
    
    # Inventory
    INVENTORY_READ = "inventory:read"
    INVENTORY_WRITE = "inventory:write"
    INVENTORY_DELETE = "inventory:delete"
    INVENTORY_ADMIN = "inventory:admin"
    
    # Tax
    TAX_READ = "tax:read"
    TAX_WRITE = "tax:write"
    TAX_DELETE = "tax:delete"
    TAX_ADMIN = "tax:admin"
    
    # Reports
    REPORTS_READ = "reports:read"
    REPORTS_WRITE = "reports:write"
    
    # System Admin
    SYSTEM_ADMIN = "system:admin"

class Role(str, Enum):
    """System roles."""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MANAGER = "manager"
    ACCOUNTANT = "accountant"
    VIEWER = "viewer"

# Role-Permission mapping
ROLE_PERMISSIONS = {
    Role.SUPER_ADMIN: [p.value for p in Permission],
    Role.ADMIN: [
        Permission.READ, Permission.WRITE, Permission.DELETE,
        Permission.AP_READ, Permission.AP_WRITE, Permission.AP_DELETE,
        Permission.AR_READ, Permission.AR_WRITE, Permission.AR_DELETE,
        Permission.GL_READ, Permission.GL_WRITE, Permission.GL_DELETE,
        Permission.PAYROLL_READ, Permission.PAYROLL_WRITE, Permission.PAYROLL_DELETE,
        Permission.INVENTORY_READ, Permission.INVENTORY_WRITE, Permission.INVENTORY_DELETE,
        Permission.TAX_READ, Permission.TAX_WRITE, Permission.TAX_DELETE,
        Permission.REPORTS_READ, Permission.REPORTS_WRITE,
    ],
    Role.MANAGER: [
        Permission.READ, Permission.WRITE,
        Permission.AP_READ, Permission.AP_WRITE,
        Permission.AR_READ, Permission.AR_WRITE,
        Permission.GL_READ, Permission.GL_WRITE,
        Permission.PAYROLL_READ, Permission.PAYROLL_WRITE,
        Permission.INVENTORY_READ, Permission.INVENTORY_WRITE,
        Permission.TAX_READ, Permission.TAX_WRITE,
        Permission.REPORTS_READ,
    ],
    Role.ACCOUNTANT: [
        Permission.READ, Permission.WRITE,
        Permission.AP_READ, Permission.AP_WRITE,
        Permission.AR_READ, Permission.AR_WRITE,
        Permission.GL_READ, Permission.GL_WRITE,
        Permission.TAX_READ, Permission.TAX_WRITE,
        Permission.REPORTS_READ,
    ],
    Role.VIEWER: [
        Permission.READ,
        Permission.AP_READ,
        Permission.AR_READ,
        Permission.GL_READ,
        Permission.PAYROLL_READ,
        Permission.INVENTORY_READ,
        Permission.TAX_READ,
        Permission.REPORTS_READ,
    ],
}

def get_current_user_permissions() -> List[str]:
    """Get current user permissions (mock implementation)."""
    # In real implementation, this would decode JWT token and get user permissions
    return ROLE_PERMISSIONS[Role.ADMIN]  # Mock admin permissions

def require_permissions(required_permissions: List[Permission]):
    """Decorator to require specific permissions."""
    def permission_checker(credentials: HTTPAuthorizationCredentials = Depends(security)):
        user_permissions = get_current_user_permissions()
        
        for permission in required_permissions:
            if permission.value not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required: {permission.value}"
                )
        return True
    
    return permission_checker

def require_permission(permission: Permission):
    """Require a single permission."""
    return require_permissions([permission])