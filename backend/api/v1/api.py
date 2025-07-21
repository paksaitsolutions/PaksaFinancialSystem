"""
API v1 Router Configuration

This module defines the main API v1 router and includes all endpoint routes.
"""
from fastapi import APIRouter

# Import all endpoint routers here
# from .endpoints import users, items, etc.

# Create the main API v1 router
api_router = APIRouter(prefix="/api/v1", tags=["v1"])

# Include authentication routes
from app.modules.cross_cutting.auth.router import router as auth_router
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])

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
