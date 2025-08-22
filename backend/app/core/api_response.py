"""
Standardized API response formats and error handling.
"""
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from fastapi import status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    """Standard API response format."""
    status: str = "success"
    message: Optional[str] = None
    data: Optional[T] = None
    meta: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseModel):
    """Standard error response format."""
    status: str = "error"
    message: str
    error_code: Optional[str] = None
    details: Optional[Any] = None

class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response format."""
    status: str = "success"
    message: Optional[str] = None
    data: List[T]
    meta: Dict[str, Any] = Field(default_factory=dict)
    pagination: Dict[str, int] = Field(...)

def success_response(
    data: Any = None, 
    message: Optional[str] = None, 
    meta: Optional[Dict[str, Any]] = None,
    status_code: int = status.HTTP_200_OK
) -> JSONResponse:
    """Create a standardized success response."""
    return JSONResponse(
        status_code=status_code,
        content=APIResponse(
            status="success",
            message=message,
            data=data,
            meta=meta
        ).model_dump(exclude_none=True)
    )

def error_response(
    message: str,
    status_code: int = status.HTTP_400_BAD_REQUEST,
    error_code: Optional[str] = None,
    details: Optional[Any] = None
) -> JSONResponse:
    """Create a standardized error response."""
    return JSONResponse(
        status_code=status_code,
        content=ErrorResponse(
            status="error",
            message=message,
            error_code=error_code,
            details=details
        ).model_dump(exclude_none=True)
    )

def paginated_response(
    data: List[Any],
    total: int,
    page: int,
    page_size: int,
    message: Optional[str] = None,
    meta: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """Create a standardized paginated response."""
    pagination = {
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size
    }
    
    return JSONResponse(
        content=PaginatedResponse(
            status="success",
            message=message,
            data=data,
            meta=meta or {},
            pagination=pagination
        ).model_dump(exclude_none=True)
    )