"""
Tax Analytics Schemas

This module contains Pydantic schemas for tax analytics and reporting.
"""
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, validator

from app.modules.cross_cutting.bi_ai.schemas import AIInsights


class TaxPeriod(str, Enum):
    """Enum for tax period types."""
    CURRENT_MONTH = "current_month"
    CURRENT_QUARTER = "current_quarter"
    CURRENT_YEAR = "current_year"
    CUSTOM = "custom"


class TaxMetrics(BaseModel):
    """Tax metrics for a specific period."""
    total_tax: float = Field(..., description="Total tax amount for the period")
    avg_tax_per_employee: float = Field(..., description="Average tax per employee")
    compliance_rate: float = Field(..., description="Tax compliance rate as a percentage")
    exemption_usage: Dict[str, float] = Field(..., description="Tax exemption usage by type")
    jurisdictional_breakdown: Dict[str, float] = Field(..., description="Tax breakdown by jurisdiction")


class TaxAnalyticsRequest(BaseModel):
    """Request schema for tax analytics."""
    period: TaxPeriod = Field(..., description="Time period for analysis")
    start_date: Optional[datetime] = Field(None, description="Start date for custom period")
    end_date: Optional[datetime] = Field(None, description="End date for custom period")
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        if v and 'start_date' in values and values['start_date'] and v < values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v


class TaxAnalyticsResponse(BaseModel):
    """Response schema for tax analytics."""
    metrics: TaxMetrics = Field(..., description="Tax metrics")
    insights: AIInsights = Field(..., description="AI-powered insights")
    period: Dict[str, datetime] = Field(..., description="Date range for analysis")


class TaxComplianceMetrics(BaseModel):
    """Metrics for tax compliance analysis."""
    compliance_rate: float = Field(..., description="Overall compliance rate")
    compliant_transactions: int = Field(..., description="Number of compliant transactions")
    non_compliant_transactions: int = Field(..., description="Number of non-compliant transactions")
    compliance_by_type: Dict[str, float] = Field(..., description="Compliance rate by tax type")


class TaxOptimizationRecommendations(BaseModel):
    """Tax optimization recommendations."""
    potential_savings: float = Field(..., description="Estimated potential tax savings")
    recommended_actions: List[str] = Field(..., description="List of recommended optimization actions")
    risk_level: str = Field(..., description="Risk level of optimization recommendations")


class TaxRiskAssessment(BaseModel):
    """Tax risk assessment."""
    overall_risk_score: float = Field(..., description="Overall tax risk score")
    risk_factors: List[str] = Field(..., description="List of identified risk factors")
    mitigation_strategies: List[str] = Field(..., description="List of recommended mitigation strategies")
