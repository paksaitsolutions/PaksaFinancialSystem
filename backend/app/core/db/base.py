"""
Base database model with common fields and functionality.
"""
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, Boolean, MetaData
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import Mapped

# Recommended naming convention used by Alembic
# See: https://alembic.sqlalchemy.org/en/latest/naming.html
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=NAMING_CONVENTION)

class BaseModel:
    """Base model class with common fields and methods."""
    
    # Primary key
    id: Mapped[UUID] = Column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
        unique=True,
        nullable=False,
    )
    
    # Timestamps
    created_at: Mapped[datetime] = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        index=True,
    )
    
    updated_at: Mapped[datetime] = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    
    # Soft delete
    is_active: Mapped[bool] = Column(Boolean, default=True, nullable=False, index=True)
    deleted_at: Mapped[Optional[datetime]] = Column(DateTime(timezone=True), nullable=True)
    
    # Table metadata
    __name__: str
    
    @declared_attr
    def __tablename__(cls) -> str:
        """
        Generate __tablename__ automatically.
        Converts CamelCase class name to snake_case table name.
        """
        return ''.join(['_' + i.lower() if i.isupper() else i for i in cls.__name__]).lstrip('_')
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model instance to dictionary.
        """
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            
            # Convert UUID to string
            if isinstance(value, UUID):
                value = str(value)
            # Convert datetime to ISO format string
            elif isinstance(value, datetime):
                value = value.isoformat()
                
            result[column.name] = value
            
        return result
    
    def update(self, **kwargs) -> None:
        """
        Update model attributes.
        
        Args:
            **kwargs: Attributes to update
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def soft_delete(self) -> None:
        """Mark the record as deleted."""
        self.is_active = False
        self.deleted_at = datetime.utcnow()
    
    def restore(self) -> None:
        """Restore a soft-deleted record."""
        self.is_active = True
        self.deleted_at = None

# Create a base class for SQLAlchemy models
Base = as_declarative(cls=BaseModel, metadata=metadata)
