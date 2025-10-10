from fastapi import APIRouter
from app.api.v1.endpoints import cash_management, budget_forecast, budget, tax_returns, inventory, fixed_assets, reports, settings
from app.api.endpoints.tax_api import router as tax_router
from app.api.endpoints.payroll_api import router as payroll_router
from app.api.endpoints.currency import router as currency_router
from app.api.endpoints.region import router as region_router

api_router = APIRouter()
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