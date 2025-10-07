from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt

router = APIRouter()

# Mock user data
MOCK_USERS = {
    "admin@paksa.com": {
        "id": "1",
        "email": "admin@paksa.com",
        "full_name": "Admin User",
        "password": "admin123",
        "is_active": True,
        "is_superuser": True,
        "created_at": "2024-01-01T00:00:00Z"
    },
    "user@paksa.com": {
        "id": "2", 
        "email": "user@paksa.com",
        "full_name": "Regular User",
        "password": "user123",
        "is_active": True,
        "is_superuser": False,
        "created_at": "2024-01-01T00:00:00Z"
    }
}

SECRET_KEY = "your-secret-key-here"

class LoginRequest(BaseModel):
    email: str
    password: str
    remember_me: bool = False

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

@router.post("/login", response_model=LoginResponse)
def login(credentials: LoginRequest):
    """Mock login endpoint"""
    user = MOCK_USERS.get(credentials.email)
    
    if not user or user["password"] != credentials.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create JWT token
    token_data = {
        "sub": user["email"],
        "user_id": user["id"],
        "exp": datetime.utcnow() + timedelta(hours=24 if credentials.remember_me else 8)
    }
    
    token = jwt.encode(token_data, SECRET_KEY, algorithm="HS256")
    
    # Remove password from user data
    user_data = {k: v for k, v in user.items() if k != "password"}
    
    return LoginResponse(
        access_token=token,
        user=user_data
    )

@router.get("/me")
def get_current_user():
    """Mock current user endpoint"""
    return {
        "id": "1",
        "email": "admin@paksa.com", 
        "full_name": "Admin User",
        "is_active": True,
        "is_superuser": True,
        "created_at": "2024-01-01T00:00:00Z"
    }