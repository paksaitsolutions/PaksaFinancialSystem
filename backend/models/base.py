from datetime import datetime
from typing import Any, Dict, Optional
from uuid import uuid4, UUID

from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import declarative_base, declared_attr
from sqlalchemy.sql import expression
from sqlalchemy.types import TypeDecorator, CHAR

from core.database import Base

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
        if not isinstance(value, UUID):
            return str(UUID(value).hex)
        return value.hex
    
    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if not isinstance(value, UUID):
            value = UUID(value)
        return value

class BaseModel(Base):
    """Base model class that includes common fields and methods."""
    __abstract__ = True
    
    id = Column(GUID(), primary_key=True, default=uuid4, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    is_active = Column(Boolean, server_default=expression.true(), nullable=False, default=True)
    
    @declared_attr
    def __tablename__(cls) -> str:
        ""
        Generate __tablename__ automatically.
        Convert CamelCase class name to snake_case table name.
        """
        name = cls.__name__
        return ''.join(['_' + i.lower() if i.isupper() else i for i in name]).lstrip('_')
    
    def to_dict(self, exclude: Optional[list] = None) -> Dict[str, Any]:
        """Convert model instance to dictionary.
        
        Args:
            exclude: List of field names to exclude from the result.
            
        Returns:
            Dictionary representation of the model instance.
        """
        exclude = set(exclude or [])
        exclude.update({'is_active', 'created_at', 'updated_at'})
        
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
            if column.name not in exclude
        }
    
    def update(self, **kwargs) -> None:
        """Update model instance with given attributes.
        
        Args:
            **kwargs: Attributes to update.
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def __repr__(self) -> str:
        """String representation of the model instance."""
        return f"<{self.__class__.__name__}(id={self.id})>"
