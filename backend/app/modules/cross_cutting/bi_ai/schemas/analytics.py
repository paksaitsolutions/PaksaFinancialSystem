"""
Analytics & Dashboard Schemas

This module contains Pydantic schemas for analytics, reports, visualizations,
and dashboards in the BI/AI module.
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator, HttpUrl, Json, conlist, conint, constr

from .core import (
    BaseSchema, BaseCreateSchema, BaseUpdateSchema, BaseInDBBase,
    UUIDModelMixin, TimestampMixin, AuditMixin,
    ReportType, VisualizationType, DashboardLayoutType, AccessLevel,
    Response, PaginatedResponse, ErrorResponse, ErrorDetail,
    Relationship, RelationshipData, Metadata, DateRangeFilter
)

# --- Report ---
class ReportBase(BaseSchema):
    ""Base schema for reports with common fields."""
    name: str = Field(..., max_length=255, description="Name of the report")
    description: Optional[str] = Field(None, description="Description of the report")
    type: ReportType = Field(..., description="Type of the report")
    
    # Report configuration
    config: Dict[str, Any] = Field(
        ...,
        description="Report configuration including filters, columns, and other settings"
    )
    
    # Access control
    is_public: bool = Field(
        default=False,
        description="Whether the report is publicly accessible"
    )
    access_level: AccessLevel = Field(
        default=AccessLevel.VIEWER,
        description="Minimum access level required to view this report"
    )
    
    # Scheduling
    refresh_schedule: Optional[str] = Field(
        None,
        description="Cron expression for scheduled refreshes"
    )
    last_refreshed_at: Optional[datetime] = Field(
        None,
        description="Timestamp of the last refresh"
    )
    
    # Relationships (as IDs)
    data_source_ids: List[UUID] = Field(
        default_factory=list,
        description="IDs of data sources used in this report"
    )
    owner_id: Optional[UUID] = Field(
        None,
        description="ID of the user who owns this report"
    )

class ReportCreate(BaseCreateSchema, ReportBase):
    ""Schema for creating a new report."""
    pass

class ReportUpdate(BaseUpdateSchema):
    ""Schema for updating an existing report."""
    name: Optional[str] = Field(None, max_length=255, description="Name of the report")
    description: Optional[str] = Field(None, description="Description of the report")
    type: Optional[ReportType] = Field(None, description="Type of the report")
    config: Optional[Dict[str, Any]] = Field(
        None,
        description="Report configuration including filters, columns, and other settings"
    )
    is_public: Optional[bool] = Field(
        None,
        description="Whether the report is publicly accessible"
    )
    access_level: Optional[AccessLevel] = Field(
        None,
        description="Minimum access level required to view this report"
    )
    refresh_schedule: Optional[str] = Field(
        None,
        description="Cron expression for scheduled refreshes"
    )
    data_source_ids: Optional[List[UUID]] = Field(
        None,
        description="IDs of data sources used in this report"
    )

class ReportInDB(BaseInDBBase, ReportBase):
    ""Schema for report as stored in the database."""
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    class Config:
        orm_mode = True

# --- Visualization ---
class VisualizationBase(BaseSchema):
    ""Base schema for visualizations with common fields."""
    name: str = Field(..., max_length=255, description="Name of the visualization")
    description: Optional[str] = Field(None, description="Description of the visualization")
    type: VisualizationType = Field(..., description="Type of the visualization")
    
    # Visualization configuration
    config: Dict[str, Any] = Field(
        ...,
        description="Visualization configuration including data mapping, styling, and interactivity"
    )
    
    # Data configuration
    data_query: Optional[Dict[str, Any]] = Field(
        None,
        description="Query configuration for fetching data"
    )
    
    # Relationships (as IDs)
    report_id: UUID = Field(..., description="ID of the parent report")
    data_source_id: Optional[UUID] = Field(
        None,
        description="ID of the data source for this visualization"
    )

class VisualizationCreate(BaseCreateSchema, VisualizationBase):
    ""Schema for creating a new visualization."""
    pass

class VisualizationUpdate(BaseUpdateSchema):
    ""Schema for updating an existing visualization."""
    name: Optional[str] = Field(None, max_length=255, description="Name of the visualization")
    description: Optional[str] = Field(None, description="Description of the visualization")
    type: Optional[VisualizationType] = Field(None, description="Type of the visualization")
    config: Optional[Dict[str, Any]] = Field(
        None,
        description="Visualization configuration"
    )
    data_query: Optional[Dict[str, Any]] = Field(
        None,
        description="Query configuration for fetching data"
    )
    data_source_id: Optional[UUID] = Field(
        None,
        description="ID of the data source for this visualization"
    )

class VisualizationInDB(BaseInDBBase, VisualizationBase):
    ""Schema for visualization as stored in the database."""
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    class Config:
        orm_mode = True

# --- Dashboard ---
class DashboardBase(BaseSchema):
    ""Base schema for dashboards with common fields."""
    name: str = Field(..., max_length=255, description="Name of the dashboard")
    description: Optional[str] = Field(None, description="Description of the dashboard")
    
    # Layout and appearance
    layout_type: DashboardLayoutType = Field(
        default=DashboardLayoutType.GRID,
        description="Type of layout for the dashboard"
    )
    layout_config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Configuration for the dashboard layout"
    )
    theme: str = Field(
        default="light",
        description="Theme for the dashboard (light, dark, or custom)"
    )
    
    # Access control
    is_public: bool = Field(
        default=False,
        description="Whether the dashboard is publicly accessible"
    )
    access_level: AccessLevel = Field(
        default=AccessLevel.VIEWER,
        description="Minimum access level required to view this dashboard"
    )
    
    # Relationships (as IDs)
    report_ids: List[UUID] = Field(
        default_factory=list,
        description="IDs of reports included in this dashboard"
    )
    visualization_ids: List[UUID] = Field(
        default_factory=list,
        description="IDs of visualizations included in this dashboard"
    )
    owner_id: Optional[UUID] = Field(
        None,
        description="ID of the user who owns this dashboard"
    )

class DashboardCreate(BaseCreateSchema, DashboardBase):
    ""Schema for creating a new dashboard."""
    pass

class DashboardUpdate(BaseUpdateSchema):
    ""Schema for updating an existing dashboard."""
    name: Optional[str] = Field(None, max_length=255, description="Name of the dashboard")
    description: Optional[str] = Field(None, description="Description of the dashboard")
    layout_type: Optional[DashboardLayoutType] = Field(
        None,
        description="Type of layout for the dashboard"
    )
    layout_config: Optional[Dict[str, Any]] = Field(
        None,
        description="Configuration for the dashboard layout"
    )
    theme: Optional[str] = Field(
        None,
        description="Theme for the dashboard (light, dark, or custom)"
    )
    is_public: Optional[bool] = Field(
        None,
        description="Whether the dashboard is publicly accessible"
    )
    access_level: Optional[AccessLevel] = Field(
        None,
        description="Minimum access level required to view this dashboard"
    )
    report_ids: Optional[List[UUID]] = Field(
        None,
        description="IDs of reports included in this dashboard"
    )
    visualization_ids: Optional[List[UUID]] = Field(
        None,
        description="IDs of visualizations included in this dashboard"
    )

class DashboardInDB(BaseInDBBase, DashboardBase):
    ""Schema for dashboard as stored in the database."""
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    class Config:
        orm_mode = True

# --- Dashboard Item (for layout) ---
class DashboardItemBase(BaseSchema):
    ""Base schema for dashboard items (widgets)."""
    dashboard_id: UUID = Field(..., description="ID of the parent dashboard")
    item_type: str = Field(..., description="Type of the item (report, visualization, etc.)")
    item_id: UUID = Field(..., description="ID of the item (report, visualization, etc.)")
    
    # Layout configuration
    x: int = Field(..., description="X position in the grid")
    y: int = Field(..., description="Y position in the grid")
    w: int = Field(..., description="Width of the item in grid units")
    h: int = Field(..., description="Height of the item in grid units")
    
    # Additional configuration
    config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional configuration for the dashboard item"
    )

class DashboardItemCreate(BaseCreateSchema, DashboardItemBase):
    ""Schema for creating a new dashboard item."""
    pass

class DashboardItemUpdate(BaseUpdateSchema):
    ""Schema for updating an existing dashboard item."""
    x: Optional[int] = Field(None, description="X position in the grid")
    y: Optional[int] = Field(None, description="Y position in the grid")
    w: Optional[int] = Field(None, description="Width of the item in grid units")
    h: Optional[int] = Field(None, description="Height of the item in grid units")
    config: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional configuration for the dashboard item"
    )

class DashboardItemInDB(BaseInDBBase, DashboardItemBase):
    ""Schema for dashboard item as stored in the database."""
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    class Config:
        orm_mode = True

# --- Relationship Schemas ---
class ReportWithRelationships(ReportInDB):
    ""Report with relationships included."""
    visualizations: List[VisualizationInDB] = Field(
        default_factory=list,
        description="List of visualizations in this report"
    )
    data_sources: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of data sources used in this report"
    )
    dashboards: List[DashboardInDB] = Field(
        default_factory=list,
        description="List of dashboards that include this report"
    )

class VisualizationWithRelationships(VisualizationInDB):
    ""Visualization with relationships included."""
    report: Optional[ReportInDB] = Field(
        None,
        description="Parent report"
    )
    data_source: Optional[Dict[str, Any]] = Field(
        None,
        description="Data source for this visualization"
    )
    dashboards: List[DashboardInDB] = Field(
        default_factory=list,
        description="List of dashboards that include this visualization"
    )

class DashboardWithRelationships(DashboardInDB):
    ""Dashboard with relationships included."""
    reports: List[ReportInDB] = Field(
        default_factory=list,
        description="List of reports included in this dashboard"
    )
    visualizations: List[VisualizationInDB] = Field(
        default_factory=list,
        description="List of visualizations included in this dashboard"
    )
    items: List[DashboardItemInDB] = Field(
        default_factory=list,
        description="List of items (widgets) in this dashboard"
    )

# --- Request/Response Schemas ---
class RunReportRequest(BaseModel):
    ""Schema for running a report with custom parameters."""
    report_id: UUID = Field(..., description="ID of the report to run")
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Parameters to use when running the report"
    )
    format: str = Field(
        default="json",
        description="Output format (json, csv, excel, pdf, etc.)"
    )

class RunReportResponse(BaseModel):
    ""Response schema for running a report."""
    report_id: UUID = Field(..., description="ID of the report that was run")
    status: str = Field(..., description="Status of the report run")
    data: Optional[Any] = Field(None, description="Report data (if successful)")
    columns: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Column definitions for the report data"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional metadata about the report"
    )
    error: Optional[str] = Field(
        None,
        description="Error message if the report failed to run"
    )

class ExportDashboardRequest(BaseModel):
    ""Schema for exporting a dashboard."""
    dashboard_id: UUID = Field(..., description="ID of the dashboard to export")
    format: str = Field(
        default="pdf",
        description="Export format (pdf, png, json, etc.)"
    )
    include_data: bool = Field(
        default=False,
        description="Whether to include the data in the export"
    )

# --- Response Wrappers ---
class ReportResponse(Response[ReportWithRelationships]):
    ""Response wrapper for a single report."""
    data: ReportWithRelationships

class ReportListResponse(PaginatedResponse[ReportInDB]):
    ""Response wrapper for a paginated list of reports."""
    pass

class VisualizationResponse(Response[VisualizationWithRelationships]):
    ""Response wrapper for a single visualization."""
    data: VisualizationWithRelationships

class VisualizationListResponse(PaginatedResponse[VisualizationInDB]):
    ""Response wrapper for a paginated list of visualizations."""
    pass

class DashboardResponse(Response[DashboardWithRelationships]):
    ""Response wrapper for a single dashboard."""
    data: DashboardWithRelationships

class DashboardListResponse(PaginatedResponse[DashboardInDB]):
    ""Response wrapper for a paginated list of dashboards."""
    pass
