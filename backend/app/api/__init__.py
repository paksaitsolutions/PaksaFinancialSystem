"""
API package for the Paksa Financial System.
This package contains all API routes and endpoints.
"""
from fastapi import APIRouter

# Create a main API router
api_router = APIRouter()

# Import the API v1 router
from .api_v1.api import api_router as api_v1_router

# Import deps after to avoid circular import
try:
    from ..core import deps
except ImportError:
    deps = None

# Include the v1 router with a prefix
api_router.include_router(api_v1_router, prefix="/v1")

# This makes the router available when importing from app.api
__all__ = ["api_router", "deps"]