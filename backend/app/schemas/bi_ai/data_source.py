"""
Data Source Schemas

This module contains Pydantic schemas for data source management,
including data sources, pipelines, and transformations.
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator, HttpUrl, Json, SecretStr

from .core import (
    BaseSchema, BaseCreateSchema, BaseUpdateSchema, BaseInDBBase,
    UUIDModelMixin, TimestampMixin, AuditMixin,
    DataSourceType, DataSourceStatus, ScheduleFrequency,
    Response, PaginatedResponse, ErrorResponse, ErrorDetail,
    Relationship, RelationshipData, Metadata, DateRangeFilter
)

# --- Data Source ---
class DataSourceBase(BaseSchema):
    ""Base schema for data source with common fields."""
    name: str = Field(..., max_length=255, description="Name of the data source")
    description: Optional[str] = Field(None, description="Description of the data source")
    type: DataSourceType = Field(..., description="Type of the data source")
    status: DataSourceStatus = Field(
        default=DataSourceStatus.ACTIVE,
        description="Current status of the data source"
    )
    
    # Connection details (encrypted in production)
    connection_details: Dict[str, Any] = Field(
        ...,
        description="Connection details specific to the data source type"
    )
    
    # Schema information
    schema_info: Optional[Dict[str, Any]] = Field(
        None,
        description="Schema information for the data source"
    )
    
    # Refresh configuration
    refresh_schedule: Optional[str] = Field(
        None,
        description="Cron expression for scheduled refreshes"
    )
    refresh_frequency: Optional[ScheduleFrequency] = Field(
        None,
        description="Frequency of scheduled refreshes"
    )
    last_refreshed_at: Optional[datetime] = Field(
        None,
        description="Timestamp of the last successful refresh"
    )

class DataSourceCreate(BaseCreateSchema, DataSourceBase):
    ""Schema for creating a new data source."""
    pass

class DataSourceUpdate(BaseUpdateSchema):
    ""Schema for updating an existing data source."""
    name: Optional[str] = Field(None, max_length=255, description="Name of the data source")
    description: Optional[str] = Field(None, description="Description of the data source")
    status: Optional[DataSourceStatus] = Field(None, description="Current status of the data source")
    connection_details: Optional[Dict[str, Any]] = Field(
        None,
        description="Connection details specific to the data source type"
    )
    schema_info: Optional[Dict[str, Any]] = Field(
        None,
        description="Schema information for the data source"
    )
    refresh_schedule: Optional[str] = Field(
        None,
        description="Cron expression for scheduled refreshes"
    )
    refresh_frequency: Optional[ScheduleFrequency] = Field(
        None,
        description="Frequency of scheduled refreshes"
    )

    @validator('connection_details', pre=True)
    def validate_connection_details(cls, v, values):
        # Add validation for connection details based on data source type
        if 'type' in values and values['type'] == 'database':
            required_fields = ['host', 'port', 'database', 'username']
            if not all(field in v for field in required_fields):
                raise ValueError(f"Database connection requires {required_fields}")
        return v

class DataSourceInDB(BaseInDBBase, DataSourceBase):
    ""Schema for data source as stored in the database."""
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    class Config:
        orm_mode = True

# --- Data Pipeline ---
class DataPipelineBase(BaseSchema):
    ""Base schema for data pipeline with common fields."""
    name: str = Field(..., max_length=255, description="Name of the data pipeline")
    description: Optional[str] = Field(None, description="Description of the pipeline")
    
    # Source configuration
    data_source_id: UUID = Field(..., description="ID of the source data source")
    
    # Pipeline configuration
    status: str = Field(
        default="active",
        description="Current status of the pipeline (active, paused, error)"
    )
    schedule: Optional[str] = Field(
        None,
        description="Cron expression for scheduled pipeline runs"
    )
    
    # Processing details
    last_run_at: Optional[datetime] = Field(
        None,
        description="Timestamp of the last pipeline run"
    )
    last_run_status: Optional[str] = Field(
        None,
        description="Status of the last pipeline run"
    )
    last_error: Optional[str] = Field(
        None,
        description="Error message from the last failed run"
    )

class DataPipelineCreate(BaseCreateSchema, DataPipelineBase):
    ""Schema for creating a new data pipeline."""
    pass

class DataPipelineUpdate(BaseUpdateSchema):
    ""Schema for updating an existing data pipeline."""
    name: Optional[str] = Field(None, max_length=255, description="Name of the data pipeline")
    description: Optional[str] = Field(None, description="Description of the pipeline")
    status: Optional[str] = Field(None, description="Current status of the pipeline")
    schedule: Optional[str] = Field(None, description="Cron expression for scheduled runs")
    last_run_status: Optional[str] = Field(None, description="Status of the last run")
    last_error: Optional[str] = Field(None, description="Error message from the last failed run")

class DataPipelineInDB(BaseInDBBase, DataPipelineBase):
    ""Schema for data pipeline as stored in the database."""
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    class Config:
        orm_mode = True

# --- Data Transformation ---
class DataTransformationBase(BaseSchema):
    ""Base schema for data transformation with common fields."""
    name: str = Field(..., max_length=255, description="Name of the transformation")
    description: Optional[str] = Field(None, description="Description of the transformation")
    type: str = Field(..., description="Type of transformation (sql_query, python_script, builtin_function)")
    
    # Transformation configuration
    config: Dict[str, Any] = Field(
        ...,
        description="Configuration specific to the transformation type"
    )
    
    # Execution order
    order: int = Field(
        default=0,
        ge=0,
        description="Execution order within the pipeline"
    )
    
    # Pipeline ID (relationship)
    pipeline_id: UUID = Field(..., description="ID of the parent pipeline")

class DataTransformationCreate(BaseCreateSchema, DataTransformationBase):
    ""Schema for creating a new data transformation."""
    pass

class DataTransformationUpdate(BaseUpdateSchema):
    ""Schema for updating an existing data transformation."""
    name: Optional[str] = Field(None, max_length=255, description="Name of the transformation")
    description: Optional[str] = Field(None, description="Description of the transformation")
    type: Optional[str] = Field(None, description="Type of transformation")
    config: Optional[Dict[str, Any]] = Field(
        None,
        description="Configuration specific to the transformation type"
    )
    order: Optional[int] = Field(None, ge=0, description="Execution order within the pipeline")

class DataTransformationInDB(BaseInDBBase, DataTransformationBase):
    ""Schema for data transformation as stored in the database."""
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    class Config:
        orm_mode = True

# --- Relationship Schemas ---
class DataSourceWithRelationships(DataSourceInDB):
    ""Data source with relationships included."""
    pipelines: List[DataPipelineInDB] = Field(
        default_factory=list,
        description="List of pipelines using this data source"
    )

class DataPipelineWithRelationships(DataPipelineInDB):
    ""Data pipeline with relationships included."""
    data_source: Optional[DataSourceInDB] = Field(
        None,
        description="Source data source"
    )
    transformations: List[DataTransformationInDB] = Field(
        default_factory=list,
        description="List of transformations in this pipeline"
    )

class DataTransformationWithRelationships(DataTransformationInDB):
    ""Data transformation with relationships included."""
    pipeline: Optional[DataPipelineInDB] = Field(
        None,
        description="Parent pipeline"
    )

# --- Request/Response Schemas ---
class DataSourceTestRequest(BaseModel):
    ""Schema for testing data source connections."""
    type: DataSourceType = Field(..., description="Type of the data source")
    connection_details: Dict[str, Any] = Field(
        ...,
        description="Connection details to test"
    )

class DataSourceTestResponse(BaseModel):
    ""Response schema for data source connection tests."""
    success: bool = Field(..., description="Whether the connection was successful")
    message: Optional[str] = Field(None, description="Status message")
    error: Optional[str] = Field(None, description="Error message if connection failed")
    schema_info: Optional[Dict[str, Any]] = Field(
        None,
        description="Schema information if connection was successful"
    )

class DataPipelineRunRequest(BaseModel):
    ""Schema for running a data pipeline."""
    pipeline_id: UUID = Field(..., description="ID of the pipeline to run")
    force: bool = Field(
        default=False,
        description="Whether to force run even if not scheduled"
    )

class DataPipelineRunResponse(BaseModel):
    ""Response schema for pipeline run requests."""
    run_id: UUID = Field(..., description="ID of the pipeline run")
    status: str = Field(..., description="Status of the run (started, queued, failed)")
    message: Optional[str] = Field(None, description="Status message")

# --- Response Wrappers ---
class DataSourceResponse(Response[DataSourceWithRelationships]):
    ""Response wrapper for a single data source."""
    data: DataSourceWithRelationships

class DataSourceListResponse(PaginatedResponse[DataSourceInDB]):
    ""Response wrapper for a paginated list of data sources."""
    pass

class DataPipelineResponse(Response[DataPipelineWithRelationships]):
    ""Response wrapper for a single data pipeline."""
    data: DataPipelineWithRelationships

class DataPipelineListResponse(PaginatedResponse[DataPipelineInDB]):
    ""Response wrapper for a paginated list of data pipelines."""
    pass

class DataTransformationResponse(Response[DataTransformationWithRelationships]):
    ""Response wrapper for a single data transformation."""
    data: DataTransformationWithRelationships

class DataTransformationListResponse(PaginatedResponse[DataTransformationInDB]):
    ""Response wrapper for a paginated list of data transformations."""
    pass
