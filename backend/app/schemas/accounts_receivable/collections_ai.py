"""
Collections AI schemas.
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import date

class CollectionPredictionRequest(BaseModel):
    customer_id: str
    
class CollectionPredictionResponse(BaseModel):
    customer_id: str
    payment_probability: float = Field(..., ge=0, le=1)
    risk_score: float = Field(..., ge=0, le=1)
    recommended_action: str
    
class OverdueAccountResponse(BaseModel):
    customer_id: str
    customer_name: str
    overdue_amount: float
    days_overdue: int
    risk_score: float

class CustomerRiskProfile(BaseModel):
    customer_id: str
    risk_score: float
    payment_history: str
    credit_rating: str

class CollectionPrediction(BaseModel):
    customer_id: str
    payment_probability: float
    predicted_payment_date: Optional[date] = None
    confidence_score: float

class CollectionsInsights(BaseModel):
    total_overdue: float
    high_risk_customers: int
    collection_efficiency: float
    recommendations: List[str]

class CollectionStrategy(BaseModel):
    customer_id: str
    strategy_type: str
    priority_level: str
    recommended_actions: List[str]
    follow_up_date: date