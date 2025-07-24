"""
Database query optimization helpers.

This module provides utilities for optimizing database queries,
including pagination, filtering, and sorting.
"""
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from sqlalchemy import asc, desc, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select
from sqlalchemy.orm import selectinload, joinedload

from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)

class QueryHelper(Generic[ModelType]):
    """Helper class for building optimized database queries."""
    
    def __init__(self, model: Type[ModelType]):
        """Initialize the query helper.
        
        Args:
            model: The SQLAlchemy model class
        """
        self.model = model
    
    def build_query(
        self,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
        eager_load: Optional[List[str]] = None,
    ) -> Select:
        """Build an optimized query with filters, sorting, and pagination.
        
        Args:
            filters: Dictionary of field-value pairs to filter by
            sort_by: Field to sort by
            sort_order: Sort order ("asc" or "desc")
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_deleted: Whether to include soft-deleted records
            eager_load: List of relationships to eager load
            
        Returns:
            SQLAlchemy Select object
        """
        # Start with a base query
        query = select(self.model)
        
        # Apply filters
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    if isinstance(value, list):
                        query = query.where(getattr(self.model, field).in_(value))
                    else:
                        query = query.where(getattr(self.model, field) == value)
        
        # Filter out soft-deleted records unless explicitly included
        if hasattr(self.model, "deleted_at") and not include_deleted:
            query = query.where(self.model.deleted_at.is_(None))
        
        # Apply sorting
        if sort_by and hasattr(self.model, sort_by):
            if sort_order.lower() == "desc":
                query = query.order_by(desc(getattr(self.model, sort_by)))
            else:
                query = query.order_by(asc(getattr(self.model, sort_by)))
        
        # Apply eager loading for relationships
        if eager_load:
            for relationship in eager_load:
                if "__" in relationship:
                    # Nested relationship (e.g., "parent__children")
                    parts = relationship.split("__")
                    load_strategy = joinedload(getattr(self.model, parts[0]))
                    for part in parts[1:]:
                        load_strategy = load_strategy.joinedload(part)
                    query = query.options(load_strategy)
                else:
                    # Direct relationship
                    query = query.options(selectinload(getattr(self.model, relationship)))
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        return query
    
    async def execute_query(
        self,
        db: AsyncSession,
        query: Select,
    ) -> List[ModelType]:
        """Execute the query and return the results.
        
        Args:
            db: Database session
            query: SQLAlchemy Select object
            
        Returns:
            List of model instances
        """
        result = await db.execute(query)
        return result.scalars().all()
    
    async def count_query(
        self,
        db: AsyncSession,
        filters: Optional[Dict[str, Any]] = None,
        include_deleted: bool = False,
    ) -> int:
        """Count the number of records matching the filters.
        
        Args:
            db: Database session
            filters: Dictionary of field-value pairs to filter by
            include_deleted: Whether to include soft-deleted records
            
        Returns:
            Number of matching records
        """
        # Start with a base query
        query = select(func.count()).select_from(self.model)
        
        # Apply filters
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    if isinstance(value, list):
                        query = query.where(getattr(self.model, field).in_(value))
                    else:
                        query = query.where(getattr(self.model, field) == value)
        
        # Filter out soft-deleted records unless explicitly included
        if hasattr(self.model, "deleted_at") and not include_deleted:
            query = query.where(self.model.deleted_at.is_(None))
        
        # Execute the query
        result = await db.execute(query)
        return result.scalar() or 0
    
    async def get_paginated(
        self,
        db: AsyncSession,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
        page: int = 1,
        page_size: int = 20,
        include_deleted: bool = False,
        eager_load: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Get paginated results.
        
        Args:
            db: Database session
            filters: Dictionary of field-value pairs to filter by
            sort_by: Field to sort by
            sort_order: Sort order ("asc" or "desc")
            page: Page number (1-based)
            page_size: Number of records per page
            include_deleted: Whether to include soft-deleted records
            eager_load: List of relationships to eager load
            
        Returns:
            Dictionary with pagination info and results
        """
        # Calculate skip
        skip = (page - 1) * page_size
        
        # Build and execute the query
        query = self.build_query(
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order,
            skip=skip,
            limit=page_size,
            include_deleted=include_deleted,
            eager_load=eager_load,
        )
        items = await self.execute_query(db, query)
        
        # Count total records
        total = await self.count_query(db, filters, include_deleted)
        
        # Calculate total pages
        total_pages = (total + page_size - 1) // page_size if total > 0 else 1
        
        return {
            "items": items,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1,
            },
        }