"""
Schemas for inventory forecasting.
"""
from typing import List, Optional
from uuid import UUID
from datetime import date
from decimal import Decimal
from pydantic import BaseModel

class DemandForecast(BaseModel):
    """Schema for demand forecast."""
    item_id: UUID
    sku: str
    name: str
    current_stock: Decimal
    average_daily_usage: Decimal
    forecasted_demand_30_days: Decimal
    forecasted_demand_60_days: Decimal
    forecasted_demand_90_days: Decimal
    days_until_stockout: Optional[int] = None
    recommended_order_quantity: Decimal
    reorder_point: Decimal

class StockoutRisk(BaseModel):
    """Schema for stockout risk analysis."""
    item_id: UUID
    sku: str
    name: str
    current_stock: Decimal
    daily_usage: Decimal
    days_remaining: int
    risk_level: str  # low, medium, high, critical
    recommended_action: str

class ForecastSummary(BaseModel):
    """Schema for forecast summary."""
    total_items_analyzed: int
    items_at_risk: int
    items_requiring_reorder: int
    total_recommended_order_value: Decimal
    forecast_accuracy: Optional[float] = None