"""
Base service class with common CRUD operations and utilities.
"""
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union, cast
from uuid import UUID
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.database import Base, SessionLocal

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
T = TypeVar('T')

class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base service with common CRUD operations and utilities."""
    
    def __init__(self, model: Type[ModelType]):
        """Initialize the service with a model class."""
        self.model = model
    
    def _get_db(self) -> Session:
        """Get a database session."""
        return SessionLocal()
    
    def _get_or_404(
        self, 
        db: Session, 
        model: Type[T], 
        id: UUID,
        not_found_exception: Exception = None
    ) -> T:
        """
        Get a record by ID or raise an appropriate exception.
        
        Args:
            db: Database session
            model: SQLAlchemy model class
            id: Record ID to fetch
            not_found_exception: Custom exception to raise if not found
            
        Returns:
            The fetched record
            
        Raises:
            HTTPException: If record not found and no custom exception provided
            Exception: If record not found and custom exception is provided
        """
        obj = db.query(model).get(id)
        if not obj:
            if not_found_exception:
                raise not_found_exception
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{model.__name__} with id {id} not found"
            )
        return obj

    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_multi(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        result = await db.execute(select(self.model).offset(skip).limit(limit))
        return result.scalars().all()

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
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
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, id: Any) -> Optional[ModelType]:
        result = await db.execute(select(self.model).where(self.model.id == id))
        obj = result.scalar_one_or_none()
        if obj is None:
            return None
        await db.delete(obj)
        await db.commit()
        return obj
