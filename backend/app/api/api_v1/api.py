
from fastapi import APIRouter

from app.api.endpoints.accounts_payable import vendor, invoice, payment, credit_memo, form_1099
from app.api.endpoints.inventory import item as inventory_item, adjustment as inventory_adjustment, category as inventory_category, purchase_order as inventory_purchase_order, reports as inventory_reports, barcode as inventory_barcode, cycle_count as inventory_cycle_count, forecast as inventory_forecast, location as inventory_location, transaction as inventory_transaction
from app.api.endpoints.accounts_receivable import collections_ai as ar_collections_ai
from app.api.endpoints.tax import tax_endpoints as tax_management
from app.api.endpoints.tax import tax_endpoints as tax_management

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

<<<<<<< HEAD
api_router.include_router(
    ar_collections_ai.router,
    prefix="/accounts-receivable/collections-ai",
    tags=["accounts-receivable", "ai"],
)

api_router.include_router(
    tax_management.router,
    prefix="/tax",
    tags=["tax"],
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
    from app.ai.api.ai_endpoints import router as ai_router
    api_router.include_router(ai_router, prefix="/ai", tags=["AI"])
except ImportError:
    pass

# Accounts Payable
try:
    from app.api.endpoints.accounts_payable import vendor, invoice, payment, credit_memo, form_1099
    api_router.include_router(vendor.router, prefix="/accounts-payable/vendors", tags=["Accounts Payable"])
    api_router.include_router(invoice.router, prefix="/accounts-payable/invoices", tags=["Accounts Payable"])
    api_router.include_router(payment.router, prefix="/accounts-payable/payments", tags=["Accounts Payable"])
    api_router.include_router(credit_memo.router, prefix="/accounts-payable/credit-memos", tags=["Accounts Payable"])
    api_router.include_router(form_1099.router, prefix="/accounts-payable/1099", tags=["Accounts Payable"])
except ImportError:
    pass

# Inventory
try:
    from app.api.endpoints.inventory import (
        item, adjustment, category, purchase_order, reports, 
        barcode, cycle_count, forecast, location, transaction
    )
    api_router.include_router(item.router, prefix="/inventory/items", tags=["Inventory"])
    api_router.include_router(adjustment.router, prefix="/inventory/adjustments", tags=["Inventory"])
    api_router.include_router(category.router, prefix="/inventory/categories", tags=["Inventory"])
    api_router.include_router(purchase_order.router, prefix="/inventory/purchase-orders", tags=["Inventory"])
    api_router.include_router(reports.router, prefix="/inventory/reports", tags=["Inventory"])
    api_router.include_router(barcode.router, prefix="/inventory/barcode", tags=["Inventory"])
    api_router.include_router(cycle_count.router, prefix="/inventory/cycle-counts", tags=["Inventory"])
    api_router.include_router(forecast.router, prefix="/inventory/forecast", tags=["Inventory"])
    api_router.include_router(location.router, prefix="/inventory/locations", tags=["Inventory"])
    api_router.include_router(transaction.router, prefix="/inventory/transactions", tags=["Inventory"])
except ImportError:
    pass

# Other endpoints
try:
    from app.api.endpoints import (
        financial_statements, currency, gl, intercompany, allocation, 
        period_close, rbac, password, session, audit, encryption, 
        compliance, retention, backup, user
    )
    api_router.include_router(financial_statements.router, prefix="/financial-statements", tags=["Financial Statements"])
    api_router.include_router(currency.router, prefix="/currency", tags=["Currency"])
    api_router.include_router(gl.router, prefix="/gl", tags=["General Ledger"])
    api_router.include_router(intercompany.router, prefix="/intercompany", tags=["Intercompany"])
    api_router.include_router(allocation.router, prefix="/allocation", tags=["Allocation"])
    api_router.include_router(period_close.router, prefix="/period-close", tags=["Period Close"])
    api_router.include_router(rbac.router, prefix="/rbac", tags=["RBAC"])
    api_router.include_router(password.router, prefix="/password", tags=["Password"])
    api_router.include_router(session.router, prefix="/session", tags=["Session"])
    api_router.include_router(audit.router, prefix="/audit", tags=["Audit"])
    api_router.include_router(encryption.router, prefix="/encryption", tags=["Encryption"])
    api_router.include_router(compliance.router, prefix="/compliance", tags=["Compliance"])
    api_router.include_router(retention.router, prefix="/retention", tags=["Retention"])
    api_router.include_router(backup.router, prefix="/backup", tags=["Backup"])
    api_router.include_router(user.router, prefix="/users", tags=["Users"])
except ImportError:
    pass