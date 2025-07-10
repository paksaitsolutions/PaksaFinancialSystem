from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import Boolean, Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import BaseModel, GUID

# Avoid circular imports
if TYPE_CHECKING:
    from .role import Role
    from .permission import UserPermission

class User(BaseModel):
    """User model for authentication and authorization."""
    __tablename__ = "users"
    
    # Basic information
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=True)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    
    # Authentication
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean(), default=True)
    is_verified = Column(Boolean(), default=False)
    is_superuser = Column(Boolean(), default=False)
    
    # Contact information
    phone_number = Column(String(20), nullable=True)
    profile_picture = Column(String(255), nullable=True)
    
    # Timestamps
    last_login = Column(DateTime(timezone=True), nullable=True)
    date_joined = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    role_id = Column(GUID(), ForeignKey('roles.id'), nullable=True)
    role = relationship("Role", back_populates="users")
    
    # User-specific settings
    preferences = Column(Text, nullable=True)  # JSON string for user preferences
    
    # Relationships for permissions
    permissions = relationship("UserPermission", back_populates="user")
    
    # Audit fields
    created_by = Column(GUID(), ForeignKey('users.id'), nullable=True)
    updated_by = Column(GUID(), ForeignKey('users.id'), nullable=True)
    
    # Self-referential relationship for created_by/updated_by
    created_users = relationship(
        "User",
        foreign_keys=[created_by],
        remote_side="User.id",
        backref="created_by_user"
    )
    updated_users = relationship(
        "User",
        foreign_keys=[updated_by],
        remote_side="User.id",
        backref="updated_by_user"
    )
    
    @property
    def full_name(self) -> str:
        """Return the full name of the user."""
        return f"{self.first_name or ''} {self.last_name or ''}".strip()
    
    @classmethod
    async def get_by_email(cls, db, email: str) -> Optional['User']:
        """Get a user by email."""
        from sqlalchemy import select
        result = await db.execute(select(cls).where(cls.email == email))
        return result.scalars().first()
    
    @classmethod
    async def get_by_username(cls, db, username: str) -> Optional['User']:
        """Get a user by username."""
        from sqlalchemy import select
        result = await db.execute(select(cls).where(cls.username == username))
        return result.scalars().first()
    
    @classmethod
    async def authenticate(
        cls, 
        db, 
        email: str, 
        password: str
    ) -> Optional['User']:
        """Authenticate a user by email and password."""
        from core.security import verify_password
        
        user = await cls.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"

# Create a separate model for email verification tokens
class EmailVerificationToken(BaseModel):
    """Model for email verification tokens."""
    __tablename__ = "email_verification_tokens"
    
    user_id = Column(GUID(), ForeignKey('users.id'), nullable=False, index=True)
    token = Column(String(255), nullable=False, unique=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False)
    
    # Relationship
    user = relationship("User", foreign_keys=[user_id])
    
    @property
    def is_expired(self) -> bool:
        """Check if the token is expired."""
        return datetime.utcnow() > self.expires_at
    
    @classmethod
    async def get_by_token(cls, db, token: str) -> Optional['EmailVerificationToken']:
        """Get a token by its value."""
        from sqlalchemy import select
        result = await db.execute(select(cls).where(cls.token == token))
        return result.scalars().first()

# Create a separate model for password reset tokens
class PasswordResetToken(BaseModel):
    """Model for password reset tokens."""
    __tablename__ = "password_reset_tokens"
    
    user_id = Column(GUID(), ForeignKey('users.id'), nullable=False, index=True)
    token = Column(String(255), nullable=False, unique=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False)
    
    # Relationship
    user = relationship("User", foreign_keys=[user_id])
    
    @property
    def is_expired(self) -> bool:
        """Check if the token is expired."""
        return datetime.utcnow() > self.expires_at
    
    @classmethod
    async def get_by_token(cls, db, token: str) -> Optional['PasswordResetToken']:
        """Get a token by its value."""
        from sqlalchemy import select
        result = await db.execute(select(cls).where(cls.token == token))
        return result.scalars().first()
