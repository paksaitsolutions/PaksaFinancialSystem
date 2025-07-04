"""
Base service class with common functionality for all services.
"""
from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.exceptions import (
    BusinessRuleException,
    NotFoundException,
    ValidationException
)
from app.db.base_class import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
ResponseSchemaType = TypeVar("ResponseSchemaType", bound=BaseModel)

class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType, ResponseSchemaType]):
    """Base service class with CRUD operations."""
    
    def __init__(self, db: Session, model: Type[ModelType]):
        """Initialize with database session and model class."""
        self.db = db
        self.model = model
    
    def get(self, id: Union[str, UUID]) -> Optional[ResponseSchemaType]:
        """Get a single record by ID."""
        obj = self.db.query(self.model).filter(
            self.model.id == id,
            self.model.is_active == True
        ).first()
        
        if not obj:
            return None
            
        return self._to_response_schema(obj)
    
    def get_multi(
        self, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        **filters: Any
    ) -> List[ResponseSchemaType]:
        """Get multiple records with optional filtering and pagination."""
        query = self.db.query(self.model).filter(self.model.is_active == True)
        
        # Apply filters
        for field, value in filters.items():
            if hasattr(self.model, field) and value is not None:
                query = query.filter(getattr(self.model, field) == value)
        
        # Apply pagination
        objs = query.offset(skip).limit(limit).all()
        return [self._to_response_schema(obj) for obj in objs]
    
    def create(self, obj_in: CreateSchemaType, created_by: UUID) -> ResponseSchemaType:
        """Create a new record."""
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(
            **obj_in_data,
            created_by=created_by,
            updated_by=created_by
        )
        
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        
        return self._to_response_schema(db_obj)
    
    def update(
        self, 
        id: Union[str, UUID], 
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
        updated_by: UUID
    ) -> Optional[ResponseSchemaType]:
        """Update a record."""
        db_obj = self.db.query(self.model).filter(
            self.model.id == id,
            self.model.is_active == True
        ).first()
        
        if not db_obj:
            return None
        
        obj_data = jsonable_encoder(db_obj)
        
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        for field in obj_data:
            if field in update_data and field != 'id':
                setattr(db_obj, field, update_data[field])
        
        db_obj.updated_by = updated_by
        db_obj.updated_at = datetime.utcnow()
        
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        
        return self._to_response_schema(db_obj)
    
    def delete(self, id: Union[str, UUID], deleted_by: UUID) -> bool:
        """Soft delete a record."""
        db_obj = self.db.query(self.model).filter(
            self.model.id == id,
            self.model.is_active == True
        ).first()
        
        if not db_obj:
            return False
        
        db_obj.is_active = False
        db_obj.updated_by = deleted_by
        db_obj.updated_at = datetime.utcnow()
        
        self.db.add(db_obj)
        self.db.commit()
        
        return True
    
    def _to_response_schema(self, db_obj: ModelType) -> ResponseSchemaType:
        """Convert a database model to a response schema."""
        # This should be implemented by subclasses
        raise NotImplementedError("Subclasses must implement this method")
