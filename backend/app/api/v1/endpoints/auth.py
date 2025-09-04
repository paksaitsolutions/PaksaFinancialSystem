from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import create_access_token
from app.models.user import User


router = APIRouter()


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/login")
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await User.authenticate(db, email=payload.email, password=payload.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(subject=str(user.id), additional_claims={"email": user.email})
    return {
        "access_token": token,
        "user": {
            "id": str(user.id),
            "email": user.email,
            "firstName": getattr(user, "first_name", "") or "",
            "lastName": getattr(user, "last_name", "") or "",
            "roles": ["admin"] if getattr(user, "is_superuser", False) else [],
            "permissions": [],
            "isAdmin": bool(getattr(user, "is_superuser", False)),
        },
    }

