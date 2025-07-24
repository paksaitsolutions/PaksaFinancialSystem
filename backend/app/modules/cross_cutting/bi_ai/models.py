"""
BI/AI Database Models

This module defines the SQLAlchemy models for the Business Intelligence
and Artificial Intelligence components.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from enum import Enum as PyEnum
from uuid import UUID, uuid4

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, 
    ForeignKey, JSON, Text, Enum, Table, BigInteger, Numeric,
    event
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func

from app.core.db.base import Base

# Association tables for many-to-many relationships
model_data_sources = Table(
    'ai_model_data_sources', Base.metadata,
    Column('model_id', PG_UUID(as_uuid=True), ForeignKey('ai_models.id')),
    Column('data_source_id', PG_UUID(as_uuid=True), ForeignKey('data_sources.id'))
)

dashboard_kpis = Table(
    'dashboard_kpis', Base.metadata,
    Column('dashboard_id', PG_UUID(as_uuid=True), ForeignKey('dashboards.id')),
    Column('kpi_id', PG_UUID(as_uuid=True), ForeignKey('kpis.id'))
)

class AIModelStatus(str, PyEnum):    
    DRAFT = "draft"
    TRAINING = "training"
    ACTIVE = "active"
    ARCHIVED = "archived"
    ERROR = "error"

class AIModelType(str, PyEnum):
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    TIME_SERIES = "time_series"
    NLP = "nlp"
    COMPUTER_VISION = "computer_vision"
    RECOMMENDATION = "recommendation"
    ANOMALY_DETECTION = "anomaly_detection"
    FORECASTING = "forecasting"

class AIModelFramework(str, PyEnum):
    TENSORFLOW = "tensorflow"
    PYTORCH = "pytorch"
    SCIKIT_LEARN = "scikit-learn"
    HUGGINGFACE = "huggingface"
    XGBOOST = "xgboost"
    LIGHTGBM = "lightgbm"
    SPACY = "spacy"
    PROPHET = "prophet"
    CUSTOM = "custom"

class DataSourceType(str, PyEnum):
    DATABASE = "database"
    API = "api"
    FILE = "file"
    STREAM = "stream"
    DATA_WAREHOUSE = "data_warehouse"
    DATA_LAKE = "data_lake"

class DataSourceStatus(str, PyEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    SYNCING = "syncing"

class ScheduleFrequency(str, PyEnum):
    MINUTELY = "minutely"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    ON_DEMAND = "on_demand"

class AIModel(Base):
    """
    Represents an AI/ML model used for predictions and analytics.
    """
    __tablename__ = "ai_models"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    model_type = Column(Enum(AIModelType), nullable=False)
    framework = Column(Enum(AIModelFramework), nullable=False)
    status = Column(Enum(AIModelStatus), default=AIModelStatus.DRAFT, nullable=False)
    
    # Model metadata
    input_schema = Column(JSONB, nullable=True)  # JSON Schema for input validation
    output_schema = Column(JSONB, nullable=True)  # JSON Schema for output validation
    parameters = Column(JSONB, nullable=True)     # Model hyperparameters
    metrics = Column(JSONB, nullable=True)        # Training/validation metrics
    
    # Data sources used for training
    data_sources = relationship(
        "DataSource",
        secondary=model_data_sources,
        back_populates="ai_models"
    )
    
    # Relationships
    versions = relationship("AIModelVersion", back_populates="model", cascade="all, delete-orphan")
    deployments = relationship("AIModelDeployment", back_populates="model", cascade="all, delete-orphan")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Audit fields
    created_by = Column(String(255), nullable=True)
    updated_by = Column(String(255), nullable=True)
    
    def __repr__(self):
        return f"<AIModel(id={self.id}, name='{self.name}', type='{self.model_type}')>"

class AIModelVersion(Base):
    """
    Represents a specific version of an AI/ML model.
    """
    __tablename__ = "ai_model_versions"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    model_id = Column(PG_UUID(as_uuid=True), ForeignKey('ai_models.id', ondelete='CASCADE'), nullable=False)
    version = Column(String(50), nullable=False)
    
    # Model artifacts
    artifact_uri = Column(String(512), nullable=True)  # Path to model files
    code_version = Column(String(100), nullable=True)  # Git commit hash
    
    # Training metadata
    training_data_range_start = Column(DateTime(timezone=True), nullable=True)
    training_data_range_end = Column(DateTime(timezone=True), nullable=True)
    training_parameters = Column(JSONB, nullable=True)
    training_metrics = Column(JSONB, nullable=True)
    
    # Relationships
    model = relationship("AIModel", back_populates="versions")
    deployments = relationship("AIModelDeployment", back_populates="model_version", cascade="all, delete-orphan")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Audit fields
    created_by = Column(String(255), nullable=True)
    
    def __repr__(self):
        return f"<AIModelVersion(id={self.id}, model_id={self.model_id}, version='{self.version}')>"

class AIModelDeployment(Base):
    """
    Represents a deployment of an AI model version to a serving environment.
    """
    __tablename__ = "ai_model_deployments"
    
    class DeploymentStatus(str, PyEnum):
        PENDING = "pending"
        DEPLOYING = "deploying"
        ACTIVE = "active"
        FAILED = "failed"
        UPDATING = "updating"
        ROLLING_BACK = "rolling_back"
        DELETED = "deleted"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    model_id = Column(PG_UUID(as_uuid=True), ForeignKey('ai_models.id', ondelete='CASCADE'), nullable=False)
    model_version_id = Column(PG_UUID(as_uuid=True), ForeignKey('ai_model_versions.id', ondelete='CASCADE'), nullable=False)
    
    # Deployment configuration
    name = Column(String(255), nullable=False)
    environment = Column(String(100), nullable=False)  # e.g., 'staging', 'production'
    status = Column(Enum(DeploymentStatus), default=DeploymentStatus.PENDING, nullable=False)
    endpoint_url = Column(String(512), nullable=True)
    
    # Scaling and resource configuration
    min_replicas = Column(Integer, default=1, nullable=False)
    max_replicas = Column(Integer, default=1, nullable=False)
    
    # Monitoring
    request_count = Column(BigInteger, default=0, nullable=False)
    avg_latency_ms = Column(Float, nullable=True)
    error_rate = Column(Float, default=0.0, nullable=False)
    
    # Relationships
    model = relationship("AIModel", back_populates="deployments")
    model_version = relationship("AIModelVersion", back_populates="deployments")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deployed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Audit fields
    created_by = Column(String(255), nullable=True)
    updated_by = Column(String(255), nullable=True)
    
    def __repr__(self):
        return f"<AIModelDeployment(id={self.id}, name='{self.name}', status='{self.status}')>"

class DataSource(Base):
    """
    Represents a data source that can be used for analytics and model training.
    """
    __tablename__ = "data_sources"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    type = Column(Enum(DataSourceType), nullable=False)
    status = Column(Enum(DataSourceStatus), default=DataSourceStatus.ACTIVE, nullable=False)
    
    # Connection details (encrypted in production)
    connection_details = Column(JSONB, nullable=False)
    
    # Schema information
    schema_info = Column(JSONB, nullable=True)  # Schema of the data source
    
    # Refresh configuration
    refresh_schedule = Column(String(100), nullable=True)  # Cron expression
    refresh_frequency = Column(Enum(ScheduleFrequency), nullable=True)
    last_refreshed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    ai_models = relationship(
        "AIModel",
        secondary=model_data_sources,
        back_populates="data_sources"
    )
    pipelines = relationship("DataPipeline", back_populates="data_source", cascade="all, delete-orphan")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Audit fields
    created_by = Column(String(255), nullable=True)
    updated_by = Column(String(255), nullable=True)
    
    def __repr__(self):
        return f"<DataSource(id={self.id}, name='{self.name}', type='{self.type}')>"

class DataPipeline(Base):
    """
    Represents an ETL (Extract, Transform, Load) pipeline for data processing.
    """
    __tablename__ = "data_pipelines"
    
    class PipelineStatus(str, PyEnum):
        ACTIVE = "active"
        PAUSED = "paused"
        ERROR = "error"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Source configuration
    data_source_id = Column(PG_UUID(as_uuid=True), ForeignKey('data_sources.id', ondelete='CASCADE'), nullable=False)
    
    # Pipeline configuration
    status = Column(Enum(PipelineStatus), default=PipelineStatus.ACTIVE, nullable=False)
    schedule = Column(String(100), nullable=True)  # Cron expression
    
    # Processing details
    last_run_at = Column(DateTime(timezone=True), nullable=True)
    last_run_status = Column(String(50), nullable=True)
    last_error = Column(Text, nullable=True)
    
    # Relationships
    data_source = relationship("DataSource", back_populates="pipelines")
    transformations = relationship("DataTransformation", back_populates="pipeline", cascade="all, delete-orphan")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Audit fields
    created_by = Column(String(255), nullable=True)
    updated_by = Column(String(255), nullable=True)
    
    def __repr__(self):
        return f"<DataPipeline(id={self.id}, name='{self.name}')>"

class DataTransformation(Base):
    """
    Represents a transformation step in a data pipeline.
    """
    __tablename__ = "data_transformations"
    
    class TransformationType(str, PyEnum):
        SQL_QUERY = "sql_query"
        PYTHON_SCRIPT = "python_script"
        BUILTIN_FUNCTION = "builtin_function"
        
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    pipeline_id = Column(PG_UUID(as_uuid=True), ForeignKey('data_pipelines.id', ondelete='CASCADE'), nullable=False)
    
    # Transformation details
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    type = Column(Enum(TransformationType), nullable=False)
    
    # Transformation configuration
    config = Column(JSONB, nullable=False)  # Type-specific configuration
    
    # Execution order
    order = Column(Integer, nullable=False, default=0)
    
    # Relationships
    pipeline = relationship("DataPipeline", back_populates="transformations")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Audit fields
    created_by = Column(String(255), nullable=True)
    updated_by = Column(String(255), nullable=True)
    
    def __repr__(self):
        return f"<DataTransformation(id={self.id}, name='{self.name}', type='{self.type}')>"

class ReportDefinition(Base):
    """
    Defines a report template that can be generated on demand or scheduled.
    """
    __tablename__ = "report_definitions"
    
    class ReportFormat(str, PyEnum):
        PDF = "pdf"
        EXCEL = "excel"
        CSV = "csv"
        HTML = "html"
        
    class ReportFrequency(str, PyEnum):
        HOURLY = "hourly"
        DAILY = "daily"
        WEEKLY = "weekly"
        MONTHLY = "monthly"
        QUARTERLY = "quarterly"
        YEARLY = "yearly"
        ON_DEMAND = "on_demand"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Report configuration
    query = Column(Text, nullable=True)  # SQL query or query reference
    template = Column(Text, nullable=True)  # Report template (Jinja2, etc.)
    default_format = Column(Enum(ReportFormat), default=ReportFormat.PDF, nullable=False)
    
    # Scheduling
    is_scheduled = Column(Boolean, default=False, nullable=False)
    schedule = Column(String(100), nullable=True)  # Cron expression
    frequency = Column(Enum(ReportFrequency), nullable=True)
    
    # Security
    is_public = Column(Boolean, default=False, nullable=False)
    allowed_roles = Column(ARRAY(String(100)), default=[], nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_generated_at = Column(DateTime(timezone=True), nullable=True)
    
    # Audit fields
    created_by = Column(String(255), nullable=True)
    updated_by = Column(String(255), nullable=True)
    
    def __repr__(self):
        return f"<ReportDefinition(id={self.id}, name='{self.name}')>"

class DashboardDefinition(Base):
    """
    Defines a dashboard layout and configuration.
    """
    __tablename__ = "dashboard_definitions"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Layout and configuration
    layout_config = Column(JSONB, nullable=False)  # Dashboard layout
    
    # Security
    is_public = Column(Boolean, default=False, nullable=False)
    allowed_roles = Column(ARRAY(String(100)), default=[], nullable=False)
    
    # Relationships
    kpis = relationship(
        "KPI",
        secondary=dashboard_kpis,
        back_populates="dashboards"
    )
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Audit fields
    created_by = Column(String(255), nullable=True)
    updated_by = Column(String(255), nullable=True)
    
    def __repr__(self):
        return f"<DashboardDefinition(id={self.id}, name='{self.name}')>"

class KPI(Base):
    """
    Represents a Key Performance Indicator (KPI) that can be displayed on dashboards.
    """
    __tablename__ = "kpis"
    
    class KPIType(str, PyEnum):
        NUMERIC = "numeric"
        PERCENTAGE = "percentage"
        CURRENCY = "currency"
        BOOLEAN = "boolean"
        TREND = "trend"
        
    class TimeRange(str, PyEnum):
        TODAY = "today"
        YESTERDAY = "yesterday"
        THIS_WEEK = "this_week"
        LAST_WEEK = "last_week"
        THIS_MONTH = "this_month"
        LAST_MONTH = "last_month"
        THIS_QUARTER = "this_quarter"
        LAST_QUARTER = "last_quarter"
        THIS_YEAR = "this_year"
        LAST_YEAR = "last_year"
        LAST_7_DAYS = "last_7_days"
        LAST_30_DAYS = "last_30_days"
        LAST_90_DAYS = "last_90_days"
        LAST_365_DAYS = "last_365_days"
        CUSTOM = "custom"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # KPI configuration
    kpi_type = Column(Enum(KPIType), nullable=False)
    query = Column(Text, nullable=False)  # SQL query or reference to a data source
    
    # Formatting
    unit = Column(String(50), nullable=True)  # e.g., "$", "%", "items"
    decimal_places = Column(Integer, default=2, nullable=False)
    
    # Time range for the KPI
    default_time_range = Column(Enum(TimeRange), default=TimeRange.THIS_MONTH, nullable=False)
    
    # Thresholds for visualization
    warning_threshold = Column(Float, nullable=True)
    critical_threshold = Column(Float, nullable=True)
    
    # Relationships
    dashboards = relationship(
        "DashboardDefinition",
        secondary=dashboard_kpis,
        back_populates="kpis"
    )
    
    # Timestamps
    last_calculated_at = Column(DateTime(timezone=True), nullable=True)
    next_calculation_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Audit fields
    created_by = Column(String(255), nullable=True)
    updated_by = Column(String(255), nullable=True)
    
    def __repr__(self):
        return f"<KPI(id={self.id}, name='{self.name}', type='{self.kpi_type}')>"

# Event listeners for audit logging
@event.listens_for(AIModel, 'before_update')
def receive_before_update(mapper, connection, target):
    """Update the updated_at timestamp on model update."""
    target.updated_at = func.now()

@event.listens_for(DataSource, 'before_update')
def receive_data_source_before_update(mapper, connection, target):
    """Update the updated_at timestamp on data source update."""
    target.updated_at = func.now()

@event.listens_for(DataPipeline, 'before_update')
def receive_pipeline_before_update(mapper, connection, target):
    """Update the updated_at timestamp on pipeline update."""
    target.updated_at = func.now()

@event.listens_for(DataTransformation, 'before_update')
def receive_transformation_before_update(mapper, connection, target):
    """Update the updated_at timestamp on transformation update."""
    target.updated_at = func.now()

@event.listens_for(ReportDefinition, 'before_update')
def receive_report_def_before_update(mapper, connection, target):
    """Update the updated_at timestamp on report definition update."""
    target.updated_at = func.now()

@event.listens_for(DashboardDefinition, 'before_update')
def receive_dashboard_def_before_update(mapper, connection, target):
    """Update the updated_at timestamp on dashboard definition update."""
    target.updated_at = func.now()

@event.listens_for(KPI, 'before_update')
def receive_kpi_before_update(mapper, connection, target):
    """Update the updated_at timestamp on KPI update."""
    target.updated_at = func.now()
