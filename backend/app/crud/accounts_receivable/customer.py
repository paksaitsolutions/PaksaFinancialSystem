"""
CRUD operations for customers.
"""
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.db.query_helper import QueryHelper
from app.models.accounts_receivable.customer import Customer, CustomerContact
from app.schemas.accounts_receivable.customer import CustomerCreate, CustomerUpdate

class CustomerCRUD:
    """CRUD operations for customers."""
    
    def __init__(self):
        """Initialize with query helper."""
        self.query_helper = QueryHelper(Customer)
    
    async def create(self, db: AsyncSession, *, obj_in: CustomerCreate) -> Customer:
        """Create a new customer."""
        # Extract contacts data
        contacts_data = obj_in.contacts
        obj_in_data = obj_in.dict(exclude={"contacts"})
        
        # Create customer
        db_obj = Customer(**obj_in_data)
        db.add(db_obj)
        await db.flush()
        
        # Create contacts if provided
        if contacts_data:
            for contact_data in contacts_data:
                contact = CustomerContact(**contact_data.dict(), customer_id=db_obj.id)
                db.add(contact)
        
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get(self, db: AsyncSession, id: UUID) -> Optional[Customer]:
        """Get a customer by ID."""
        query = select(Customer).where(Customer.id == id).options(
            selectinload(Customer.contacts)
        )
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_by_code(self, db: AsyncSession, code: str) -> Optional[Customer]:
        """Get a customer by code."""
        query = select(Customer).where(Customer.code == code)
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> List[Customer]:
        """Get multiple customers."""
        query = self.query_helper.build_query(
            filters=filters,
            sort_by=sort_by or "name",
            sort_order=sort_order,
            skip=skip,
            limit=limit,
            eager_load=["contacts"]
        )
        return await self.query_helper.execute_query(db, query)
    
    async def get_paginated(
        self,
        db: AsyncSession,
        *,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> Dict[str, Any]:
        """Get paginated customers."""
        return await self.query_helper.get_paginated(
            db,
            filters=filters,
            sort_by=sort_by or "name",
            sort_order=sort_order,
            page=page,
            page_size=page_size,
            eager_load=["contacts"]
        )
    
    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: Customer,
        obj_in: Union[CustomerUpdate, Dict[str, Any]]
    ) -> Customer:
        """Update a customer."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        # Update customer attributes
        for field in update_data:
            if field != "contacts" and hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def delete(self, db: AsyncSession, *, id: UUID) -> Optional[Customer]:
        """Delete a customer."""
        customer = await self.get(db, id)
        if customer:
            await db.delete(customer)
            await db.commit()
        return customer

# Create an instance for dependency injection
customer_crud = CustomerCRUD()