"""
Base CRUD operations for Accounts Payable module
"""
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union, cast
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import and_, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import Base
from app.core.exceptions import (
    BadRequestException,
    NotFoundException,
    ValidationException
)

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBaseAP(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base CRUD operations for Accounts Payable"""
    
    def __init__(self, model: Type[ModelType]):
        """Initialize with the SQLAlchemy model"""
        self.model = model
    
    async def get(self, db: AsyncSession, id: UUID) -> Optional[ModelType]:
        """Get a single record by ID"""
        result = await db.get(self.model, id)
        return result
    
    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None
    ) -> List[ModelType]:
        """Get multiple records with optional filtering and pagination"""
        query = select(self.model)
        
        # Apply filters
        if filters:
            filter_conditions = []
            for field, value in filters.items():
                if hasattr(self.model, field):
                    if isinstance(value, (list, set, tuple)):
                        filter_conditions.append(getattr(self.model, field).in_(value))
                    else:
                        filter_conditions.append(getattr(self.model, field) == value)
            
            if filter_conditions:
                query = query.where(and_(*filter_conditions))
        
        # Apply ordering
        if order_by:
            if order_by.startswith('-'):
                order_column = getattr(self.model, order_by[1:], None)
                if order_column is not None:
                    query = query.order_by(order_column.desc())
            else:
                order_column = getattr(self.model, order_by, None)
                if order_column is not None:
                    query = query.order_by(order_column)
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType, **kwargs) -> ModelType:
        """Create a new record"""
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data, **kwargs)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """Update an existing record"""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def remove(self, db: AsyncSession, *, id: UUID) -> ModelType:
        """Delete a record by ID"""
        obj = await self.get(db, id)
        if not obj:
            raise NotFoundException(f"{self.model.__name__} with ID {id} not found")
        
        await db.delete(obj)
        await db.commit()
        return obj

# Alias for backward compatibility
CRUDBase = CRUDBaseAP