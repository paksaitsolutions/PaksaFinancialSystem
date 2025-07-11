"""
Schemas for AI/ML endpoints.
"""
from pydantic import BaseModel
from typing import List, Any

class AnomalyDetectionRequest(BaseModel):
    data: List[Any]

class AnomalyDetectionResult(BaseModel):
    anomalies: List[Any]

class ForecastingRequest(BaseModel):
    data: List[Any]

class ForecastingResult(BaseModel):
    forecast: List[Any]

class RecommendationRequest(BaseModel):
    context: dict

class RecommendationResult(BaseModel):
    recommendations: List[Any]
