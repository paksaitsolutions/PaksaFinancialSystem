from fastapi import APIRouter
from .endpoints import router as payroll_router

# Create a parent router for all payroll endpoints
router = APIRouter()
router.include_router(payroll_router, prefix="/payroll", tags=["payroll"])

__all__ = ["router"]