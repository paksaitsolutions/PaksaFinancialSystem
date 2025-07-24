"""
API v1 router.
"""
from fastapi import APIRouter

from app.api.endpoints.accounts_payable import vendor, invoice, payment, credit_memo, form_1099

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

api_router.include_router(
    credit_memo.router,
    prefix="/accounts-payable/credit-memos",
    tags=["accounts-payable", "credit-memos"],
)

api_router.include_router(
    form_1099.router,
    prefix="/accounts-payable/1099",
    tags=["accounts-payable", "1099-reporting"],
)

# Add more routers here as needed