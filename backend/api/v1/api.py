from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from core.database import get_db
from core.security import get_current_active_user

# Create main API router
api_router = APIRouter()

# Import and include all API routes here
from .endpoints import (
    accounts_payable,
    chart_of_accounts,
    journal_entries
)

# Include API routes
api_router.include_router(
    chart_of_accounts.router, 
    prefix="/chart-of-accounts", 
    tags=["Chart of Accounts"]
)

api_router.include_router(
    journal_entries.router,
    prefix="/journal-entries",
    tags=["Journal Entries"]
)

api_router.include_router(
    accounts_payable.router,
    prefix="/accounts-payable",
    tags=["Accounts Payable"]
)

@api_router.get("/")
async def api_root():
    """Root API endpoint."""
    return {
        "message": "Welcome to Paksa Financial System API",
        "version": "v1",
        "documentation": "/docs",
    }
