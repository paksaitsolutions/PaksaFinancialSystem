"""
Schemas for AI-powered collections insights.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import date
from decimal import Decimal
from pydantic import BaseModel

class CustomerRiskProfile(BaseModel):
    """Schema for customer risk assessment."""
    customer_id: UUID
    customer_name: str
    risk_score: float  # 0-100, higher = riskier
    risk_level: str  # low, medium, high, critical
    payment_behavior: str
    days_sales_outstanding: int
    total_outstanding: Decimal
    overdue_amount: Decimal
    payment_history_score: float
    credit_utilization: float
    recommended_action: str

class CollectionPrediction(BaseModel):
    """Schema for collection probability prediction."""
    invoice_id: UUID
    customer_id: UUID
    invoice_number: str
    amount: Decimal
    days_overdue: int
    collection_probability: float  # 0-1
    predicted_collection_date: Optional[date] = None
    recommended_strategy: str
    confidence_level: float

class CollectionsInsights(BaseModel):
    """Schema for overall collections insights."""
    total_outstanding: Decimal
    high_risk_customers: int
    predicted_collections_30_days: Decimal
    collection_efficiency_score: float
    top_risks: List[CustomerRiskProfile]
    urgent_actions: List[Dict[str, Any]]
    trends: Dict[str, Any]

class CollectionStrategy(BaseModel):
    """Schema for AI-recommended collection strategy."""
    customer_id: UUID
    strategy_type: str  # email, call, legal, discount
    priority: int  # 1-5
    message_template: str
    timing: str
    expected_outcome: str
    success_probability: float