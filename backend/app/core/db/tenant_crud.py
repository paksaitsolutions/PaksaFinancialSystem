from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import DeclarativeBase
from .tenant_middleware import get_current_tenant

ModelType = TypeVar("ModelType", bound=DeclarativeBase)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class TenantAwareCRUD(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        tenant_id = get_current_tenant()
        result = await db.execute(
            select(self.model).where(
                and_(self.model.id == id, self.model.tenant_id == tenant_id)
            )
        )
        return result.scalar_one_or_none()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        tenant_id = get_current_tenant()
        result = await db.execute(
            select(self.model)
            .where(self.model.tenant_id == tenant_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        tenant_id = get_current_tenant()
        obj_in_data = jsonable_encoder(obj_in)
        obj_in_data['tenant_id'] = tenant_id
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
        tenant_id = get_current_tenant()
        
        # Verify the object belongs to the current tenant
        if hasattr(db_obj, 'tenant_id') and db_obj.tenant_id != tenant_id:
            raise ValueError("Cannot update object from different tenant")
        
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, id: int) -> ModelType:
        tenant_id = get_current_tenant()
        obj = await db.execute(
            select(self.model).where(
                and_(self.model.id == id, self.model.tenant_id == tenant_id)
            )
        )
        obj = obj.scalar_one_or_none()
        if not obj:
            raise ValueError("Object not found or access denied")
        
        await db.delete(obj)
        await db.commit()
        return obj

    async def get_by_tenant(self, db: AsyncSession, tenant_id: str) -> List[ModelType]:
        """Admin function to get objects by specific tenant"""
        result = await db.execute(
            select(self.model).where(self.model.tenant_id == tenant_id)
        )
        return result.scalars().all()

    async def count_by_tenant(self, db: AsyncSession, tenant_id: str) -> int:
        """Count objects for a specific tenant"""
        result = await db.execute(
            select(func.count(self.model.id)).where(self.model.tenant_id == tenant_id)
        )
        return result.scalar()