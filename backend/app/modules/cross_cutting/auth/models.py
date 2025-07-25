"""
Authentication and authorization models.
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


# Association table for many-to-many relationship between roles and permissions
role_permission = Table(
    'role_permission',
    Base.metadata,
    Column('role_id', PG_UUID(as_uuid=True), ForeignKey('role.id'), primary_key=True),
    Column('permission_id', PG_UUID(as_uuid=True), ForeignKey('permission.id'), primary_key=True),
)


class UserStatus(str, Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    SUSPENDED = 'suspended'
    PENDING = 'pending'


class User(Base):
    """User model for authentication and authorization."""
    __tablename__ = 'user'
    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Status and flags
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean(), default=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean(), default=False)
    status: Mapped[UserStatus] = mapped_column(String(20), default=UserStatus.PENDING)
    
    # Timestamps
    last_login_at: Mapped[Optional[datetime]]
    email_verified_at: Mapped[Optional[datetime]]
    
    # Relationships
    role_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('role.id'))
    role: Mapped[Optional['Role']] = relationship('Role', back_populates='users')
    
    # Audit fields
    created_by: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('user.id'))
    updated_by: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('user.id'))
    
    # Backrefs
    created_users: Mapped[List['User']] = relationship(
        'User', 
        remote_side=[id],
        foreign_keys=[created_by],
        backref='creator',
    )
    updated_users: Mapped[List['User']] = relationship(
        'User',
        remote_side=[id],
        foreign_keys=[updated_by],
        backref='updater',
    )
    
    def __repr__(self) -> str:
        return f'<User {self.email}>'
    
    @property
    def is_authenticated(self) -> bool:
        return self.is_active
    
    @property
    def is_admin(self) -> bool:
        return self.is_superuser


class Permission(Base):
    """Permission model for fine-grained access control."""
    __tablename__ = 'permission'
    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Relationships
    roles: Mapped[List['Role']] = relationship(
        'Role', 
        secondary=role_permission, 
        back_populates='permissions',
    )
    
    def __repr__(self) -> str:
        return f'<Permission {self.name}>'


class Role(Base):
    """Role model for grouping permissions."""
    __tablename__ = 'role'
    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255))
    is_default: Mapped[bool] = mapped_column(Boolean(), default=False)
    
    # Relationships
    permissions: Mapped[List[Permission]] = relationship(
        'Permission',
        secondary=role_permission,
        back_populates='roles',
    )
    users: Mapped[List[User]] = relationship('User', back_populates='role')
    
    def __repr__(self) -> str:
        return f'<Role {self.name}>'


class RefreshToken(Base):
    """Refresh token for JWT authentication."""
    __tablename__ = 'refresh_token'
    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    token: Mapped[str] = mapped_column(String(512), unique=True, index=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    user_agent: Mapped[Optional[str]] = mapped_column(String(255))
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))  # IPv6 max length
    
    # Relationships
    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('user.id'), nullable=False)
    user: Mapped[User] = relationship('User')
    
    @property
    def is_expired(self) -> bool:
        return datetime.utcnow() >= self.expires_at
    
    def __repr__(self) -> str:
        return f'<RefreshToken {self.token[:10]}...> for user {self.user_id}'


class AuditLog(Base):
    """Audit log for tracking user actions."""
    __tablename__ = 'audit_log'
    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    action: Mapped[str] = mapped_column(String(50), nullable=False)  # create, update, delete, login, etc.
    table_name: Mapped[str] = mapped_column(String(50), nullable=False)
    record_id: Mapped[Optional[str]]  # ID of the affected record
    old_values: Mapped[Optional[dict]]  # JSONB in database
    new_values: Mapped[Optional[dict]]  # JSONB in database
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Relationships
    user_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('user.id'))
    user: Mapped[Optional[User]] = relationship('User')
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f'<AuditLog {self.action} on {self.table_name} by {self.user_id}>'
