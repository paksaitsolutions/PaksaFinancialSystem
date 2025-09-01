"""
Unified SQLAlchemy base models for Paksa Financial System.
"""
from typing import Any
from uuid import uuid4

from sqlalchemy import Column, DateTime, Boolean
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.sql import func
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

# Use the shared Base from the centralized database module
from app.core.database import Base


class GUID(TypeDecorator):
    """Platform-independent GUID type.

    Uses PostgreSQL's UUID type, otherwise uses CHAR(32), storing as stringified hex values.
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_UUID())
        return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        # store as hex string for non-PostgreSQL
        return value if isinstance(value, str) else ("%.32x" % int(value))

    def process_result_value(self, value, dialect):
        return value


class BaseModel(Base):
    """Base model with common audit fields and shared metadata."""
    __abstract__ = True

    id: Any

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    id = Column(GUID(), primary_key=True, default=uuid4, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(GUID(), nullable=True)
    updated_by = Column(GUID(), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
