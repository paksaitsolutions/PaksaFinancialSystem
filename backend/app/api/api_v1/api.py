"""
Main API router that includes all endpoint routers.
"""
from fastapi import APIRouter

# Import core financial modules
from app.modules.core_financials.general_ledger.api import router as gl_router
from app.modules.core_financials.payroll.api import router as payroll_router

api_router = APIRouter(prefix="/api/v1")

# Core Financial Modules
api_router.include_router(gl_router, prefix="/gl", tags=["General Ledger"])
api_router.include_router(payroll_router, prefix="/payroll", tags=["Payroll"])

# Health check
@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Paksa Financial System API is running"}
