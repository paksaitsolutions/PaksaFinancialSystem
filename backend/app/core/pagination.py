"""
Standardized pagination utilities for consistent API responses.
"""
from typing import Any, Dict, List, Optional, TypeVar
from pydantic import BaseModel, Field
from sqlalchemy.orm import Query
from sqlalchemy import func

T = TypeVar('T')

class PaginationParams(BaseModel):
    """Standard pagination parameters."""
    page: int = Field(default=1, ge=1, description="Page number (1-based)")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")
    sort_by: Optional[str] = Field(default=None, description="Field to sort by")
    sort_order: str = Field(default="asc", regex="^(asc|desc)$", description="Sort order")

class PaginationMeta(BaseModel):
    """Pagination metadata."""
    total: int = Field(description="Total number of items")
    page: int = Field(description="Current page number")
    page_size: int = Field(description="Items per page")
    pages: int = Field(description="Total number of pages")
    has_next: bool = Field(description="Whether there is a next page")
    has_prev: bool = Field(description="Whether there is a previous page")

def paginate_query(
    query: Query,
    page: int = 1,
    page_size: int = 20
) -> tuple[List[Any], PaginationMeta]:
    """
    Paginate a SQLAlchemy query and return results with metadata.
    
    Args:
        query: SQLAlchemy query object
        page: Page number (1-based)
        page_size: Number of items per page
        
    Returns:
        Tuple of (items, pagination_meta)
    """
    # Get total count
    total = query.count()
    
    # Calculate pagination values
    pages = (total + page_size - 1) // page_size
    offset = (page - 1) * page_size
    
    # Get paginated results
    items = query.offset(offset).limit(page_size).all()
    
    # Create pagination metadata
    meta = PaginationMeta(
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
        has_next=page < pages,
        has_prev=page > 1
    )
    
    return items, meta