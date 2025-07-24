"""
BI/AI schemas.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

class DashboardBase(BaseModel):
    """Base dashboard schema."""
    name: str
    description: Optional[str] = None
    layout_config: Optional[Dict[str, Any]] = None
    is_default: bool = False
    is_active: bool = True

class DashboardCreate(DashboardBase):
    """Create dashboard schema."""
    pass

class DashboardResponse(DashboardBase):
    """Dashboard response schema."""
    id: UUID
    tenant_id: UUID
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class KPIBase(BaseModel):
    """Base KPI schema."""
    name: str
    description: Optional[str] = None
    formula: str
    target_value: Optional[str] = None
    unit: Optional[str] = None
    category: Optional[str] = None
    refresh_frequency: str = "daily"
    is_active: bool = True

class KPICreate(KPIBase):
    """Create KPI schema."""
    pass

class KPIResponse(KPIBase):
    """KPI response schema."""
    id: UUID
    tenant_id: UUID
    created_by: UUID
    created_at: datetime

    class Config:
        orm_mode = True

class KPIValue(BaseModel):
    """KPI value schema."""
    kpi_id: UUID
    name: str
    current_value: str
    target_value: Optional[str] = None
    unit: Optional[str] = None
    trend: str  # up, down, stable
    change_percentage: Optional[float] = None

class AnomalyBase(BaseModel):
    """Base anomaly schema."""
    metric_name: str
    metric_value: str
    expected_range: Optional[str] = None
    anomaly_score: Optional[str] = None
    severity: str = "medium"
    description: Optional[str] = None
    recommendation: Optional[str] = None

class AnomalyResponse(AnomalyBase):
    """Anomaly response schema."""
    id: UUID
    tenant_id: UUID
    status: str
    detected_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class PredictionBase(BaseModel):
    """Base prediction schema."""
    prediction_type: str
    target_metric: str
    prediction_data: Dict[str, Any]
    confidence_score: Optional[str] = None
    prediction_period: Optional[str] = None
    model_used: Optional[str] = None

class PredictionResponse(PredictionBase):
    """Prediction response schema."""
    id: UUID
    tenant_id: UUID
    created_at: datetime
    expires_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class AnalyticsData(BaseModel):
    """Analytics data schema."""
    revenue_trend: List[Dict[str, Any]]
    expense_breakdown: List[Dict[str, Any]]
    cash_flow_forecast: List[Dict[str, Any]]
    key_metrics: List[KPIValue]
    anomalies: List[AnomalyResponse]
    predictions: List[PredictionResponse]

class AIInsight(BaseModel):
    """AI insight schema."""
    insight_type: str
    title: str
    description: str
    impact: str  # high, medium, low
    recommendation: str
    confidence: float
    data_points: List[Dict[str, Any]]