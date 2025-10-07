"""
User model for authentication and authorization.
"""
from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime
import uuid
from app.core.database import Base
from app.core.security import verify_password


class User(Base):
    """User model."""
    
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    
    @classmethod
    def authenticate(cls, db: Session, email: str, password: str):
        """Authenticate user by email and password."""
        user = db.query(cls).filter(
            cls.email == email,
            cls.is_active == True
        ).first()

        if user and verify_password(password, user.hashed_password):
            # Update last login
            user.last_login = datetime.utcnow()
            db.commit()
            return user

        return None
    
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        return f"{self.first_name or ''} {self.last_name or ''}".strip()
    
    def __repr__(self):
        return f"<User {self.email}>"