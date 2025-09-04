from fastapi import APIRouter
from .endpoints import router as payroll_router
from .payroll_analytics_api import router as analytics_router

# Create a parent router for all payroll endpoints
router = APIRouter(prefix="/api/payroll", tags=["payroll"])

# Include the main payroll router without additional prefix
router.include_router(payroll_router, prefix="")

# Include the analytics router with the correct prefix
# Note: The analytics_router already has prefix="/api/payroll/analytics"
# So it will be available at /api/payroll/api/payroll/analytics
# We'll fix this by updating the analytics_router's prefix
router.include_router(analytics_router, prefix="")

__all__ = ["router"]