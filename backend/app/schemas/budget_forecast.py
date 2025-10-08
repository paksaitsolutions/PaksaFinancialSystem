from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

class BudgetForecastDetailBase(BaseModel):
    period: str
    category: str
    historical_amount: Decimal = 0
    forecast_amount: Decimal = 0
    variance: Decimal = 0
    confidence: int = 0

class BudgetForecastDetailCreate(BudgetForecastDetailBase):
    pass

class BudgetForecastDetail(BudgetForecastDetailBase):
    id: int
    forecast_id: int

    class Config:
        from_attributes = True

class BudgetScenarioBase(BaseModel):
    scenario_type: str
    growth_rate: Decimal
    q1_amount: Decimal = 0
    q2_amount: Decimal = 0
    q3_amount: Decimal = 0
    q4_amount: Decimal = 0

class BudgetScenarioCreate(BudgetScenarioBase):
    pass

class BudgetScenario(BudgetScenarioBase):
    id: int
    forecast_id: int

    class Config:
        from_attributes = True

class BudgetForecastBase(BaseModel):
    name: str
    period: str
    method: str
    growth_rate: Decimal = 0
    total_forecast: Decimal = 0
    confidence_level: int = 0
    risk_level: str = "Medium"
    status: str = "Draft"

class BudgetForecastCreate(BudgetForecastBase):
    forecast_details: List[BudgetForecastDetailCreate] = []

class BudgetForecastUpdate(BaseModel):
    name: Optional[str] = None
    period: Optional[str] = None
    method: Optional[str] = None
    growth_rate: Optional[Decimal] = None
    total_forecast: Optional[Decimal] = None
    confidence_level: Optional[int] = None
    risk_level: Optional[str] = None
    status: Optional[str] = None

class BudgetForecast(BudgetForecastBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    forecast_details: List[BudgetForecastDetail] = []

    class Config:
        from_attributes = True

class ForecastSummary(BaseModel):
    total: Decimal
    growth_rate: Decimal
    confidence: int
    risk_level: str

class ChartData(BaseModel):
    labels: List[str]
    datasets: List[dict]