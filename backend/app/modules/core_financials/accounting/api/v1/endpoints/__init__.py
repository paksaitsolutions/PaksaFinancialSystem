from fastapi import APIRouter
from .financial_statements import router as financial_statements_router

# Create a router for all v1 endpoints
router = APIRouter(prefix="/v1")

# Include the financial statements router
router.include_router(
    financial_statements_router,
    prefix="/financial-statements",
    tags=["Financial Statements"]
)
