from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db.session import get_db
from app.models.core_models import User
from app.core.security import verify_password, create_access_token
from sqlalchemy import select

router = APIRouter()

class LoginRequest(BaseModel):
    username: str  # Can be username or email
    password: str
    remember_me: bool = False

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate user with username or email"""
    # Try to find user by username or email
    result = await db.execute(
        select(User).where(
            (User.username == credentials.username) | 
            (User.email == credentials.username)
        )
    )
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled"
        )
    
    # Create JWT token
    access_token = create_access_token(
        data={"sub": user.email, "user_id": str(user.id)},
        expires_delta=timedelta(hours=24 if credentials.remember_me else 8)
    )
    
    user_data = {
        "id": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
        "created_at": user.created_at.isoformat()
    }
    
    return LoginResponse(
        access_token=access_token,
        user=user_data
    )

@router.get("/me")
async def get_current_user(db: AsyncSession = Depends(get_db)):
    """Get current authenticated user from database"""
    # This would normally use the current user from JWT token
    # For now, return the admin user from database
    result = await db.execute(select(User).where(User.email == "admin@paksa.com"))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
        "created_at": user.created_at.isoformat()
    }