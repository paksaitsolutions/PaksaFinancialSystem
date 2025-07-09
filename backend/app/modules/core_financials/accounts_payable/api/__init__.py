from fastapi import APIRouter
from .endpoints import router_vendors, router_bills, router_payments

router = APIRouter()
router.include_router(router_vendors, prefix="/vendors", tags=["Accounts Payable - Vendors"])
router.include_router(router_bills, prefix="/bills", tags=["Accounts Payable - Bills"])
router.include_router(router_payments, prefix="/payments", tags=["Accounts Payable - Payments"])
