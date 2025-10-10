from fastapi import APIRouter
from app.api.v1.endpoints import cash_management, budget_forecast, budget, tax_returns, inventory, fixed_assets, reports, settings, gl
from app.api.endpoints.tax_api import router as tax_router
from app.api.endpoints.payroll_api import router as payroll_router
from app.api.endpoints.currency import router as currency_router
from app.api.endpoints.region import router as region_router
from app.api.endpoints.ap import router as ap_router
from app.api.endpoints.ar import router as ar_router
from app.api.endpoints.cash import router as cash_router
from app.api.endpoints.budget_advanced import router as budget_advanced_router
from app.api.endpoints.inventory import router as inventory_router
from app.api.endpoints.fixed_assets import router as fixed_assets_router
from app.api.endpoints.tax import router as tax_router_new
from app.api.endpoints.payroll import router as payroll_router
from app.api.endpoints.reports import router as reports_router
from app.api.endpoints.bi_ai.bi_ai_endpoints import router as bi_ai_router
from app.api.endpoints.settings import router as settings_router

api_router = APIRouter()
api_router.include_router(gl.router, tags=["general-ledger"])
api_router.include_router(ap_router, prefix="/ap", tags=["accounts-payable"])
api_router.include_router(ar_router, prefix="/ar", tags=["accounts-receivable"])
api_router.include_router(cash_router, prefix="/cash", tags=["cash-management"])
api_router.include_router(budget_advanced_router, prefix="/budgets", tags=["budget-advanced"])
api_router.include_router(inventory_router, prefix="/inventory", tags=["inventory-management"])
api_router.include_router(fixed_assets_router, prefix="/fixed-assets", tags=["fixed-assets"])
api_router.include_router(tax_router_new, prefix="/tax", tags=["tax-management"])
api_router.include_router(payroll_router, prefix="/payroll", tags=["payroll"])
api_router.include_router(reports_router, prefix="/reports", tags=["reports"])
api_router.include_router(bi_ai_router, prefix="/bi-ai", tags=["bi-ai"])
api_router.include_router(settings_router, prefix="/settings", tags=["settings"])
api_router.include_router(cash_management.router, prefix="/cash-management", tags=["cash-management"])
api_router.include_router(budget_forecast.router, prefix="/budget-forecasts", tags=["budget-forecasts"])
api_router.include_router(budget.router, prefix="/budgets", tags=["budgets"])
api_router.include_router(tax_returns.router, prefix="/tax-returns", tags=["tax-returns"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["inventory"])
api_router.include_router(fixed_assets.router, prefix="/fixed-assets", tags=["fixed-assets"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
api_router.include_router(tax_router, tags=["tax"])
api_router.include_router(payroll_router, tags=["payroll"])
api_router.include_router(currency_router, prefix="/currency", tags=["currency"])
api_router.include_router(region_router, prefix="/regions", tags=["regions"])