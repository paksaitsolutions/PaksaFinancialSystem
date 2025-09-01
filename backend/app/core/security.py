"""
Security utilities: password hashing, JWT helpers, and FastAPI dependencies.
"""
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login", auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None,
    additional_claims: Optional[Dict[str, Any]] = None,
) -> str:
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=getattr(settings, "ACCESS_TOKEN_EXPIRE_MINUTES", 30)))
    to_encode: Dict[str, Any] = {"sub": str(subject), "exp": expire, "iat": datetime.utcnow(), "type": "access"}
    if additional_claims:
        to_encode.update(additional_claims)
    return jwt.encode(to_encode, getattr(settings, "SECRET_KEY", "dev-secret-key"), algorithm=getattr(settings, "ALGORITHM", "HS256"))


def decode_token(token: str) -> Dict[str, Any]:
    return jwt.decode(token, getattr(settings, "SECRET_KEY", "dev-secret-key"), algorithms=[getattr(settings, "ALGORITHM", "HS256")])


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db=Depends(get_db),
) -> User:
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = decode_token(token)
        sub = payload.get("sub")
        if not sub:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")
        # Try to fetch user by ID or email
        user = await User.get(db, id=sub) if hasattr(User, "get") else None
        if not user and hasattr(User, "get_by_email"):
            user = await User.get_by_email(db, email=sub)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Could not validate credentials")


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if getattr(current_user, "is_active", True) is False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user


def role_required(required_roles: list):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            current_user: Optional[User] = kwargs.get("current_user")
            roles = []
            if current_user is not None and hasattr(current_user, "roles"):
                roles = list(getattr(current_user, "roles", []) or [])
            if not any(r in roles for r in required_roles):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
            return await func(*args, **kwargs)

        return wrapper

    return decorator
