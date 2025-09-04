"""
Enhanced Authentication API with complete security features
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import timedelta
from app.core.database import get_db
from app.core.auth_enhanced import AuthService, PasswordPolicy, get_current_user
from app.models.user import User

router = APIRouter()

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    company: Optional[str] = None

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Enhanced login with proper JWT tokens"""
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user or not AuthService.verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is disabled"
        )
    
    # Create tokens
    access_token_expires = timedelta(hours=8 if request.remember_me else 1)
    access_token = AuthService.create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role},
        expires_delta=access_token_expires
    )
    refresh_token = AuthService.create_refresh_token(str(user.id))
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=int(access_token_expires.total_seconds()),
        user={
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
            "is_admin": user.role in ["admin", "super_admin"],
            "permissions": ["*"] if user.role == "super_admin" else []
        }
    )

@router.post("/register")
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """User registration with password validation"""
    # Check if user exists
    if db.query(User).filter(User.email == request.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate password
    password_check = PasswordPolicy.validate_password(request.password)
    if not password_check["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Password does not meet requirements", "errors": password_check["errors"]}
        )
    
    # Create user
    user = User(
        email=request.email,
        hashed_password=AuthService.get_password_hash(request.password),
        first_name=request.first_name,
        last_name=request.last_name,
        role="viewer",  # Default role
        is_active=True
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {"message": "User registered successfully", "user_id": str(user.id)}

@router.post("/change-password")
async def change_password(
    request: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    if not AuthService.verify_password(request.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    password_check = PasswordPolicy.validate_password(request.new_password)
    if not password_check["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "New password does not meet requirements", "errors": password_check["errors"]}
        )
    
    current_user.hashed_password = AuthService.get_password_hash(request.new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}

@router.post("/refresh-token")
async def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    """Refresh access token"""
    try:
        payload = AuthService.verify_token(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="User not found or inactive")
        
        new_access_token = AuthService.create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role}
        )
        
        return {"access_token": new_access_token, "token_type": "bearer"}
        
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "last_login": current_user.last_login,
        "permissions": ["*"] if current_user.role == "super_admin" else []
    }

@router.post("/logout")
async def logout():
    """Logout user (client should remove tokens)"""
    return {"message": "Logged out successfully"}