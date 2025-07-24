"""
API endpoints for BI/AI.
"""
from typing import Any, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.session import get_db
from app.core.db.router import db_router
from app.core.api_response import success_response, error_response
from app.core.permissions import require_permission, Permission
from app.crud.bi_ai.bi_ai_crud import bi_ai_crud
from app.schemas.bi_ai.bi_ai_schemas import (
    DashboardCreate, DashboardResponse,
    KPICreate, KPIResponse,
    AnalyticsData, AIInsight
)

router = APIRouter()

# Mock tenant and user IDs
MOCK_TENANT_ID = UUID("12345678-1234-5678-9012-123456789012")
MOCK_USER_ID = UUID("12345678-1234-5678-9012-123456789012")

# Dashboard endpoints
@router.post("/dashboards", response_model=DashboardResponse, status_code=status.HTTP_201_CREATED)
async def create_dashboard(
    *,
    db: AsyncSession = Depends(get_db),
    dashboard_in: DashboardCreate,
    _: bool = Depends(require_permission(Permission.WRITE)),
) -> Any:
    """Create dashboard."""
    dashboard = await bi_ai_crud.create_dashboard(
        db, tenant_id=MOCK_TENANT_ID, created_by=MOCK_USER_ID, obj_in=dashboard_in
    )
    return success_response(
        data=dashboard,
        message="Dashboard created successfully",
        status_code=status.HTTP_201_CREATED,
    )

@router.get("/dashboards", response_model=List[DashboardResponse])
async def get_dashboards(
    *,
    db: AsyncSession = Depends(db_router.get_read_session),
    active_only: bool = Query(True),
    _: bool = Depends(require_permission(Permission.READ)),
) -> Any:
    """Get dashboards."""
    dashboards = await bi_ai_crud.get_dashboards(
        db, tenant_id=MOCK_TENANT_ID, active_only=active_only
    )
    return success_response(data=dashboards)

# KPI endpoints
@router.post("/kpis", response_model=KPIResponse, status_code=status.HTTP_201_CREATED)
async def create_kpi(
    *,
    db: AsyncSession = Depends(get_db),
    kpi_in: KPICreate,
    _: bool = Depends(require_permission(Permission.WRITE)),
) -> Any:
    """Create KPI."""
    kpi = await bi_ai_crud.create_kpi(
        db, tenant_id=MOCK_TENANT_ID, created_by=MOCK_USER_ID, obj_in=kpi_in
    )
    return success_response(
        data=kpi,
        message="KPI created successfully",
        status_code=status.HTTP_201_CREATED,
    )

@router.get("/kpis", response_model=List[KPIResponse])
async def get_kpis(
    *,
    db: AsyncSession = Depends(db_router.get_read_session),
    category: Optional[str] = Query(None),
    _: bool = Depends(require_permission(Permission.READ)),
) -> Any:
    """Get KPIs."""
    kpis = await bi_ai_crud.get_kpis(
        db, tenant_id=MOCK_TENANT_ID, category=category
    )
    return success_response(data=kpis)

# Analytics endpoints
@router.get("/analytics", response_model=AnalyticsData)
async def get_analytics_data(
    *,
    db: AsyncSession = Depends(db_router.get_read_session),
    _: bool = Depends(require_permission(Permission.READ)),
) -> Any:
    """Get comprehensive analytics data."""
    analytics = await bi_ai_crud.get_analytics_data(
        db, tenant_id=MOCK_TENANT_ID
    )
    return success_response(data=analytics)

# Anomaly Detection endpoints
@router.post("/anomalies/detect")
async def detect_anomalies(
    *,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(require_permission(Permission.WRITE)),
) -> Any:
    """Detect anomalies in financial data."""
    anomalies = await bi_ai_crud.detect_anomalies(
        db, tenant_id=MOCK_TENANT_ID
    )
    return success_response(
        data=anomalies,
        message=f"Detected {len(anomalies)} anomalies",
    )

# Predictive Analytics endpoints
@router.post("/predictions/generate")
async def generate_predictions(
    *,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(require_permission(Permission.WRITE)),
) -> Any:
    """Generate AI predictions."""
    predictions = await bi_ai_crud.generate_predictions(
        db, tenant_id=MOCK_TENANT_ID
    )
    return success_response(
        data=predictions,
        message=f"Generated {len(predictions)} predictions",
    )

# AI Insights endpoints
@router.get("/insights", response_model=List[AIInsight])
async def get_ai_insights(
    *,
    db: AsyncSession = Depends(db_router.get_read_session),
    _: bool = Depends(require_permission(Permission.READ)),
) -> Any:
    """Get AI-powered insights."""
    insights = await bi_ai_crud.get_ai_insights(
        db, tenant_id=MOCK_TENANT_ID
    )
    return success_response(data=insights)