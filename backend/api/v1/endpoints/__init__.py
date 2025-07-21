"""
API Endpoints Package

This package contains all API endpoint modules for the v1 API.
"""

from fastapi import APIRouter

# Import all endpoint modules here
from . import tax, tax_calculation

# Create main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(tax.router, prefix="/tax", tags=["tax"])
api_router.include_router(tax_calculation.router, prefix="/tax", tags=["tax"])

__all__ = ["api_router"]
