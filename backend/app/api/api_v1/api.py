"""
API v1 router.
"""
from fastapi import APIRouter

from app.api.endpoints.accounts_payable import vendor, invoice, payment, credit_memo, form_1099
from app.api.endpoints.inventory import item as inventory_item, adjustment as inventory_adjustment, category as inventory_category, purchase_order as inventory_purchase_order, reports as inventory_reports, barcode as inventory_barcode, cycle_count as inventory_cycle_count, forecast as inventory_forecast, location as inventory_location, transaction as inventory_transaction

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

api_router.include_router(
    inventory_item.router,
    prefix="/inventory/items",
    tags=["inventory", "items"],
)

api_router.include_router(
    inventory_adjustment.router,
    prefix="/inventory/adjustments",
    tags=["inventory", "adjustments"],
)

api_router.include_router(
    inventory_category.router,
    prefix="/inventory/categories",
    tags=["inventory", "categories"],
)

api_router.include_router(
    inventory_purchase_order.router,
    prefix="/inventory/purchase-orders",
    tags=["inventory", "purchase-orders"],
)

api_router.include_router(
    inventory_reports.router,
    prefix="/inventory/reports",
    tags=["inventory", "reports"],
)

api_router.include_router(
    inventory_barcode.router,
    prefix="/inventory/barcode",
    tags=["inventory", "barcode"],
)

api_router.include_router(
    inventory_cycle_count.router,
    prefix="/inventory/cycle-counts",
    tags=["inventory", "cycle-counts"],
)

api_router.include_router(
    inventory_forecast.router,
    prefix="/inventory/forecast",
    tags=["inventory", "forecast"],
)

api_router.include_router(
    inventory_location.router,
    prefix="/inventory/locations",
    tags=["inventory", "locations"],
)

api_router.include_router(
    inventory_transaction.router,
    prefix="/inventory/transactions",
    tags=["inventory", "transactions"],
)

# Security & Compliance modules
try:
    from app.api.endpoints.rbac import router as rbac_router
    api_router.include_router(rbac_router, prefix="/rbac", tags=["RBAC"])
except ImportError as e:
    print(f"Warning: Could not import RBAC module: {e}")

try:
    from app.api.endpoints.password import router as password_router
    api_router.include_router(password_router, prefix="/password", tags=["Password"])
except ImportError as e:
    print(f"Warning: Could not import password module: {e}")

try:
    from app.api.endpoints.session import router as session_router
    api_router.include_router(session_router, prefix="/session", tags=["Session"])
except ImportError as e:
    print(f"Warning: Could not import session module: {e}")

try:
    from app.api.endpoints.audit import router as audit_router
    api_router.include_router(audit_router, prefix="/audit", tags=["Audit"])
except ImportError as e:
    print(f"Warning: Could not import audit module: {e}")

try:
    from app.api.endpoints.encryption import router as encryption_router
    api_router.include_router(encryption_router, prefix="/encryption", tags=["Encryption"])
except ImportError as e:
    print(f"Warning: Could not import encryption module: {e}")

try:
    from app.api.endpoints.compliance import router as compliance_router
    api_router.include_router(compliance_router, prefix="/compliance", tags=["Compliance"])
except ImportError as e:
    print(f"Warning: Could not import compliance module: {e}")

try:
    from app.api.endpoints.retention import router as retention_router
    api_router.include_router(retention_router, prefix="/retention", tags=["Retention"])
except ImportError as e:
    print(f"Warning: Could not import retention module: {e}")

try:
    from app.api.endpoints.backup import router as backup_router
    api_router.include_router(backup_router, prefix="/backup", tags=["Backup"])
except ImportError as e:
    print(f"Warning: Could not import backup module: {e}")

# Multi-tenant modules
try:
    from app.api.endpoints.company import router as company_router
    api_router.include_router(company_router, prefix="/company", tags=["Company"])
except ImportError as e:
    print(f"Warning: Could not import company module: {e}")

try:
    from app.api.endpoints.enhanced_reports import router as enhanced_reports_router
    api_router.include_router(enhanced_reports_router, prefix="/enhanced-reports", tags=["Enhanced Reports"])
except ImportError as e:
    print(f"Warning: Could not import enhanced reports module: {e}")

# Financial modules
try:
    from app.api.endpoints.financial_statements import router as financial_statements_router
    api_router.include_router(financial_statements_router, prefix="/financial-statements", tags=["Financial Statements"])
except ImportError as e:
    print(f"Warning: Could not import financial statements module: {e}")

try:
    from app.api.endpoints.currency import router as currency_router
    api_router.include_router(currency_router, prefix="/currency", tags=["Currency"])
except ImportError as e:
    print(f"Warning: Could not import currency module: {e}")

try:
    from app.api.endpoints.gl import router as gl_router
    api_router.include_router(gl_router, prefix="/gl", tags=["General Ledger"])
except ImportError as e:
    print(f"Warning: Could not import general ledger module: {e}")

try:
    from app.api.endpoints.intercompany import router as intercompany_router
    api_router.include_router(intercompany_router, prefix="/intercompany", tags=["Intercompany"])
except ImportError as e:
    print(f"Warning: Could not import intercompany module: {e}")

try:
    from app.api.endpoints.allocation import router as allocation_router
    api_router.include_router(allocation_router, prefix="/allocation", tags=["Allocation"])
except ImportError as e:
    print(f"Warning: Could not import allocation module: {e}")

try:
    from app.api.endpoints.period_close import router as period_close_router
    api_router.include_router(period_close_router, prefix="/period-close", tags=["Period Close"])
except ImportError as e:
    print(f"Warning: Could not import period close module: {e}")

# Authentication
try:
    from app.modules.cross_cutting.auth.router import router as auth_router
    api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
except ImportError as e:
    print(f"Warning: Could not import auth module: {e}")