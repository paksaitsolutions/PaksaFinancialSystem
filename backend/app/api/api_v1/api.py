from fastapi import APIRouter

# Create API v1 router
api_router = APIRouter()

# Core modules
try:
    from app.modules.core_financials.general_ledger.api import router as gl_router
    api_router.include_router(gl_router, prefix="/general-ledger", tags=["General Ledger"])
except ImportError:
    pass

try:
    from app.modules.core_financials.tax.api import router as tax_router
    api_router.include_router(tax_router, prefix="/tax", tags=["Tax"])
except ImportError:
    pass

try:
    from app.modules.accounts_receivable.api.ar_endpoints import router as ar_router
    api_router.include_router(ar_router, prefix="/accounts-receivable", tags=["Accounts Receivable"])
except ImportError:
    pass

try:
    from app.modules.super_admin.api.super_admin_endpoints import router as super_admin_router
    api_router.include_router(super_admin_router, prefix="/super-admin", tags=["Super Admin"])
except ImportError:
    pass

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