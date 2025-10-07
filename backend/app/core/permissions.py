"""
Advanced permission system for enterprise-level access control.
"""
from enum import Enum
from typing import List, Optional, Set, Dict, Any
from functools import wraps
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User


class Permission(str, Enum):
    """System permissions."""
    
    # Generic permissions
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    
    # General Ledger
    GL_READ = "gl:read"
    GL_WRITE = "gl:write"
    GL_DELETE = "gl:delete"
    GL_APPROVE = "gl:approve"
    GL_POST = "gl:post"
    GL_CLOSE_PERIOD = "gl:close_period"
    
    # Accounts Payable
    AP_READ = "ap:read"
    AP_WRITE = "ap:write"
    AP_DELETE = "ap:delete"
    AP_APPROVE = "ap:approve"
    AP_PAYMENT_CREATE = "ap:payment_create"
    AP_PAYMENT_APPROVE = "ap:payment_approve"
    
    # Accounts Receivable
    AR_READ = "ar:read"
    AR_WRITE = "ar:write"
    AR_DELETE = "ar:delete"
    AR_INVOICE_CREATE = "ar:invoice_create"
    AR_PAYMENT_PROCESS = "ar:payment_process"
    AR_CREDIT_MEMO = "ar:credit_memo"
    
    # Budget Management
    BUDGET_READ = "budget:read"
    BUDGET_WRITE = "budget:write"
    BUDGET_DELETE = "budget:delete"
    BUDGET_APPROVE = "budget:approve"
    BUDGET_ALLOCATE = "budget:allocate"
    
    # Cash Management
    CASH_READ = "cash:read"
    CASH_WRITE = "cash:write"
    CASH_RECONCILE = "cash:reconcile"
    CASH_TRANSFER = "cash:transfer"
    
    # Inventory
    INVENTORY_READ = "inventory:read"
    INVENTORY_WRITE = "inventory:write"
    INVENTORY_DELETE = "inventory:delete"
    INVENTORY_ADJUST = "inventory:adjust"
    INVENTORY_TRANSFER = "inventory:transfer"
    
    # Payroll
    PAYROLL_READ = "payroll:read"
    PAYROLL_WRITE = "payroll:write"
    PAYROLL_PROCESS = "payroll:process"
    PAYROLL_APPROVE = "payroll:approve"
    
    # Tax Management
    TAX_READ = "tax:read"
    TAX_WRITE = "tax:write"
    TAX_FILE = "tax:file"
    TAX_APPROVE = "tax:approve"
    
    # Fixed Assets
    ASSETS_READ = "assets:read"
    ASSETS_WRITE = "assets:write"
    ASSETS_DELETE = "assets:delete"
    ASSETS_DEPRECIATE = "assets:depreciate"
    
    # Reports
    REPORTS_READ = "reports:read"
    REPORTS_GENERATE = "reports:generate"
    REPORTS_EXPORT = "reports:export"
    REPORTS_SCHEDULE = "reports:schedule"
    
    # HRM
    HRM_READ = "hrm:read"
    HRM_WRITE = "hrm:write"
    HRM_DELETE = "hrm:delete"
    HRM_PAYROLL = "hrm:payroll"
    
    # System Administration
    ADMIN_READ = "admin:read"
    ADMIN_WRITE = "admin:write"
    ADMIN_USER_MANAGE = "admin:user_manage"
    ADMIN_SYSTEM_CONFIG = "admin:system_config"
    ADMIN_BACKUP = "admin:backup"
    ADMIN_AUDIT = "admin:audit"
    
    # Super Admin
    SUPER_ADMIN = "super_admin:all"


class Role(str, Enum):
    """System roles with predefined permissions."""
    
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    FINANCE_MANAGER = "finance_manager"
    ACCOUNTANT = "accountant"
    AP_CLERK = "ap_clerk"
    AR_CLERK = "ar_clerk"
    PAYROLL_CLERK = "payroll_clerk"
    INVENTORY_MANAGER = "inventory_manager"
    BUDGET_ANALYST = "budget_analyst"
    AUDITOR = "auditor"
    VIEWER = "viewer"


# Role-Permission mapping
ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
    Role.SUPER_ADMIN: {Permission.SUPER_ADMIN},
    
    Role.ADMIN: {
        Permission.READ, Permission.WRITE, Permission.DELETE,
        Permission.GL_READ, Permission.GL_WRITE, Permission.GL_APPROVE,
        Permission.AP_READ, Permission.AP_WRITE, Permission.AP_APPROVE,
        Permission.AR_READ, Permission.AR_WRITE,
        Permission.BUDGET_READ, Permission.BUDGET_WRITE, Permission.BUDGET_APPROVE,
        Permission.CASH_READ, Permission.CASH_WRITE, Permission.CASH_RECONCILE,
        Permission.INVENTORY_READ, Permission.INVENTORY_WRITE,
        Permission.PAYROLL_READ, Permission.PAYROLL_WRITE,
        Permission.TAX_READ, Permission.TAX_WRITE,
        Permission.ASSETS_READ, Permission.ASSETS_WRITE,
        Permission.REPORTS_READ, Permission.REPORTS_GENERATE, Permission.REPORTS_EXPORT,
        Permission.HRM_READ, Permission.HRM_WRITE,
        Permission.ADMIN_READ, Permission.ADMIN_WRITE,
    },
    
    Role.FINANCE_MANAGER: {
        Permission.GL_READ, Permission.GL_WRITE, Permission.GL_APPROVE, Permission.GL_POST,
        Permission.AP_READ, Permission.AP_WRITE, Permission.AP_APPROVE,
        Permission.AR_READ, Permission.AR_WRITE,
        Permission.BUDGET_READ, Permission.BUDGET_WRITE, Permission.BUDGET_APPROVE,
        Permission.CASH_READ, Permission.CASH_WRITE, Permission.CASH_RECONCILE,
        Permission.TAX_READ, Permission.TAX_WRITE, Permission.TAX_APPROVE,
        Permission.ASSETS_READ, Permission.ASSETS_WRITE,
        Permission.REPORTS_READ, Permission.REPORTS_GENERATE, Permission.REPORTS_EXPORT,
    },
    
    Role.ACCOUNTANT: {
        Permission.GL_READ, Permission.GL_WRITE,
        Permission.AP_READ, Permission.AP_WRITE,
        Permission.AR_READ, Permission.AR_WRITE,
        Permission.BUDGET_READ,
        Permission.CASH_READ, Permission.CASH_WRITE,
        Permission.TAX_READ, Permission.TAX_WRITE,
        Permission.ASSETS_READ, Permission.ASSETS_WRITE,
        Permission.REPORTS_READ, Permission.REPORTS_GENERATE,
    },
    
    Role.AP_CLERK: {
        Permission.AP_READ, Permission.AP_WRITE,
        Permission.GL_READ,
        Permission.REPORTS_READ,
    },
    
    Role.AR_CLERK: {
        Permission.AR_READ, Permission.AR_WRITE,
        Permission.GL_READ,
        Permission.REPORTS_READ,
    },
    
    Role.PAYROLL_CLERK: {
        Permission.PAYROLL_READ, Permission.PAYROLL_WRITE,
        Permission.HRM_READ,
        Permission.REPORTS_READ,
    },
    
    Role.INVENTORY_MANAGER: {
        Permission.INVENTORY_READ, Permission.INVENTORY_WRITE,
        Permission.INVENTORY_ADJUST, Permission.INVENTORY_TRANSFER,
        Permission.REPORTS_READ, Permission.REPORTS_GENERATE,
    },
    
    Role.BUDGET_ANALYST: {
        Permission.BUDGET_READ, Permission.BUDGET_WRITE,
        Permission.GL_READ,
        Permission.REPORTS_READ, Permission.REPORTS_GENERATE,
    },
    
    Role.AUDITOR: {
        Permission.GL_READ, Permission.AP_READ, Permission.AR_READ,
        Permission.BUDGET_READ, Permission.CASH_READ,
        Permission.INVENTORY_READ, Permission.PAYROLL_READ,
        Permission.TAX_READ, Permission.ASSETS_READ,
        Permission.REPORTS_READ, Permission.REPORTS_GENERATE,
        Permission.ADMIN_AUDIT,
    },
    
    Role.VIEWER: {
        Permission.READ,
        Permission.GL_READ, Permission.AP_READ, Permission.AR_READ,
        Permission.BUDGET_READ, Permission.CASH_READ,
        Permission.INVENTORY_READ, Permission.PAYROLL_READ,
        Permission.TAX_READ, Permission.ASSETS_READ,
        Permission.REPORTS_READ,
    },
}


def get_user_permissions(user: User) -> Set[Permission]:
    """Get all permissions for a user based on their roles."""
    if user.is_superuser:
        return {Permission.SUPER_ADMIN}
    
    # For now, assign default role based on user type
    # In a real system, this would come from user-role assignments
    if user.is_superuser:
        return ROLE_PERMISSIONS.get(Role.SUPER_ADMIN, set())
    else:
        return ROLE_PERMISSIONS.get(Role.ADMIN, set())  # Default to admin for demo


def has_permission(user: User, permission: Permission) -> bool:
    """Check if user has specific permission."""
    user_permissions = get_user_permissions(user)
    
    # Super admin has all permissions
    if Permission.SUPER_ADMIN in user_permissions:
        return True
    
    return permission in user_permissions


def require_permission(permission: Permission):
    """Decorator to require specific permission."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user from dependencies
            current_user = kwargs.get('current_user')
            if not current_user:
                # Try to get from args (for dependency injection)
                for arg in args:
                    if isinstance(arg, User):
                        current_user = arg
                        break
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            if not has_permission(current_user, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission required: {permission.value}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_permissions(*permissions: Permission):
    """Decorator to require multiple permissions (all required)."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                for arg in args:
                    if isinstance(arg, User):
                        current_user = arg
                        break
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            missing_permissions = []
            for permission in permissions:
                if not has_permission(current_user, permission):
                    missing_permissions.append(permission.value)
            
            if missing_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing permissions: {', '.join(missing_permissions)}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_any_permission(*permissions: Permission):
    """Decorator to require any of the specified permissions."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                for arg in args:
                    if isinstance(arg, User):
                        current_user = arg
                        break
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            for permission in permissions:
                if has_permission(current_user, permission):
                    return await func(*args, **kwargs)
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"One of these permissions required: {', '.join([p.value for p in permissions])}"
            )
        return wrapper
    return decorator


# Dependency for FastAPI
def get_current_user_with_permission(permission: Permission):
    """FastAPI dependency to get current user with specific permission."""
    def dependency(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        if not has_permission(current_user, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission required: {permission.value}"
            )
        return current_user
    return dependency