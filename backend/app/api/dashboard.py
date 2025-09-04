"""
Dashboard API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth_enhanced import get_current_user
from app.services.dashboard_service import *
from typing import Optional

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

# KPI Endpoints
@router.get("/kpis")
async def get_financial_kpis(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get real-time financial KPIs"""
    try:
        kpis = DashboardService.get_financial_kpis(db)
        return {"kpis": kpis}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics/ratios")
async def get_financial_ratios(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get financial ratios"""
    try:
        ratios = DashboardMetrics.calculate_financial_ratios(db)
        return {"ratios": ratios}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics/performance")
async def get_performance_indicators(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get performance indicators"""
    try:
        indicators = DashboardMetrics.get_performance_indicators(db)
        return {"indicators": indicators}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Chart Data Endpoints
@router.get("/charts/{chart_type}")
async def get_chart_data(
    chart_type: str,
    period: str = "30d",
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get chart data for visualizations"""
    try:
        chart_data = DashboardService.get_chart_data(db, chart_type, period)
        return {"chart_data": chart_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/charts/revenue-trend")
async def get_revenue_trend(
    period: str = "12m",
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get revenue trend chart"""
    try:
        chart_data = DashboardService.get_chart_data(db, "revenue_trend", period)
        return chart_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/charts/expense-breakdown")
async def get_expense_breakdown(
    period: str = "30d",
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get expense breakdown pie chart"""
    try:
        chart_data = DashboardService.get_chart_data(db, "expense_breakdown", period)
        return chart_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/charts/cash-flow")
async def get_cash_flow_chart(
    period: str = "8w",
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get cash flow chart"""
    try:
        chart_data = DashboardService.get_chart_data(db, "cash_flow", period)
        return chart_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/charts/ap-aging")
async def get_ap_aging_chart(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get accounts payable aging chart"""
    try:
        chart_data = DashboardService.get_chart_data(db, "ap_aging")
        return chart_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/charts/ar-aging")
async def get_ar_aging_chart(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get accounts receivable aging chart"""
    try:
        chart_data = DashboardService.get_chart_data(db, "ar_aging")
        return chart_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Alert Endpoints
@router.get("/alerts")
async def get_active_alerts(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get active alerts for user"""
    try:
        alerts = AlertService.get_active_alerts(db, current_user.id)
        return {"alerts": alerts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/alerts/{alert_id}/dismiss")
async def dismiss_alert(
    alert_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Dismiss an alert"""
    try:
        success = AlertService.dismiss_alert(db, alert_id, current_user.id)
        return {"success": success, "message": "Alert dismissed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Quick Actions Endpoints
@router.get("/quick-actions")
async def get_quick_actions(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get available quick actions"""
    try:
        actions = QuickActionsService.get_quick_actions(db, current_user.id)
        return {"actions": actions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Activity Feed Endpoints
@router.get("/activity")
async def get_recent_activity(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get recent activity feed"""
    try:
        activities = ActivityFeedService.get_recent_activity(db, current_user.id, limit)
        return {"activities": activities}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Summary Dashboard Endpoint
@router.get("/summary")
async def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get complete dashboard summary"""
    try:
        # Get all dashboard data in one call
        kpis = DashboardService.get_financial_kpis(db)
        alerts = AlertService.get_active_alerts(db, current_user.id)
        quick_actions = QuickActionsService.get_quick_actions(db, current_user.id)
        recent_activity = ActivityFeedService.get_recent_activity(db, current_user.id, 10)
        ratios = DashboardMetrics.calculate_financial_ratios(db)
        
        return {
            "kpis": kpis,
            "alerts": alerts,
            "quick_actions": quick_actions,
            "recent_activity": recent_activity,
            "financial_ratios": ratios,
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Real-time Updates Endpoint
@router.get("/updates")
async def get_dashboard_updates(
    last_update: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get dashboard updates since last check"""
    try:
        # In production, implement WebSocket or Server-Sent Events for real-time updates
        # For now, return current data
        kpis = DashboardService.get_financial_kpis(db)
        alerts = AlertService.get_active_alerts(db, current_user.id)
        
        return {
            "kpis": kpis,
            "alerts": alerts,
            "timestamp": datetime.now().isoformat(),
            "has_updates": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))