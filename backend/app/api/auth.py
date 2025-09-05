from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from ..core.security import SecurityManager, LoginAttemptTracker, rate_limit_dependency
from ..core.config import settings

router = APIRouter(prefix="/auth", tags=["authentication"])

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    company_name: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class RefreshTokenRequest(BaseModel):
    refresh_token: str

@router.post("/login", response_model=Token, dependencies=[Depends(rate_limit_dependency)])
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    """Secure login with rate limiting and lockout protection"""
    
    # Check if account is locked out
    if LoginAttemptTracker.is_locked_out(form_data.username):
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"Account locked due to too many failed attempts. Try again in {settings.LOCKOUT_DURATION_MINUTES} minutes."
        )
    
    # Authenticate user (implement your user authentication logic)
    user = authenticate_user(form_data.username, form_data.password)
    
    if not user:
        LoginAttemptTracker.record_failed_attempt(form_data.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Clear failed attempts on successful login
    LoginAttemptTracker.clear_failed_attempts(form_data.username)
    
    # Create tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = SecurityManager.create_access_token(
        data={"sub": str(user["id"]), "email": user["email"]},
        expires_delta=access_token_expires
    )
    
    refresh_token = SecurityManager.create_refresh_token(
        data={"sub": str(user["id"]), "email": user["email"]}
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@router.post("/refresh", response_model=Token)
async def refresh_token(request: RefreshTokenRequest):
    """Refresh access token using refresh token"""
    
    try:
        payload = SecurityManager.verify_token(request.refresh_token, "refresh")
        user_id = payload.get("sub")
        email = payload.get("email")
        
        if not user_id or not email:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        # Create new access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = SecurityManager.create_access_token(
            data={"sub": user_id, "email": email},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "refresh_token": request.refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
    except HTTPException:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

@router.post("/logout")
async def logout(request: Request, current_user: dict = Depends(SecurityManager.get_current_user)):
    """Logout and blacklist token"""
    
    # Get token from Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        SecurityManager.blacklist_token(token)
    
    return {"message": "Successfully logged out"}

@router.post("/register", dependencies=[Depends(rate_limit_dependency)])
async def register(user_data: UserRegister):
    """User registration with validation"""
    
    # Check if user already exists
    if user_exists(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    hashed_password = SecurityManager.get_password_hash(user_data.password)
    
    # Create user (implement your user creation logic)
    user = create_user({
        "email": user_data.email,
        "hashed_password": hashed_password,
        "full_name": user_data.full_name,
        "company_name": user_data.company_name,
        "is_active": True
    })
    
    return {"message": "User registered successfully", "user_id": user["id"]}

# Mock functions - implement with your database
def authenticate_user(email: str, password: str):
    """Mock authentication - implement with your database"""
    # Mock user for demo
    mock_users = {
        "admin@paksa.com": {
            "id": 1,
            "email": "admin@paksa.com",
            "hashed_password": SecurityManager.get_password_hash("admin123"),
            "full_name": "Admin User",
            "is_active": True
        }
    }
    
    user = mock_users.get(email)
    if user and SecurityManager.verify_password(password, user["hashed_password"]):
        return user
    return None

def user_exists(email: str) -> bool:
    """Check if user exists - implement with your database"""
    return email == "admin@paksa.com"

def create_user(user_data: dict):
    """Create user - implement with your database"""
    return {"id": 1, **user_data}