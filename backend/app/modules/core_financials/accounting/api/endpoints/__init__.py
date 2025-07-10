"""
General Ledger API Endpoints

This module contains all API endpoints related to the General Ledger functionality.
"""
from fastapi import APIRouter

# Import all endpoint modules here
from . import accounts, journal_entries, account_balances, financial_statement_templates

# Create the main GL router
gl_router = APIRouter(prefix="/gl", tags=["general-ledger"])

# Include all endpoint routers
gl_router.include_router(accounts.router, prefix="/accounts", tags=["accounts"])
gl_router.include_router(journal_entries.router, prefix="/journal-entries", tags=["journal-entries"])
gl_router.include_router(account_balances.router, prefix="/account-balances", tags=["account-balances"])
gl_router.include_router(
    financial_statement_templates.router, 
    prefix="/financial-statement-templates", 
    tags=["financial-statement-templates"]
)

# Export the router for use in the main API
router = gl_router
