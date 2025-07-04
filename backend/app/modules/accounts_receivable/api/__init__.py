"""
API endpoints for the Accounts Receivable module.
"""
from fastapi import APIRouter
from .endpoints import router as endpoints_router

# Create the main router for the API
router = APIRouter(prefix="/accounts-receivable", tags=["Accounts Receivable"])

# Include all endpoint routers
router.include_router(endpoints_router)

__all__ = ["router"]
