"""
BI/AI Module

This module provides business intelligence and artificial intelligence capabilities
across all financial modules, including analytics, reporting, and predictive insights.
"""

from fastapi import APIRouter
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from enum import Enum

# Import core components
from .models import (
    AIModel, AIModelVersion, AIModelDeployment,
    ReportDefinition, DashboardDefinition, KPI,
    DataSource, DataPipeline, DataTransformation
)

# Import services
from .services import (
    AnalyticsService, AIService, ReportService,
    AnomalyDetectionService, ForecastingService
)

# Import schemas
from .schemas import (
    # Core schemas
    AIModelSchema, AIModelVersionSchema, AIModelDeploymentSchema,
    ReportDefinitionSchema, DashboardDefinitionSchema, KPISchema,
    DataSourceSchema, DataPipelineSchema, DataTransformationSchema,
    
    # Request/Response schemas
    PredictionRequest, PredictionResponse,
    AnomalyDetectionRequest, AnomalyDetectionResponse,
    ForecastingRequest, ForecastingResponse,
    ReportRequest, ReportResponse
)

# Initialize services
def get_analytics_service():
    """Factory function to get an AnalyticsService instance."""
    return AnalyticsService()

def get_ai_service():
    """Factory function to get an AIService instance."""
    return AIService()

def get_report_service():
    """Factory function to get a ReportService instance."""
    return ReportService()

# Module metadata
MODULE_NAME = "bi_ai"
MODULE_DESCRIPTION = "Business Intelligence and Artificial Intelligence services"

# Export the router to be included in the main FastAPI app
router = APIRouter()

# Export models for Alembic migrations
__all__ = [
    # Models
    'AIModel', 'AIModelVersion', 'AIModelDeployment',
    'ReportDefinition', 'DashboardDefinition', 'KPI',
    'DataSource', 'DataPipeline', 'DataTransformation',
    
    # Services
    'AnalyticsService', 'AIService', 'ReportService',
    'AnomalyDetectionService', 'ForecastingService',
    
    # Schemas
    'AIModelSchema', 'AIModelVersionSchema', 'AIModelDeploymentSchema',
    'ReportDefinitionSchema', 'DashboardDefinitionSchema', 'KPISchema',
    'DataSourceSchema', 'DataPipelineSchema', 'DataTransformationSchema',
    'PredictionRequest', 'PredictionResponse',
    'AnomalyDetectionRequest', 'AnomalyDetectionResponse',
    'ForecastingRequest', 'ForecastingResponse',
    'ReportRequest', 'ReportResponse',
    
    # Factory functions
    'get_analytics_service', 'get_ai_service', 'get_report_service',
    
    # Router
    'router'
]
