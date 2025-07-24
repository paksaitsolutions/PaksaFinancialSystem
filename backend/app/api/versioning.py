"""
API versioning utilities.

This module provides utilities for API versioning, allowing for multiple
versions of the API to coexist and ensuring backward compatibility.
"""
from enum import Enum
from typing import Callable, Dict, List, Optional, Type, Union

from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException, Request, status
from pydantic import BaseModel

class APIVersion(str, Enum):
    """API version enum."""
    V1 = "v1"
    V2 = "v2"
    # Add new versions here as needed

class VersionedAPIRouter(APIRouter):
    """Router that supports API versioning."""
    
    def __init__(
        self,
        version: APIVersion,
        prefix: str = "",
        *args,
        **kwargs
    ):
        """Initialize the versioned router.
        
        Args:
            version: The API version for this router
            prefix: The prefix for all routes in this router
            *args: Additional arguments for APIRouter
            **kwargs: Additional keyword arguments for APIRouter
        """
        self.version = version
        versioned_prefix = f"/api/{version}{prefix}"
        super().__init__(prefix=versioned_prefix, *args, **kwargs)

def get_version(
    accept_version: Optional[str] = Header(None, alias="Accept-Version"),
    request: Request = None,
) -> APIVersion:
    """Dependency to get the requested API version.
    
    The version can be specified in the Accept-Version header or in the URL path.
    If not specified, defaults to the latest version.
    
    Args:
        accept_version: The Accept-Version header value
        request: The request object
        
    Returns:
        The API version to use
        
    Raises:
        HTTPException: If the requested version is invalid
    """
    # Check header first
    if accept_version:
        try:
            return APIVersion(accept_version.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid API version: {accept_version}"
            )
    
    # Check URL path
    if request and request.url.path:
        path_parts = request.url.path.split("/")
        for part in path_parts:
            if part.startswith("v") and len(part) > 1:
                try:
                    return APIVersion(part.lower())
                except ValueError:
                    # Continue checking other parts
                    pass
    
    # Default to latest version
    return APIVersion.V2  # Change this to the latest version

def version_dependency(allowed_versions: List[APIVersion]) -> Callable:
    """Create a dependency that checks if the requested version is allowed.
    
    Args:
        allowed_versions: List of allowed API versions
        
    Returns:
        A dependency function that checks the version
    """
    def _check_version(version: APIVersion = Depends(get_version)) -> APIVersion:
        if version not in allowed_versions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"API version {version} is not supported for this endpoint"
            )
        return version
    
    return _check_version

def setup_versioned_routes(app: FastAPI, routers: Dict[APIVersion, List[APIRouter]]) -> None:
    """Set up versioned routes for the application.
    
    Args:
        app: The FastAPI application
        routers: Dictionary mapping API versions to lists of routers
    """
    for version, router_list in routers.items():
        for router in router_list:
            app.include_router(router)