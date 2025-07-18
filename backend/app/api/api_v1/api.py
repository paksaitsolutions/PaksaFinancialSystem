"""
Main API router that includes all endpoint routers.
"""
from fastapi import APIRouter

# Import core financial modules
from app.modules.core_financials.general_ledger.api import router as gl_router
from app.modules.core_financials.accounts_payable.api import router as ap_router
from app.modules.core_financials.accounts_receivable.api import router as ar_router
from app.modules.core_financials.cash_management.api import router as cash_router
from app.modules.core_financials.payroll.api import router as payroll_router
from app.modules.core_financials.fixed_assets.api import router as assets_router
from app.modules.core_financials.budget.api import router as budget_router

# Import extended financial modules
from app.modules.extended_financials.project_accounting.api import router as project_router

# Import cross-cutting modules
try:
    from app.modules.cross_cutting.bi_ai.api import router as bi_router
    has_bi_module = True
except ImportError:
    has_bi_module = False

try:
    from app.modules.cross_cutting.compliance.api import router as compliance_router
    has_compliance_module = True
except ImportError:
    has_compliance_module = False

try:
    from app.modules.tax.api import router as tax_router
    has_tax_module = True
except ImportError:
    has_tax_module = False

api_router = APIRouter(prefix="/api/v1")

# Core Financial Modules
api_router.include_router(gl_router, prefix="/gl", tags=["General Ledger"])
api_router.include_router(ap_router, prefix="/ap", tags=["Accounts Payable"])
api_router.include_router(ar_router, prefix="/ar", tags=["Accounts Receivable"])
api_router.include_router(cash_router, prefix="/cash", tags=["Cash Management"])
api_router.include_router(payroll_router, prefix="/payroll", tags=["Payroll"])
api_router.include_router(assets_router, prefix="/assets", tags=["Fixed Assets"])
api_router.include_router(budget_router, prefix="/budget", tags=["Budget"])

# Extended Financial Modules
api_router.include_router(project_router, prefix="/projects", tags=["Project Accounting"])

# Cross-cutting Modules
if has_bi_module:
    api_router.include_router(bi_router, prefix="/bi", tags=["Business Intelligence"])

if has_compliance_module:
    api_router.include_router(compliance_router, prefix="/compliance", tags=["Compliance"])

if has_tax_module:
    api_router.include_router(tax_router, prefix="/tax", tags=["Taxation"])

# Health check
@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Paksa Financial System API is running"}