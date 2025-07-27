"""
Base model classes with common fields and functionality.
"""
from datetime import datetime
from typing import Any
from uuid import uuid4
from sqlalchemy import Column, Integer, DateTime, String, Boolean, Text
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import TypeDecorator, CHAR

class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses PostgreSQL's UUID type, otherwise uses CHAR(32), storing as stringified hex values.
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, str):
                return "%.32x" % int(value)
            else:
                return value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, str):
                return str(value)
            return value

@as_declarative()
class Base:
    id: Any
    __name__: str
    
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

class BaseModel(Base):
    """Base model with common audit fields."""
    __abstract__ = True
    
    id = Column(GUID(), primary_key=True, default=uuid4, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(GUID(), nullable=True)
    updated_by = Column(GUID(), nullable=True)
    is_active = Column(Boolean, default=True)

class AuditModel(BaseModel):
    """Extended base model with full audit trail."""
    __abstract__ = True
    
    version = Column(Integer, default=1)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime(timezone=True))
    deleted_by = Column(GUID(), nullable=True)
    
    # Additional audit fields
    tenant_id = Column(GUID(), nullable=True, index=True)
    notes = Column(Text, nullable=True)