"""
AI Model Schemas

This module contains Pydantic schemas for AI/ML model management,
including models, versions, and deployments.
"""
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union, Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator, HttpUrl, Json

from .core import (
    BaseSchema, BaseCreateSchema, BaseUpdateSchema, BaseInDBBase,
    UUIDModelMixin, TimestampMixin, AuditMixin,
    AIModelType, AIModelFramework, AIModelStatus,
    Response, PaginatedResponse, ErrorResponse, ErrorDetail,
    Relationship, RelationshipData, Metadata, DateRangeFilter
)

# --- AI Model ---
class AIModelBase(BaseSchema):
    ""Base schema for AI model with common fields."""
    name: str = Field(..., max_length=255, description="Name of the AI model")
    description: Optional[str] = Field(None, description="Description of the model")
    model_type: AIModelType = Field(..., description="Type of the AI model")
    framework: AIModelFramework = Field(..., description="Framework used to build the model")
    status: AIModelStatus = Field(default=AIModelStatus.DRAFT, description="Current status of the model")
    
    # Model metadata
    input_schema: Optional[Dict[str, Any]] = Field(
        None,
        description="JSON Schema for validating model inputs"
    )
    output_schema: Optional[Dict[str, Any]] = Field(
        None,
        description="JSON Schema for validating model outputs"
    )
    parameters: Optional[Dict[str, Any]] = Field(
        None,
        description="Model hyperparameters and configuration"
    )
    metrics: Optional[Dict[str, float]] = Field(
        None,
        description="Training and evaluation metrics"
    )
    
    # Relationships (as IDs)
    data_source_ids: List[UUID] = Field(
        default_factory=list,
        description="IDs of data sources used for training"
    )

class AIModelCreate(BaseCreateSchema, AIModelBase):
    ""Schema for creating a new AI model."""
    pass

class AIModelUpdate(BaseUpdateSchema):
    ""Schema for updating an existing AI model."""
    name: Optional[str] = Field(None, max_length=255, description="Name of the AI model")
    description: Optional[str] = Field(None, description="Description of the model")
    status: Optional[AIModelStatus] = Field(None, description="Current status of the model")
    input_schema: Optional[Dict[str, Any]] = Field(
        None,
        description="JSON Schema for validating model inputs"
    )
    output_schema: Optional[Dict[str, Any]] = Field(
        None,
        description="JSON Schema for validating model outputs"
    )
    parameters: Optional[Dict[str, Any]] = Field(
        None,
        description="Model hyperparameters and configuration"
    )
    metrics: Optional[Dict[str, float]] = Field(
        None,
        description="Training and evaluation metrics"
    )
    data_source_ids: Optional[List[UUID]] = Field(
        None,
        description="IDs of data sources used for training"
    )

class AIModelInDB(BaseInDBBase, AIModelBase):
    ""Schema for AI model as stored in the database."""
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    class Config:
        orm_mode = True

# --- AI Model Version ---
class AIModelVersionBase(BaseSchema):
    ""Base schema for AI model version with common fields."""
    version: str = Field(..., max_length=50, description="Version identifier (e.g., '1.0.0')")
    
    # Model artifacts
    artifact_uri: Optional[str] = Field(
        None,
        description="URI to the model artifact files (e.g., S3 path)"
    )
    code_version: Optional[str] = Field(
        None,
        max_length=100,
        description="Version control commit hash or tag"
    )
    
    # Training metadata
    training_data_range_start: Optional[datetime] = Field(
        None,
        description="Start date/time of the training data"
    )
    training_data_range_end: Optional[datetime] = Field(
        None,
        description="End date/time of the training data"
    )
    training_parameters: Optional[Dict[str, Any]] = Field(
        None,
        description="Parameters used during training"
    )
    training_metrics: Optional[Dict[str, float]] = Field(
        None,
        description="Metrics from the training process"
    )
    
    # Model ID (relationship)
    model_id: UUID = Field(..., description="ID of the parent AI model")

class AIModelVersionCreate(BaseCreateSchema, AIModelVersionBase):
    ""Schema for creating a new AI model version."""
    pass

class AIModelVersionUpdate(BaseUpdateSchema):
    ""Schema for updating an existing AI model version."""
    version: Optional[str] = Field(None, max_length=50, description="Version identifier")
    artifact_uri: Optional[str] = Field(None, description="URI to the model artifact files")
    code_version: Optional[str] = Field(None, max_length=100, description="Version control commit hash or tag")
    training_parameters: Optional[Dict[str, Any]] = Field(None, description="Parameters used during training")
    training_metrics: Optional[Dict[str, float]] = Field(None, description="Metrics from the training process")

class AIModelVersionInDB(BaseInDBBase, AIModelVersionBase):
    ""Schema for AI model version as stored in the database."""
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    
    class Config:
        orm_mode = True

# --- AI Model Deployment ---
class AIModelDeploymentStatus(str, Enum):
    ""Status of an AI model deployment."""
    PENDING = "pending"
    DEPLOYING = "deploying"
    ACTIVE = "active"
    FAILED = "failed"
    UPDATING = "updating"
    ROLLING_BACK = "rolling_back"
    DELETED = "deleted"

class AIModelDeploymentBase(BaseSchema):
    ""Base schema for AI model deployment with common fields."""
    name: str = Field(..., max_length=255, description="Name of the deployment")
    environment: str = Field(..., max_length=100, description="Deployment environment (e.g., 'staging', 'production')")
    status: AIModelDeploymentStatus = Field(
        default=AIModelDeploymentStatus.PENDING,
        description="Current status of the deployment"
    )
    endpoint_url: Optional[HttpUrl] = Field(
        None,
        description="URL of the deployed model endpoint"
    )
    
    # Scaling and resource configuration
    min_replicas: int = Field(
        default=1,
        ge=0,
        description="Minimum number of replicas to run"
    )
    max_replicas: int = Field(
        default=1,
        ge=1,
        description="Maximum number of replicas to scale to"
    )
    
    # Monitoring
    request_count: int = Field(
        default=0,
        ge=0,
        description="Total number of requests processed"
    )
    avg_latency_ms: Optional[float] = Field(
        None,
        ge=0,
        description="Average request latency in milliseconds"
    )
    error_rate: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Error rate as a fraction of total requests"
    )
    
    # Relationships (as IDs)
    model_id: UUID = Field(..., description="ID of the AI model")
    model_version_id: UUID = Field(..., description="ID of the model version")

class AIModelDeploymentCreate(BaseCreateSchema, AIModelDeploymentBase):
    ""Schema for creating a new AI model deployment."""
    pass

class AIModelDeploymentUpdate(BaseUpdateSchema):
    ""Schema for updating an existing AI model deployment."""
    name: Optional[str] = Field(None, max_length=255, description="Name of the deployment")
    environment: Optional[str] = Field(None, max_length=100, description="Deployment environment")
    status: Optional[AIModelDeploymentStatus] = Field(None, description="Current status of the deployment")
    endpoint_url: Optional[HttpUrl] = Field(None, description="URL of the deployed model endpoint")
    min_replicas: Optional[int] = Field(None, ge=0, description="Minimum number of replicas to run")
    max_replicas: Optional[int] = Field(None, ge=1, description="Maximum number of replicas to scale to")
    
    @validator('max_replicas')
    def validate_max_replicas(cls, v, values):
        if 'min_replicas' in values and v is not None and values['min_replicas'] is not None:
            if v < values['min_replicas']:
                raise ValueError("max_replicas must be greater than or equal to min_replicas")
        return v

class AIModelDeploymentInDB(BaseInDBBase, AIModelDeploymentBase):
    ""Schema for AI model deployment as stored in the database."""
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    deployed_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    class Config:
        orm_mode = True

# --- Request/Response Schemas ---
class ModelPredictionRequest(BaseModel):
    ""Schema for model prediction requests."""
    model_id: UUID = Field(..., description="ID of the model to use for prediction")
    deployment_id: Optional[UUID] = Field(
        None,
        description="ID of a specific deployment to use (optional)"
    )
    input_data: Union[Dict[str, Any], List[Dict[str, Any]]] = Field(
        ...,
        description="Input data for prediction (single example or batch)"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "model_id": "550e8400-e29b-41d4-a716-446655440000",
                "input_data": {
                    "feature1": 0.5,
                    "feature2": "some_value"
                }
            }
        }

class ModelPredictionResponse(BaseModel):
    ""Schema for model prediction responses."""
    model_id: UUID = Field(..., description="ID of the model used for prediction")
    deployment_id: Optional[UUID] = Field(None, description="ID of the deployment used")
    prediction: Union[Dict[str, Any], List[Dict[str, Any]]] = Field(
        ...,
        description="Prediction results (single example or batch)"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional metadata about the prediction"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "model_id": "550e8400-e29b-41d4-a716-446655440000",
                "prediction": {
                    "class": "positive",
                    "probability": 0.95
                },
                "metadata": {
                    "model_version": "1.0.0",
                    "inference_time_ms": 45.2
                }
            }
        }

# --- Relationship Schemas ---
class AIModelWithRelationships(AIModelInDB):
    ""AI model with relationships included."""
    versions: List[AIModelVersionInDB] = Field(
        default_factory=list,
        description="List of model versions"
    )
    deployments: List[AIModelDeploymentInDB] = Field(
        default_factory=list,
        description="List of model deployments"
    )
    data_sources: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of data sources used for training"
    )

class AIModelVersionWithRelationships(AIModelVersionInDB):
    ""AI model version with relationships included."""
    model: Optional[AIModelInDB] = Field(None, description="Parent AI model")
    deployments: List[AIModelDeploymentInDB] = Field(
        default_factory=list,
        description="List of deployments using this version"
    )

class AIModelDeploymentWithRelationships(AIModelDeploymentInDB):
    ""AI model deployment with relationships included."""
    model: Optional[AIModelInDB] = Field(None, description="Parent AI model")
    model_version: Optional[AIModelVersionInDB] = Field(None, description="Model version being deployed")

# --- Response Wrappers ---
class AIModelResponse(Response[AIModelWithRelationships]):
    ""Response wrapper for a single AI model."""
    data: AIModelWithRelationships

class AIModelListResponse(PaginatedResponse[AIModelInDB]):
    ""Response wrapper for a paginated list of AI models."""
    pass

class AIModelVersionResponse(Response[AIModelVersionWithRelationships]):
    ""Response wrapper for a single AI model version."""
    data: AIModelVersionWithRelationships

class AIModelVersionListResponse(PaginatedResponse[AIModelVersionInDB]):
    ""Response wrapper for a paginated list of AI model versions."""
    pass

class AIModelDeploymentResponse(Response[AIModelDeploymentWithRelationships]):
    ""Response wrapper for a single AI model deployment."""
    data: AIModelDeploymentWithRelationships

class AIModelDeploymentListResponse(PaginatedResponse[AIModelDeploymentInDB]):
    ""Response wrapper for a paginated list of AI model deployments."""
    pass
