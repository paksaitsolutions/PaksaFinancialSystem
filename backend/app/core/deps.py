"""
FastAPI dependencies.

This module provides centralized dependency injection for the application.
"""
from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db as _get_db
from app.core.security import (
    get_current_user as _get_current_user,
    get_current_active_user as _get_current_active_user,
    get_current_superuser as _get_current_superuser
)
from app.models.user import User

security = HTTPBearer()

# Database dependency
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session dependency."""
    async for session in _get_db():
        yield session

# Authentication dependencies
get_current_user = _get_current_user
get_current_active_user = _get_current_active_user
get_current_superuser = _get_current_superuser

async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Get current admin user (legacy, prefer get_current_superuser)."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user
