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
from app.services.ai.ml_service import MLService
from app.services.ai.advanced_nlp_service import AdvancedNLPService

router = APIRouter()

# Mock tenant and user IDs
MOCK_TENANT_ID = UUID("12345678-1234-5678-9012-123456789012")
MOCK_USER_ID = UUID("12345678-1234-5678-9012-123456789012")

# Initialize services
ml_service = MLService()
nlp_service = AdvancedNLPService()

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

# Advanced ML endpoints
@router.post("/ml/cash-flow/predict")
async def predict_cash_flow(
    *,
    db: AsyncSession = Depends(db_router.get_read_session),
    days_ahead: int = Query(30, ge=1, le=365),
    _: bool = Depends(require_permission(Permission.READ)),
) -> Any:
    """Predict cash flow using ML models."""
    ml_service = MLService()
    
    # Get historical cash flow data
    historical_data = await bi_ai_crud.get_cash_flow_history(db, tenant_id=MOCK_TENANT_ID)
    
    predictions = ml_service.predict_cash_flow(historical_data, days_ahead=days_ahead)
    
    return success_response(
        data=predictions,
        message=f"Generated {days_ahead}-day cash flow predictions"
    )

@router.post("/ml/anomalies/detect")
async def detect_ml_anomalies(
    *,
    db: AsyncSession = Depends(db_router.get_read_session),
    _: bool = Depends(require_permission(Permission.READ)),
) -> Any:
    """Detect anomalies using advanced ML algorithms."""
    ml_service = MLService()
    
    # Get transaction data
    transaction_data = await bi_ai_crud.get_transaction_data(db, tenant_id=MOCK_TENANT_ID)
    
    anomalies = ml_service.detect_anomalies(transaction_data)
    
    return success_response(
        data=anomalies,
        message=f"ML anomaly detection completed"
    )

@router.post("/ml/churn/predict")
async def predict_customer_churn(
    *,
    db: AsyncSession = Depends(db_router.get_read_session),
    _: bool = Depends(require_permission(Permission.READ)),
) -> Any:
    """Predict customer churn using ML models."""
    ml_service = MLService()
    
    # Get customer data
    customer_data = await bi_ai_crud.get_customer_data(db, tenant_id=MOCK_TENANT_ID)
    
    churn_predictions = ml_service.predict_customer_churn(customer_data)
    
    return success_response(
        data=churn_predictions,
        message="Customer churn predictions generated"
    )

@router.post("/ml/insights/generate")
async def generate_ml_insights(
    *,
    db: AsyncSession = Depends(db_router.get_read_session),
    _: bool = Depends(require_permission(Permission.READ)),
) -> Any:
    """Generate AI-powered financial insights."""
    ml_service = MLService()
    
    # Get comprehensive financial data
    financial_data = await bi_ai_crud.get_financial_data(db, tenant_id=MOCK_TENANT_ID)
    
    insights = ml_service.generate_financial_insights(financial_data)
    
    return success_response(
        data=insights,
        message=f"Generated {len(insights)} AI insights"
    )

# Advanced NLP endpoints
@router.post("/nlp/query")
async def process_nlp_query(
    *,
    query: str = Query(..., description="Natural language query"),
    user_id: str = Query(str(MOCK_USER_ID)),
    session_id: str = Query("default_session"),
    _: bool = Depends(require_permission(Permission.READ)),
) -> Any:
    """Process natural language query with advanced NLP."""
    nlp_service = AdvancedNLPService()
    
    result = nlp_service.process_advanced_query(query, user_id, session_id)
    
    return success_response(
        data=result,
        message="Query processed successfully"
    )

# Custom Widget Framework endpoints
@router.post("/widgets/custom")
async def create_custom_widget(
    *,
    db: AsyncSession = Depends(get_db),
    widget_config: dict,
    _: bool = Depends(require_permission(Permission.WRITE)),
) -> Any:
    """Create custom widget with advanced configuration."""
    widget = await bi_ai_crud.create_custom_widget(
        db, tenant_id=MOCK_TENANT_ID, config=widget_config
    )
    
    return success_response(
        data=widget,
        message="Custom widget created successfully",
        status_code=status.HTTP_201_CREATED
    )

@router.get("/widgets/templates")
async def get_widget_templates(
    *,
    category: Optional[str] = Query(None),
    _: bool = Depends(require_permission(Permission.READ)),
) -> Any:
    """Get available widget templates."""
    templates = {
        "chart_widgets": [
            {"type": "line_chart", "name": "Revenue Trend", "category": "financial"},
            {"type": "bar_chart", "name": "Expense Breakdown", "category": "financial"},
            {"type": "pie_chart", "name": "Account Distribution", "category": "accounting"}
        ],
        "metric_widgets": [
            {"type": "kpi_card", "name": "Total Revenue", "category": "financial"},
            {"type": "gauge", "name": "Cash Flow Health", "category": "financial"},
            {"type": "progress", "name": "Budget Utilization", "category": "budget"}
        ],
        "ai_widgets": [
            {"type": "prediction_chart", "name": "Cash Flow Forecast", "category": "ai"},
            {"type": "anomaly_alert", "name": "Anomaly Detection", "category": "ai"},
            {"type": "insight_card", "name": "AI Insights", "category": "ai"}
        ]
    }
    
    if category:
        filtered_templates = {}
        for widget_type, widgets in templates.items():
            filtered_widgets = [w for w in widgets if w["category"] == category]
            if filtered_widgets:
                filtered_templates[widget_type] = filtered_widgets
        templates = filtered_templates
    
    return success_response(data=templates)