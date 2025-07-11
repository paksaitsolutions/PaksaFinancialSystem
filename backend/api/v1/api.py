"""
API v1 Router Configuration

This module defines the main API v1 router and includes all endpoint routes.
"""
from fastapi import APIRouter

# Import all endpoint routers here
# from .endpoints import users, items, etc.

# Create the main API v1 router
api_router = APIRouter(prefix="/api/v1", tags=["v1"])

# Include all endpoint routers
# api_router.include_router(users.router, prefix="/users", tags=["users"])
# api_router.include_router(items.router, prefix="/items", tags=["items"])

# Include the GL (General Ledger) endpoints
from ...modules.core_financials.accounting.api.endpoints import router as gl_router
api_router.include_router(gl_router, prefix="/gl", tags=["general-ledger"])

# Include the Payroll endpoints
from .endpoints.payroll import router as payroll_router
api_router.include_router(payroll_router, prefix="/payroll", tags=["payroll"])

# Include the Compliance endpoints
from ...modules.cross_cutting.compliance.api.endpoints import router as compliance_router
api_router.include_router(compliance_router, prefix="/compliance", tags=["compliance"])

# Include the Procurement endpoints
from ...modules.extended_financials.procurement import router as procurement_router
api_router.include_router(procurement_router, prefix="/procurement", tags=["procurement"])

# Include the BI Reporting endpoints
from app.modules.cross_cutting.bi_reporting.api.endpoints import router as bi_reporting_router
api_router.include_router(bi_reporting_router)

# Include the AI/ML endpoints
from app.modules.cross_cutting.ai_ml.api.endpoints import router as ai_ml_router
api_router.include_router(ai_ml_router)
