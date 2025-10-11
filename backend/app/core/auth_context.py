"""
Authentication Context for Multi-Company, Multi-User, Multi-Role System
======================================================================
Provides current user, company, and role context throughout the application.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import User, Company, Role
from app.core.database import get_db
import jwt
from app.core.config import settings

security = HTTPBearer()

class AuthContext:
    """Authentication context containing user information."""
    
    def __init__(self, user: User):
        self.user = user
        
    @property
    def user_id(self) -> str:
        return str(self.user.id)
    
    @property
    def is_superuser(self) -> bool:
        return self.user.is_superuser
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission (simplified for current schema)."""
        return self.is_superuser  # For now, only superusers have all permissions

async def get_current_user(
    token: str = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token."""
    try:
        # Decode JWT token
        payload = jwt.decode(token.credentials, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Get user from database
        query = select(User).where(User.id == user_id, User.is_active == True)
        result = await db.execute(query)
        user = result.scalars().first()
        
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_auth_context(
    user: User = Depends(get_current_user)
) -> AuthContext:
    """Get authentication context with user information."""
    return AuthContext(user=user)

# Convenience functions for common use cases
async def get_current_user_id(auth: AuthContext = Depends(get_auth_context)) -> str:
    """Get current user ID."""
    return auth.user_id

def require_permission(permission: str):
    """Decorator to require specific permission."""
    def permission_checker(auth: AuthContext = Depends(get_auth_context)):
        if not auth.has_permission(permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required"
            )
        return auth
    return permission_checker

def require_superuser():
    """Decorator to require superuser access."""
    def superuser_checker(auth: AuthContext = Depends(get_auth_context)):
        if not auth.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Superuser access required"
            )
        return auth
    return superuser_checker