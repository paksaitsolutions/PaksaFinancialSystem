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

# Include additional modules
try:
    # Authentication module
    from app.modules.cross_cutting.auth.router import router as auth_router
    api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
except ImportError as e:
    print(f"Warning: Could not import auth module: {e}")
    
try:
    # Financial Statements module
    from app.api.endpoints.financial_statements import router as financial_statements_router
    api_router.include_router(financial_statements_router, prefix="/financial-statements", tags=["Financial Statements"])
except ImportError as e:
    print(f"Warning: Could not import financial statements module: {e}")
    
try:
    # Currency module
    from app.api.endpoints.currency import router as currency_router
    api_router.include_router(currency_router, prefix="/currency", tags=["Currency"])
except ImportError as e:
    print(f"Warning: Could not import currency module: {e}")

try:
    # General Ledger module
    from app.api.endpoints.gl import router as gl_router
    api_router.include_router(gl_router, prefix="/gl", tags=["General Ledger"])
except ImportError as e:
    print(f"Warning: Could not import general ledger module: {e}")

try:
    # Intercompany module
    from app.api.endpoints.intercompany import router as intercompany_router
    api_router.include_router(intercompany_router, prefix="/intercompany", tags=["Intercompany"])
except ImportError as e:
    print(f"Warning: Could not import intercompany module: {e}")

try:
    # Allocation module
    from app.api.endpoints.allocation import router as allocation_router
    api_router.include_router(allocation_router, prefix="/allocation", tags=["Allocation"])
except ImportError as e:
    print(f"Warning: Could not import allocation module: {e}")

try:
    # Period Close module
    from app.api.endpoints.period_close import router as period_close_router
    api_router.include_router(period_close_router, prefix="/period-close", tags=["Period Close"])
except ImportError as e:
    print(f"Warning: Could not import period close module: {e}")

# Add more routers here as needed

# Include additional modules
try:
    # Authentication module
    from app.modules.cross_cutting.auth.router import router as auth_router
    api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
except ImportError as e:
    print(f"Warning: Could not import auth module: {e}")
    
try:
    # Financial Statements module
    from app.api.endpoints.financial_statements import router as financial_statements_router
    api_router.include_router(financial_statements_router, prefix="/financial-statements", tags=["Financial Statements"])
except ImportError as e:
    print(f"Warning: Could not import financial statements module: {e}")
    
try:
    # Currency module
    from app.api.endpoints.currency import router as currency_router
    api_router.include_router(currency_router, prefix="/currency", tags=["Currency"])
except ImportError as e:
    print(f"Warning: Could not import currency module: {e}")

try:
    # General Ledger module
    from app.api.endpoints.gl import router as gl_router
    api_router.include_router(gl_router, prefix="/gl", tags=["General Ledger"])
except ImportError as e:
    print(f"Warning: Could not import general ledger module: {e}")

try:
    # Intercompany module
    from app.api.endpoints.intercompany import router as intercompany_router
    api_router.include_router(intercompany_router, prefix="/intercompany", tags=["Intercompany"])
except ImportError as e:
    print(f"Warning: Could not import intercompany module: {e}")

try:
    # Allocation module
    from app.api.endpoints.allocation import router as allocation_router
    api_router.include_router(allocation_router, prefix="/allocation", tags=["Allocation"])
except ImportError as e:
    print(f"Warning: Could not import allocation module: {e}")

try:
    # Period Close module
    from app.api.endpoints.period_close import router as period_close_router
    api_router.include_router(period_close_router, prefix="/period-close", tags=["Period Close"])
except ImportError as e:
    print(f"Warning: Could not import period close module: {e}")
