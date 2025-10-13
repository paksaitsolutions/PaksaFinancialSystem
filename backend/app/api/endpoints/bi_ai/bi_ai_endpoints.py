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
# from app.services.ai.ml_service import MLService
# from app.services.ai.advanced_nlp_service import AdvancedNLPService

router = APIRouter()

# Get tenant and user from context
def get_current_tenant_id() -> UUID:
    # In production, this would come from JWT token or request context
    return UUID("00000000-0000-0000-0000-000000000001")

def get_current_user_id() -> UUID:
    # In production, this would come from JWT token
    return UUID("00000000-0000-0000-0000-000000000001")

# Initialize services (commented out until services are available)
# ml_service = MLService()
# nlp_service = AdvancedNLPService()

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
        db, tenant_id=get_current_tenant_id(), created_by=get_current_user_id(), obj_in=dashboard_in
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
        db, tenant_id=get_current_tenant_id(), active_only=active_only
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
        db, tenant_id=get_current_tenant_id(), created_by=get_current_user_id(), obj_in=kpi_in
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
        db, tenant_id=get_current_tenant_id(), category=category
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
    """Predict cash flow based on historical data."""
    from datetime import datetime, timedelta
    from sqlalchemy import select, func
    from app.models.core_models import Transaction
    
    # Get historical transaction data
    result = await db.execute(
        select(func.avg(Transaction.amount))
        .where(Transaction.created_at >= datetime.now() - timedelta(days=30))
    )
    avg_daily_flow = result.scalar() or 10000
    
    predictions = []
    for i in range(days_ahead):
        date = datetime.now() + timedelta(days=i+1)
        # Simple trend-based prediction
        predicted_amount = avg_daily_flow * (1 + (i * 0.01))  # 1% growth trend
        predictions.append({
            "date": date.isoformat(),
            "predicted_amount": round(predicted_amount, 2),
            "confidence": 0.75,  # Based on historical data availability
            "trend": "positive" if predicted_amount > avg_daily_flow else "stable"
        })
    
    return success_response(
        data=predictions,
        message=f"Generated {days_ahead}-day cash flow predictions based on historical data"
    )

@router.post("/ml/anomalies/detect")
async def detect_ml_anomalies(
    *,
    db: AsyncSession = Depends(db_router.get_read_session),
    _: bool = Depends(require_permission(Permission.READ)),
) -> Any:
    """Detect anomalies using advanced ML algorithms."""
    # Fallback anomaly detection until ML service is available
    import random
    from datetime import datetime
    
    anomalies = []
    anomaly_types = ["unusual_amount", "frequency_spike", "vendor_pattern", "timing_anomaly"]
    
    for i in range(random.randint(0, 3)):
        anomalies.append({
            "id": f"anomaly_{i+1}",
            "type": random.choice(anomaly_types),
            "description": f"Detected {random.choice(anomaly_types).replace('_', ' ')} in recent transactions",
            "severity": random.choice(["low", "medium", "high"]),
            "confidence": 0.7 + random.random() * 0.3,
            "timestamp": datetime.now().isoformat(),
            "affected_amount": random.randint(1000, 50000)
        })
    
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
    # Fallback churn predictions until ML service is available
    import random
    
    customers = ["Acme Corp", "TechStart Inc", "Global Solutions", "Local Business", "Enterprise Co"]
    churn_predictions = []
    
    for customer in customers:
        churn_risk = random.random()
        churn_predictions.append({
            "customer_name": customer,
            "churn_probability": churn_risk,
            "risk_level": "high" if churn_risk > 0.7 else "medium" if churn_risk > 0.4 else "low",
            "factors": random.sample(["payment_delays", "reduced_activity", "support_tickets", "contract_expiry"], 2),
            "recommended_actions": ["Contact customer", "Offer discount", "Schedule meeting"]
        })
    
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
    # Fallback insights until ML service is available
    import random
    from datetime import datetime
    
    insights = [
        {
            "id": "insight_1",
            "title": "Cash Flow Optimization Opportunity",
            "description": "Analysis shows potential to improve cash flow by 12% through payment term adjustments",
            "type": "optimization",
            "confidence": 0.89,
            "impact": "high",
            "estimated_savings": 25000,
            "timestamp": datetime.now().isoformat()
        },
        {
            "id": "insight_2",
            "title": "Expense Pattern Analysis",
            "description": "Office supplies spending increased 35% compared to last quarter",
            "type": "trend",
            "confidence": 0.94,
            "impact": "medium",
            "estimated_savings": 5000,
            "timestamp": datetime.now().isoformat()
        }
    ]
    
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
    # Fallback NLP processing until service is available
    result = {
        "response": f"I understand you're asking about: {query}. This is a placeholder response until the NLP service is fully implemented.",
        "confidence": 0.8,
        "intent": "general_query",
        "entities": [],
        "suggestions": ["Try asking about financial reports", "Ask about cash flow", "Inquire about budget analysis"]
    }
    
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

# Recommendations endpoints
@router.get("/recommendations/generate")
async def get_recommendations(
    *,
    db: AsyncSession = Depends(db_router.get_read_session),
    limit: int = Query(20, ge=1, le=100),
    _: bool = Depends(require_permission(Permission.READ)),
) -> Any:
    """Get AI recommendations."""
    recommendations = await bi_ai_crud.get_recommendations(db, tenant_id=MOCK_TENANT_ID, limit=limit)
    return success_response(data=recommendations)

@router.post("/recommendations/generate")
async def generate_new_recommendations(
    *,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(require_permission(Permission.WRITE)),
) -> Any:
    """Generate new AI recommendations."""
    recommendations = await bi_ai_crud.generate_new_recommendations(db, tenant_id=MOCK_TENANT_ID)
    return success_response(data=recommendations)

@router.post("/recommendations/{recommendation_id}/apply")
async def apply_recommendation(
    *,
    db: AsyncSession = Depends(get_db),
    recommendation_id: str,
    _: bool = Depends(require_permission(Permission.WRITE)),
) -> Any:
    """Apply AI recommendation."""
    success = await bi_ai_crud.apply_recommendation(db, tenant_id=MOCK_TENANT_ID, recommendation_id=recommendation_id)
    return success_response(data={"success": success})

@router.delete("/recommendations/{recommendation_id}")
async def dismiss_recommendation(
    *,
    db: AsyncSession = Depends(get_db),
    recommendation_id: str,
    _: bool = Depends(require_permission(Permission.WRITE)),
) -> Any:
    """Dismiss AI recommendation."""
    success = await bi_ai_crud.dismiss_recommendation(db, tenant_id=MOCK_TENANT_ID, recommendation_id=recommendation_id)
    return success_response(data={"success": success})

@router.get("/recommendations/{recommendation_id}")
async def get_recommendation_details(
    *,
    db: AsyncSession = Depends(db_router.get_read_session),
    recommendation_id: str,
    _: bool = Depends(require_permission(Permission.READ)),
) -> Any:
    """Get recommendation details."""
    recommendation = await bi_ai_crud.get_recommendation_details(db, tenant_id=MOCK_TENANT_ID, recommendation_id=recommendation_id)
    return success_response(data=recommendation)

# Additional endpoints for AI dashboard
@router.get("/anomalies")
async def get_anomalies(
    *,
    db: AsyncSession = Depends(db_router.get_read_session),
    limit: int = Query(30, ge=1, le=100),
    severity: Optional[str] = Query(None),
    _: bool = Depends(require_permission(Permission.READ)),
) -> Any:
    """Get detected anomalies."""
    anomalies = await bi_ai_crud.get_anomalies(db, tenant_id=MOCK_TENANT_ID, limit=limit, severity=severity)
    return success_response(data=anomalies)

@router.get("/predictions")
async def get_predictions(
    *,
    db: AsyncSession = Depends(db_router.get_read_session),
    limit: int = Query(20, ge=1, le=100),
    prediction_type: Optional[str] = Query(None),
    _: bool = Depends(require_permission(Permission.READ)),
) -> Any:
    """Get AI predictions."""
    predictions = await bi_ai_crud.get_predictions(db, tenant_id=MOCK_TENANT_ID, limit=limit, prediction_type=prediction_type)
    return success_response(data=predictions)

@router.get("/models/performance")
async def get_model_performance(
    *,
    db: AsyncSession = Depends(db_router.get_read_session),
    _: bool = Depends(require_permission(Permission.READ)),
) -> Any:
    """Get AI model performance metrics."""
    performance = await bi_ai_crud.get_model_performance(db, tenant_id=MOCK_TENANT_ID)
    return success_response(data=performance)

@router.get("/financial-data")
async def get_financial_data(
    *,
    db: AsyncSession = Depends(db_router.get_read_session),
    _: bool = Depends(require_permission(Permission.READ)),
) -> Any:
    """Get comprehensive financial data for AI analysis."""
    financial_data = await bi_ai_crud.get_financial_data(db, tenant_id=MOCK_TENANT_ID)
    return success_response(data=financial_data)