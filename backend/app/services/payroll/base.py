"""
Base service class for Payroll module services.
"""
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import Base
from app.core.logging import logger
from app.core.security import get_password_hash, verify_password



"""
Base service classes for Payroll module.
"""

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
ResponseSchemaType = TypeVar("ResponseSchemaType", bound=BaseModel)


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType, ResponseSchemaType]):
    """Base service class with CRUD operations."""

    def __init__(self, model: Type[ModelType], db: Session):
        """  Init  ."""
        """Initialize base service with model and database session."""
        self.model = model
        self.db = db

    def get(self, id: Union[UUID, str, int]) -> Optional[ModelType]:
        """Get."""
        """Get a single record by ID."""
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        """Get Multi."""
        self, *, skip: int = 0, limit: int = 100, **filters: Any
    ) -> List[ModelType]:
        """Get Multi."""
        """Get multiple records with optional filtering and pagination."""
        query = self.db.query(self.model)
        
        # Apply filters
        for field, value in filters.items():
            if hasattr(self.model, field):
                query = query.filter(getattr(self.model, field) == value)
        
        return query.offset(skip).limit(limit).all()

    def create(self, *, obj_in: CreateSchemaType) -> ModelType:
        """Create."""
        """Create a new record."""
        obj_in_data = obj_in.dict(exclude_unset=True)
        db_obj = self.model(**obj_in_data)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(
        """Update."""
        self, *, id: Union[UUID, str, int], obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> Optional[ModelType]:
        """Update."""
        """Update a record."""
        db_obj = self.get(id)
        if not db_obj:
            return None
            
        obj_data = db_obj.__dict__
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
            
        for field, value in update_data.items():
            if field in obj_data and value is not None:
                setattr(db_obj, field, value)
                
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, *, id: Union[UUID, str, int]) -> bool:
        """Delete."""
        """Delete a record."""
        db_obj = self.get(id)
        if not db_obj:
            return False
            
        self.db.delete(db_obj)
        self.db.commit()
        return True
        
    def get_or_404(self, id: Union[UUID, str, int], detail: str = "Not found") -> ModelType:
        """Get Or 404."""
        """Get a record by ID or raise 404 if not found."""
        obj = self.get(id)
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=detail
            )
        return obj
        
    def get_multi_by_employee(
        """Get Multi By Employee."""
        self, employee_id: UUID, *, skip: int = 0, limit: int = 100, **filters: Any
    ) -> List[ModelType]:
        """Get Multi By Employee."""
        """Get multiple records filtered by employee ID."""
        return self.get_multi(
            skip=skip, 
            limit=limit, 
            employee_id=employee_id,
            **filters
        )


class CRUDService(
    BaseService[ModelType, CreateSchemaType, UpdateSchemaType, ResponseSchemaType]
):
    """CRUD service with response schema mapping."""
    
    def __init__(
        """  Init  ."""
        self, 
        model: Type[ModelType], 
        db: Session, 
        response_schema: Type[ResponseSchemaType]
    ):
        """  Init  ."""
        """Initialize CRUD service with model, db session, and response schema."""
        super().__init__(model, db)
        self.response_schema = response_schema
    
    def get_response(self, db_obj: ModelType) -> ResponseSchemaType:
        """Get Response."""
        """Convert a database object to a response schema."""
        return self.response_schema.from_orm(db_obj)
    
    def get_multi_response(
        """Get Multi Response."""
        self, db_objs: List[ModelType]
    ) -> List[ResponseSchemaType]:
        """Get Multi Response."""
        """Convert a list of database objects to response schemas."""
        return [self.get_response(obj) for obj in db_objs]
    
    def get_by_id(self, id: UUID) -> Optional[ResponseSchemaType]:
        """Get By Id."""
        """Get a single record by ID and convert to response schema."""
        db_obj = self.get(id)
        if db_obj:
            return self.get_response(db_obj)
        return None
    
    def get_by_id_or_404(self, id: UUID) -> ResponseSchemaType:
        """Get By Id Or 404."""
        """Get a single record by ID or raise 404 if not found."""
        db_obj = self.get_or_404(id)
        return self.get_response(db_obj)
    
    def get_all(
        """Get All."""
        self, *, skip: int = 0, limit: int = 100, **filters: Any
    ) -> List[ResponseSchemaType]:
        """Get All."""
        """Get multiple records with filtering and convert to response schemas."""
        db_objs = self.get_multi(skip=skip, limit=limit, **filters)
        return self.get_multi_response(db_objs)
    
    def create_with_response(
        """Create With Response."""
        self, *, obj_in: CreateSchemaType
    ) -> ResponseSchemaType:
        """Create With Response."""
        """Create a new record and return the response schema."""
        db_obj = self.create(obj_in=obj_in)
        return self.get_response(db_obj)
    
    def update_with_response(
        """Update With Response."""
        self, *, id: UUID, obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> Optional[ResponseSchemaType]:
        """Update With Response."""
        """Update a record and return the response schema."""
        db_obj = self.update(id=id, obj_in=obj_in)
        if db_obj:
            return self.get_response(db_obj)
        return None
    
    def get_by_employee(
        """Get By Employee."""
        self, employee_id: UUID, *, skip: int = 0, limit: int = 100, **filters: Any
    ) -> List[ResponseSchemaType]:
        """Get By Employee."""
        """Get multiple records filtered by employee ID and convert to response schemas."""
        db_objs = self.get_multi_by_employee(
            employee_id=employee_id, 
            skip=skip, 
            limit=limit, 
            **filters
        )
        return self.get_multi_response(db_objs)
