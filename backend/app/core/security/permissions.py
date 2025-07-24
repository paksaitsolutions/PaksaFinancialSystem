"""
Permission decorators and utilities for RBAC.
"""
from functools import wraps
from typing import Callable

from fastapi import HTTPException, Depends, status
from sqlalchemy.orm import Session

from app.core.db.session import get_db
from app.api import deps
from app.models.user import User
from app.services.rbac.rbac_service import RBACService


def require_permission(resource: str, action: str):
    """
    Decorator to require specific permission for an endpoint.
    
    Args:
        resource: The resource being accessed (e.g., 'users', 'gl', 'ap')
        action: The action being performed (e.g., 'read', 'create', 'update', 'delete')
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract dependencies from kwargs
            current_user: User = kwargs.get('current_user')
            db: Session = kwargs.get('db')
            
            if not current_user or not db:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Missing required dependencies for permission check"
                )
            
            # Check permission
            rbac_service = RBACService(db)
            has_permission = rbac_service.check_permission(current_user.id, resource, action)
            
            if not has_permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required: {resource}.{action}"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def check_permission(user_id: str, resource: str, action: str, db: Session) -> bool:
    """
    Utility function to check if a user has a specific permission.
    
    Args:
        user_id: User ID
        resource: Resource name
        action: Action name
        db: Database session
        
    Returns:
        True if user has permission, False otherwise
    """
    rbac_service = RBACService(db)
    return rbac_service.check_permission(user_id, resource, action)