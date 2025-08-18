"""
API endpoints for the Accounts Receivable module.

This module aggregates all the individual API routers from the 'endpoints' file
into a single main router for the Accounts Receivable module.
"""
from fastapi import APIRouter

from .endpoints import (
    router_invoices,
    router_payments,
    router_credit_notes,
    router_reports,
)

# Create the main router for the Accounts Receivable API
router = APIRouter(tags=["Accounts Receivable"])

# Include all endpoint routers from the 'endpoints' module
router.include_router(router_invoices)
router.include_router(router_payments)
router.include_router(router_credit_notes)
router.include_router(router_reports)

__all__ = ["router"]

__all__ = ["router"]
