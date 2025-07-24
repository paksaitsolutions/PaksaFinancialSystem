"""
API v1 package for the Paksa Financial System.
This package contains all version 1 API routes and endpoints.
"""

# Initialize API router here to avoid circular imports
from fastapi import APIRouter

api_router = APIRouter(prefix="/api/v1")

# This makes the router available when importing from app.api.api_v1
__all__ = ["api_router"]

# Import and include routers after initialization to avoid circular imports
try:
    from .api import setup_routers
    setup_routers(api_router)
except ImportError as e:
    print(f"Warning: Could not set up all API routers: {e}")
