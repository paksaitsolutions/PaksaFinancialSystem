from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.core.security import verify_password, get_password_hash
from typing import Optional

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user by username/email and password."""
        result = await self.db.execute(
            select(User).where(
                (User.username == username) | (User.email == username),
                User.is_active == True
            )
        )
        user = result.scalars().first()
        
        if not user or not verify_password(password, user.hashed_password):
            return None
        
        return user
    
    async def create_user(self, user_data: dict) -> User:
        """Create a new user."""
        user = User(
            email=user_data['email'],
            username=user_data.get('username'),
            first_name=user_data.get('first_name'),
            last_name=user_data.get('last_name'),
            hashed_password=get_password_hash(user_data['password']),
            tenant_id=user_data.get('tenant_id'),
            is_active=True,
            is_verified=True
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()