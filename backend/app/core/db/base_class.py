"""
Base database model with common fields and functionality.
"""
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import Mapped

class BaseModel:
    """Base model class with common fields and methods."""
    
    # Primary key
    id: Mapped[UUID] = Column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        unique=True,
        nullable=False,
        comment="Primary key"
    )
    
    # Audit fields
    created_at: Mapped[datetime] = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        comment="When the record was created"
    )
    
    updated_at: Mapped[datetime] = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="When the record was last updated"
    )
    
    created_by: Mapped[UUID] = Column(
        PG_UUID(as_uuid=True),
        nullable=False,
        comment="User ID who created the record"
    )
    
    updated_by: Mapped[UUID] = Column(
        PG_UUID(as_uuid=True),
        nullable=False,
        comment="User ID who last updated the record"
    )
    
    # Soft delete flag
    is_active: Mapped[bool] = Column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Whether the record is active (not deleted)"
    )
    
    # Table metadata
    __name__: str
    
    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        ""
        Generate __tablename__ automatically.
        Converts CamelCase class name to snake_case table name.
        """
        return ''.join(
            ['_' + i.lower() if i.isupper() else i 
             for i in cls.__name__]).lstrip('_')
    
    def to_dict(self, exclude: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Convert model instance to dictionary."""
        exclude = exclude or {}
        data = {}
        
        for column in self.__table__.columns:
            if column.name in exclude:
                continue
                
            value = getattr(self, column.name)
            
            # Convert UUID to string
            if isinstance(value, UUID):
                value = str(value)
            # Convert datetime to ISO format
            elif isinstance(value, datetime):
                value = value.isoformat()
            
            data[column.name] = value
        
        return data
    
    def update(self, **kwargs) -> None:
        """Update model instance with given attributes."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def __repr__(self) -> str:
        """String representation of the model instance."""
        return f"<{self.__class__.__name__}(id={self.id})>"

# Create a base class for SQLAlchemy models
Base = as_declarative(cls=BaseModel)
