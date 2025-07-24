"""
API package for the Paksa Financial System.
This package contains all API routes and endpoints.
"""

# Import the API v1 router directly from the implementation file to avoid circular imports
from .api_v1.api import api_router

# This makes the router available when importing from app.api
__all__ = ["api_router"]
