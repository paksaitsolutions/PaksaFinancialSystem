"""
AI/BI Module Pydantic Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class AIInsightBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    insight_type: str = Field(..., pattern="^(anomaly|prediction|recommendation|trend)$")
    module: str = Field(..., pattern="^(gl|ap|ar|cash|budget|inventory|payroll|tax|assets|hrm)$")
    priority: str = Field(default="Medium", pattern="^(High|Medium|Low)$")
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    meta_data: Dict[str, Any] = Field(default_factory=dict)


class AIInsightCreate(AIInsightBase):
    pass


class AIInsightUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    priority: Optional[str] = Field(None, pattern="^(High|Medium|Low)$")
    status: Optional[str] = Field(None, pattern="^(Active|Dismissed|Applied)$")
    meta_data: Optional[Dict[str, Any]] = None


class AIInsight(AIInsightBase):
    id: UUID
    tenant_id: UUID
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AIRecommendationBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    recommendation_type: str = Field(..., min_length=1, max_length=50)
    module: str = Field(..., pattern="^(gl|ap|ar|cash|budget|inventory|payroll|tax|assets|hrm)$")
    priority: str = Field(default="Medium", pattern="^(High|Medium|Low)$")
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    estimated_impact: float = Field(default=0.0)
    action_items: List[str] = Field(default_factory=list)


class AIRecommendationCreate(AIRecommendationBase):
    pass


class AIRecommendationUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    priority: Optional[str] = Field(None, pattern="^(High|Medium|Low)$")
    status: Optional[str] = Field(None, pattern="^(Pending|Applied|Dismissed)$")
    estimated_impact: Optional[float] = None
    action_items: Optional[List[str]] = None


class AIRecommendation(AIRecommendationBase):
    id: UUID
    tenant_id: UUID
    status: str
    applied_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AIAnomalyBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    anomaly_type: str = Field(..., min_length=1, max_length=50)
    module: str = Field(..., pattern="^(gl|ap|ar|cash|budget|inventory|payroll|tax|assets|hrm)$")
    severity: str = Field(default="Medium", pattern="^(Critical|High|Medium|Low)$")
    anomaly_score: float = Field(..., ge=0.0)
    threshold: float = Field(..., ge=0.0)
    affected_records: List[Dict[str, Any]] = Field(default_factory=list)


class AIAnomalyCreate(AIAnomalyBase):
    pass


class AIAnomalyUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(Open|Investigating|Resolved|False_Positive)$")
    severity: Optional[str] = Field(None, pattern="^(Critical|High|Medium|Low)$")


class AIAnomaly(AIAnomalyBase):
    id: UUID
    tenant_id: UUID
    status: str
    resolved_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AIPredictionBase(BaseModel):
    prediction_type: str = Field(..., pattern="^(cash_flow|revenue|expense|budget_variance)$")
    module: str = Field(..., pattern="^(gl|ap|ar|cash|budget|inventory|payroll|tax|assets|hrm)$")
    target_date: datetime
    predicted_value: float
    confidence_interval: Dict[str, float] = Field(default_factory=dict)
    accuracy_score: float = Field(default=0.0, ge=0.0, le=1.0)
    model_version: str = Field(..., min_length=1, max_length=50)
    input_features: Dict[str, Any] = Field(default_factory=dict)


class AIPredictionCreate(AIPredictionBase):
    pass


class AIPrediction(AIPredictionBase):
    id: UUID
    tenant_id: UUID
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AIAnalyticsData(BaseModel):
    cash_flow_accuracy: float = Field(default=0.0, ge=0.0, le=100.0)
    anomalies_count: int = Field(default=0, ge=0)
    cost_savings: float = Field(default=0.0)
    processing_speed: float = Field(default=0.0, gt=0.0)
    total_accounts: int = Field(default=0, ge=0)
    total_cash: float = Field(default=0.0)
    trends: Dict[str, float] = Field(default_factory=dict)
    timestamp: datetime


class AIInsightsList(BaseModel):
    success: bool
    data: List[AIInsight]
    total: int = 0


class AIRecommendationsList(BaseModel):
    success: bool
    data: List[AIRecommendation]
    count: int = 0
    generated_at: datetime


class AIAnalyticsResponse(BaseModel):
    success: bool
    data: AIAnalyticsData


class AIModelMetricsBase(BaseModel):
    model_name: str = Field(..., min_length=1, max_length=100)
    model_type: str = Field(..., pattern="^(classification|regression|clustering|forecasting)$")
    version: str = Field(..., min_length=1, max_length=20)
    accuracy: float = Field(default=0.0, ge=0.0, le=1.0)
    precision: float = Field(default=0.0, ge=0.0, le=1.0)
    recall: float = Field(default=0.0, ge=0.0, le=1.0)
    f1_score: float = Field(default=0.0, ge=0.0, le=1.0)
    training_data_size: int = Field(default=0, ge=0)
    last_trained: datetime
    hyperparameters: Dict[str, Any] = Field(default_factory=dict)


class AIModelMetricsCreate(AIModelMetricsBase):
    pass


class AIModelMetrics(AIModelMetricsBase):
    id: UUID
    tenant_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True