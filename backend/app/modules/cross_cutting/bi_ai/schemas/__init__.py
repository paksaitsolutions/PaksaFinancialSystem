"""
BI/AI Module Schemas

This module contains all Pydantic schemas for the Business Intelligence
and Artificial Intelligence components.
"""

# Import all schemas to make them available from bi_ai.schemas
from .core import (
    # Base schemas
    BaseSchema, BaseCreateSchema, BaseUpdateSchema, BaseInDBBase,
    
    # Common field types
    PyObjectId, UUIDModelMixin, TimestampMixin, AuditMixin,
    
    # Enums
    AIModelType, AIModelFramework, AIModelStatus,
    DataSourceType, DataSourceStatus, ScheduleFrequency,
    PipelineStatus, TransformationType, ReportFormat,
    ReportFrequency, KPIType, TimeRange
)

# Import model-specific schemas
from .ai_model import (
    AIModelCreate, AIModelUpdate, AIModelInDB,
    AIModelVersionCreate, AIModelVersionUpdate, AIModelVersionInDB,
    AIModelDeploymentCreate, AIModelDeploymentUpdate, AIModelDeploymentInDB,
    AIModelDeploymentStatus
)

from .data_source import (
    DataSourceCreate, DataSourceUpdate, DataSourceInDB,
    DataPipelineCreate, DataPipelineUpdate, DataPipelineInDB,
    DataTransformationCreate, DataTransformationUpdate, DataTransformationInDB
)

from .analytics import (
    ReportDefinitionCreate, ReportDefinitionUpdate, ReportDefinitionInDB,
    DashboardDefinitionCreate, DashboardDefinitionUpdate, DashboardDefinitionInDB,
    KPICreate, KPIUpdate, KPIInDB,
    
    # Request/Response schemas
    PredictionRequest, PredictionResponse,
    AnomalyDetectionRequest, AnomalyDetectionResponse,
    ForecastingRequest, ForecastingResponse,
    ReportRequest, ReportResponse,
    KPIValue, KPITrend, KPIDataPoint
)

# Re-export commonly used types
__all__ = [
    # Base schemas
    'BaseSchema', 'BaseCreateSchema', 'BaseUpdateSchema', 'BaseInDBBase',
    
    # Common field types
    'PyObjectId', 'UUIDModelMixin', 'TimestampMixin', 'AuditMixin',
    
    # Enums
    'AIModelType', 'AIModelFramework', 'AIModelStatus',
    'DataSourceType', 'DataSourceStatus', 'ScheduleFrequency',
    'PipelineStatus', 'TransformationType', 'ReportFormat',
    'ReportFrequency', 'KPIType', 'TimeRange',
    
    # AI Model schemas
    'AIModelCreate', 'AIModelUpdate', 'AIModelInDB',
    'AIModelVersionCreate', 'AIModelVersionUpdate', 'AIModelVersionInDB',
    'AIModelDeploymentCreate', 'AIModelDeploymentUpdate', 'AIModelDeploymentInDB',
    'AIModelDeploymentStatus',
    
    # Data Source schemas
    'DataSourceCreate', 'DataSourceUpdate', 'DataSourceInDB',
    'DataPipelineCreate', 'DataPipelineUpdate', 'DataPipelineInDB',
    'DataTransformationCreate', 'DataTransformationUpdate', 'DataTransformationInDB',
    
    # Analytics schemas
    'ReportDefinitionCreate', 'ReportDefinitionUpdate', 'ReportDefinitionInDB',
    'DashboardDefinitionCreate', 'DashboardDefinitionUpdate', 'DashboardDefinitionInDB',
    'KPICreate', 'KPIUpdate', 'KPIInDB',
    
    # Request/Response schemas
    'PredictionRequest', 'PredictionResponse',
    'AnomalyDetectionRequest', 'AnomalyDetectionResponse',
    'ForecastingRequest', 'ForecastingResponse',
    'ReportRequest', 'ReportResponse',
    'KPIValue', 'KPITrend', 'KPIDataPoint'
]
