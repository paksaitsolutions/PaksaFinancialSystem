from fastapi import APIRouter
from .endpoints import router_accounts, router_journal_entries
from .v1.endpoints import router as v1_router

# Main API router
router = APIRouter()

# Include legacy endpoints
router.include_router(router_accounts, prefix="/accounts", tags=["Accounting - Chart of Accounts"])
router.include_router(router_journal_entries, prefix="/journal-entries", tags=["Accounting - Journal Entries"])

# Include v1 API endpoints
router.include_router(v1_router, tags=["API v1"])
