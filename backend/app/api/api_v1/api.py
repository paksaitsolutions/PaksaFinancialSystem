"""
API v1 router.
"""
from fastapi import APIRouter

from app.api.endpoints.accounts_payable import vendor, invoice, payment

# Create API v1 router
api_router = APIRouter()

# Include all API endpoints
api_router.include_router(
    vendor.router,
    prefix="/accounts-payable/vendors",
    tags=["accounts-payable", "vendors"],
)

api_router.include_router(
    invoice.router,
    prefix="/accounts-payable/invoices",
    tags=["accounts-payable", "invoices"],
)

api_router.include_router(
    payment.router,
    prefix="/accounts-payable/payments",
    tags=["accounts-payable", "payments"],
)

# Add more routers here as needed