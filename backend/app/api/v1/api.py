from fastapi import APIRouter
from app.api.v1.endpoints import cash_management, budget_forecast, budget, tax_returns

api_router = APIRouter()
api_router.include_router(cash_management.router, prefix="/cash-management", tags=["cash-management"])
api_router.include_router(budget_forecast.router, prefix="/budget-forecasts", tags=["budget-forecasts"])
api_router.include_router(budget.router, prefix="/budgets", tags=["budgets"])
api_router.include_router(tax_returns.router, prefix="/tax-returns", tags=["tax-returns"])