"""
API endpoints for inventory forecasting.
"""
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.session import get_db
from app.core.api_response import success_response
from app.crud.inventory.forecast import inventory_forecast_crud
from app.schemas.inventory.forecast import DemandForecast, StockoutRisk, ForecastSummary

router = APIRouter()

@router.get("/demand", response_model=List[DemandForecast])
async def get_demand_forecast(
    *,
    db: AsyncSession = Depends(get_db),
    days_history: int = Query(90, ge=30, le=365, description="Days of history to analyze"),
    category_id: Optional[str] = Query(None, description="Filter by category"),
) -> Any:
    """
    Get demand forecast for inventory items.
    """
    forecast = await inventory_forecast_crud.get_demand_forecast(
        db, days_history=days_history, category_id=category_id
    )
    return success_response(data=forecast)

@router.get("/stockout-risks", response_model=List[StockoutRisk])
async def get_stockout_risks(
    *,
    db: AsyncSession = Depends(get_db),
    risk_threshold_days: int = Query(30, ge=7, le=90, description="Risk threshold in days"),
) -> Any:
    """
    Get stockout risk analysis for inventory items.
    """
    risks = await inventory_forecast_crud.get_stockout_risks(
        db, risk_threshold_days=risk_threshold_days
    )
    return success_response(data=risks)

@router.get("/summary", response_model=ForecastSummary)
async def get_forecast_summary(
    *,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get forecast summary statistics.
    """
    summary = await inventory_forecast_crud.get_forecast_summary(db)
    return success_response(data=summary)