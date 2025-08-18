"""
Core schemas and types for the BI/AI module.

This module contains base schemas, common field types, and enums used throughout
all BI/AI module schemas.
"""
from datetime import datetime, date
from enum import Enum
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator, AnyUrl, HttpUrl, Json
from pydantic.generics import GenericModel

# Type variables for generic schemas
T = TypeVar('T')
ID = TypeVar('ID', str, int, UUID)

# Re-export common enums from models
from ..models import (
    AIModelType, AIModelFramework, AIModelStatus,
    DataSourceType, DataSourceStatus, ScheduleFrequency,
    PipelineStatus, TransformationType, ReportFormat,
    ReportFrequency, KPIType, TimeRange
)

class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
        }
        orm_mode = True
        allow_population_by_field_name = True
        use_enum_values = True
        arbitrary_types_allowed = True

class BaseCreateSchema(BaseSchema):
    ""
    Base schema for creating new records.
    Excludes id, created_at, updated_at, etc. as they're set by the system.
    """
    pass

class BaseUpdateSchema(BaseSchema):
    ""
    Base schema for updating existing records.
    All fields are optional as partial updates are supported.
    """
    pass

class BaseInDBBase(BaseSchema, Generic[T]):
    ""Base schema for database models with common fields."""
    id: Optional[ID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

# Common field types
class PyObjectId(str):
    ""Custom type for MongoDB ObjectId compatibility."""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not v:
            return None
        return str(v)

class UUIDModelMixin(BaseModel):
    ""Mixin for models that use UUID as primary key."""
    id: UUID = Field(default_factory=uuid4)

class TimestampMixin(BaseModel):
    ""Mixin for timestamp fields."""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    @validator('updated_at', pre=True, always=True)
    def set_updated_at(cls, v, values):
        return v or datetime.utcnow()

class AuditMixin(BaseModel):
    ""Mixin for audit fields."""
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

# Common response schemas
class Response(BaseModel, Generic[T]):
    ""Standard API response schema."""
    success: bool = True
    message: Optional[str] = None
    data: Optional[T] = None
    
    @classmethod
    def success_response(cls, data: T = None, message: str = None) -> 'Response[T]':
        ""Create a successful response."""
        return cls(success=True, data=data, message=message)
    
    @classmethod
    def error_response(cls, message: str, data: T = None) -> 'Response[T]':
        ""Create an error response."""
        return cls(success=False, data=data, message=message)

class PaginatedResponse(Response[T]):
    ""Paginated API response schema."""
    total: int = 0
    page: int = 1
    page_size: int = 10
    total_pages: int = 1
    
    @classmethod
    def from_pagination(
        cls, 
        items: List[T], 
        total: int, 
        page: int, 
        page_size: int
    ) -> 'PaginatedResponse[T]':
        ""Create a paginated response from a query result."""
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 1
        return cls(
            success=True,
            data=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )

# Common filter schemas
class BaseFilter(BaseModel):
    ""Base filter schema for query parameters."""
    page: int = 1
    page_size: int = 20
    sort_by: Optional[str] = None
    sort_order: str = "asc"
    search: Optional[str] = None
    
    @validator('page')
    def validate_page(cls, v):
        if v < 1:
            return 1
        return v
    
    @validator('page_size')
    def validate_page_size(cls, v):
        if v < 1:
            return 20
        if v > 100:  # Limit page size to prevent performance issues
            return 100
        return v
    
    @validator('sort_order')
    def validate_sort_order(cls, v):
        if v.lower() not in ('asc', 'desc'):
            return 'asc'
        return v.lower()

# Common relationship schemas
class Relationship(BaseModel):
    ""Schema for representing relationships between resources."""
    id: Union[str, int, UUID]
    type: str
    
    class Config:
        json_encoders = {
            UUID: lambda v: str(v),
        }

class RelationshipData(BaseModel):
    ""Schema for relationship data in JSON:API style."""
    data: Union[Relationship, List[Relationship], None]

# Common metadata schemas
class Metadata(BaseModel):
    ""Schema for additional metadata in API responses."""
    count: Optional[int] = None
    total: Optional[int] = None
    page: Optional[int] = None
    page_size: Optional[int] = None
    filters: Optional[Dict[str, Any]] = None

# Common error schemas
class ErrorDetail(BaseModel):
    ""Schema for error details."""
    code: str
    message: str
    target: Optional[str] = None
    
    @classmethod
    def from_exception(cls, exc: Exception, code: str = "internal_error"):
        ""Create an error detail from an exception."""
        return cls(code=code, message=str(exc))

class ErrorResponse(BaseModel):
    ""Standard error response schema."""
    error: ErrorDetail
    
    @classmethod
    def from_exception(
        cls, 
        exc: Exception, 
        code: str = "internal_error",
        status_code: int = 500,
        target: str = None
    ):
        ""Create an error response from an exception."""
        return cls(
            error=ErrorDetail(
                code=code,
                message=str(exc),
                target=target
            )
        )

# Common query parameter schemas
class IncludeQuery(BaseModel):
    ""Schema for include query parameter."""
    include: Optional[str] = None
    
    @validator('include')
    def validate_include(cls, v):
        if not v:
            return []
        return [rel.strip() for rel in v.split(',') if rel.strip()]

class FieldsQuery(BaseModel):
    ""Schema for fields query parameter."""
    fields: Optional[Dict[str, str]] = None
    
    @validator('fields', pre=True)
    def parse_fields(cls, v):
        if not v:
            return {}
        if isinstance(v, str):
            try:
                # Parse fields from query string like "fields[users]=name,email&fields[posts]=title"
                from urllib.parse import parse_qs, unquote
                parsed = {}
                for key, values in parse_qs(unquote(v)).items():
                    if key.startswith('fields[') and key.endswith(']'):
                        resource_type = key[7:-1]  # Extract resource type from fields[resource_type]
                        fields = [f.strip() for v in values for f in v.split(',') if f.strip()]
                        if fields:
                            parsed[resource_type] = fields
                return parsed
            except Exception:
                return {}
        return v

# Common file upload schemas
class FileUpload(BaseModel):
    ""Schema for file uploads."""
    filename: str
    content_type: str
    content: bytes
    size: int
    
    @validator('size')
    def validate_size(cls, v):
        max_size = 10 * 1024 * 1024  # 10MB
        if v > max_size:
            raise ValueError(f'File size exceeds maximum allowed size of {max_size} bytes')
        return v

# Common date range filter
class DateRangeFilter(BaseModel):
    ""Schema for date range filters."""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    
    @validator('end_date', always=True)
    def validate_date_range(cls, v, values):
        if 'start_date' in values and values['start_date'] and v:
            if v < values['start_date']:
                raise ValueError('end_date must be after start_date')
        return v or date.today()

# Common ID path parameters
class IDPath(BaseModel):
    ""Schema for ID path parameters."""
    id: Union[str, int, UUID]
    
    @validator('id', pre=True)
    def parse_id(cls, v):
        try:
            # Try to parse as UUID
            if isinstance(v, str):
                return UUID(v)
            return v
        except (ValueError, AttributeError):
            return v  # Return as is if not a valid UUID (could be an integer ID)

# Common query parameters for filtering
class CommonQueryParams(BaseModel):
    ""Common query parameters for filtering and pagination."""
    q: Optional[str] = None
    page: int = 1
    per_page: int = 20
    sort: Optional[str] = None
    
    @validator('page')
    def validate_page(cls, v):
        return max(1, v)
    
    @validator('per_page')
    def validate_per_page(cls, v):
        return min(100, max(1, v))  # Limit to 100 items per page

# Common response headers
class ResponseHeaders(BaseModel):
    ""Common response headers."""
    X_Total_Count: Optional[int] = None
    X_Page: Optional[int] = None
    X_Per_Page: Optional[int] = None
    X_Total_Pages: Optional[int] = None
    Link: Optional[str] = None
    
    class Config:
        allow_population_by_field_name = True
        fields = {
            'X_Total_Count': 'X-Total-Count',
            'X_Page': 'X-Page',
            'X_Per_Page': 'X-Per-Page',
            'X_Total_Pages': 'X-Total-Pages',
            'Link': 'Link'
        }
