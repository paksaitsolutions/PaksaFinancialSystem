"""
Security utilities including authentication and authorization.
"""
from datetime import datetime, timedelta
from typing import Any, Optional, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import ValidationError

from .models import User, Role, Permission
from .config import settings
from .database import AsyncSession, get_db
from .exceptions import (
    CredentialsException,
    InactiveUserException,
    InsufficientPermissionsException,
)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_PREFIX}/auth/login"
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate a password hash."""
    return pwd_context.hash(password)


def create_access_token(
    subject: Union[str, Any], 
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT access token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """Get the current authenticated user from the token."""
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise CredentialsException()
    except (JWTError, ValidationError):
        raise CredentialsException()
    
    user = await models.User.get(db, id=user_id)
    if user is None:
        raise CredentialsException()
    
    if not user.is_active:
        raise InactiveUserException()
    
    return user


async def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """Require that the current user is a superuser."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user


def has_permission(
    user: User, 
    permission: str, 
    resource: Optional[str] = None
) -> bool:
    """Check if a user has a specific permission."""
    # Superusers have all permissions
    if user.is_superuser:
        return True
    
    # Check role-based permissions
    if not hasattr(user, 'role') or not user.role:
        return False
    
    # Check if the role has the required permission
    if resource:
        required_permission = f"{resource}:{permission}"
        return any(
            p.name == required_permission 
            for p in user.role.permissions
        )
    
    return any(p.name == permission for p in user.role.permissions)


async def require_permission(
    permission: str,
    resource: Optional[str] = None,
    current_user: User = Depends(get_current_user),
) -> User:
    """Dependency to require a specific permission."""
    if not has_permission(current_user, permission, resource):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not enough permissions to {permission} {resource or 'this resource'}",
        )
    return current_user
