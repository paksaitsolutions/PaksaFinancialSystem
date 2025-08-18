"""
Base database models and mixins for Paksa Financial System.
"""
from datetime import datetime
from typing import Any, Dict, Optional, TypeVar, Type
from uuid import UUID, uuid4

from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, String, event
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.sql import func

from app.core.security import AuditMixin as PydanticAuditMixin

# Type variable for model classes
ModelType = TypeVar("ModelType", bound="Base")

@as_declarative()
class Base:
    """Base class for all SQLAlchemy models."""
    
    id: Any
    __name__: str
    
    # Generate table name from class name
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + 's'
    
    # Common columns
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    created_by = Column(PG_UUID(as_uuid=True), nullable=False, comment="User ID of the creator")
    updated_by = Column(PG_UUID(as_uuid=True), nullable=True, comment="User ID of the last updater")
    is_active = Column(Boolean, default=True, nullable=False, comment="Soft delete flag")
    
    # Audit logging
    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary."""
        return {
            c.name: getattr(self, c.name) 
            for c in self.__table__.columns
        }
    
    def update(self, **kwargs) -> None:
        """Update model attributes."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

# Event listeners for audit fields
@event.listens_for(Session, 'before_flush')
def before_flush(session: Session, context, instances) -> None:
    """Set audit fields before flush."""
    for instance in session.new:
        if hasattr(instance, 'created_at') and not instance.created_at:
            instance.created_at = datetime.utcnow()
    
    for instance in session.dirty:
        if hasattr(instance, 'updated_at'):
            instance.updated_at = datetime.utcnow()

class AuditBaseModel(BaseModel):
    """Base Pydantic model with audit fields."""
    id: Optional[UUID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    is_active: bool = True
    
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

class PaginatedResponse(BaseModel):
    """Generic paginated response model."""
    items: list[Any] = []
    total: int = 0
    page: int = 1
    page_size: int = 20
    total_pages: int = 1

class QueryFilter(BaseModel):
    """Base filter for querying models."""
    skip: int = 0
    limit: int = 100
    order_by: Optional[str] = None
    order_direction: str = "asc"
    
    def apply(self, query):
        """Apply filter to SQLAlchemy query."""
        if self.order_by:
            column = getattr(self.__model__, self.order_by, None)
            if column is not None:
                if self.order_direction.lower() == "desc":
                    column = column.desc()
                query = query.order_by(column)
        
        return query.offset(self.skip).limit(self.limit)

class BaseRepository:
    """Base repository for database operations."""
    
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db
    
    def get(self, id: UUID) -> Optional[ModelType]:
        """Get a single record by ID."""
        return self.db.query(self.model).filter(
            self.model.id == id,
            self.model.is_active == True
        ).first()
    
    def list(self, filter: QueryFilter) -> tuple[list[ModelType], int]:
        """List records with pagination."""
        query = self.db.query(self.model).filter(self.model.is_active == True)
        total = query.count()
        
        if filter:
            query = filter.apply(query)
        
        return query.all(), total
    
    def create(self, obj_in: BaseModel, created_by: UUID) -> ModelType:
        """Create a new record."""
        db_obj = self.model(
            **obj_in.dict(exclude_unset=True),
            created_by=created_by,
            updated_by=created_by
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def update(self, id: UUID, obj_in: BaseModel, updated_by: UUID) -> Optional[ModelType]:
        """Update a record."""
        db_obj = self.get(id)
        if not db_obj:
            return None
            
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db_obj.updated_by = updated_by
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def delete(self, id: UUID, deleted_by: UUID) -> bool:
        """Soft delete a record."""
        db_obj = self.get(id)
        if not db_obj:
            return False
            
        db_obj.is_active = False
        db_obj.updated_by = deleted_by
        self.db.commit()
        return True
