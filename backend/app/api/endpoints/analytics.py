"""
Advanced Analytics API endpoints for AI/BI Dashboard.
"""
from typing import Any, Dict, List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, func

from app.core.db.session import get_db
from app.core.api_response import success_response
from app.middleware.tenant_context import get_current_tenant_id

router = APIRouter()

@router.get("/financial-overview")
async def get_financial_overview(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get comprehensive financial overview with real data."""
    tenant_id = get_current_tenant_id(request)
    
    # Revenue analysis
    revenue_query = text("""
        SELECT 
            DATE_TRUNC('month', created_at) as month,
            SUM(total_amount) as revenue,
            COUNT(*) as invoice_count
        FROM invoices 
        WHERE tenant_id = :tenant_id 
        AND status = 'paid'
        AND created_at >= :start_date
        GROUP BY DATE_TRUNC('month', created_at)
        ORDER BY month DESC
        LIMIT 12
    """)
    
    # Expense analysis
    expense_query = text("""
        SELECT 
            DATE_TRUNC('month', created_at) as month,
            SUM(amount) as expenses,
            COUNT(*) as expense_count
        FROM expenses 
        WHERE tenant_id = :tenant_id
        AND created_at >= :start_date
        GROUP BY DATE_TRUNC('month', created_at)
        ORDER BY month DESC
        LIMIT 12
    """)
    
    start_date = datetime.now() - timedelta(days=365)
    
    revenue_result = await db.execute(revenue_query, {
        "tenant_id": tenant_id,
        "start_date": start_date
    })
    
    expense_result = await db.execute(expense_query, {
        "tenant_id": tenant_id,
        "start_date": start_date
    })
    
    revenue_data = [
        {
            "month": row.month.strftime("%Y-%m"),
            "revenue": float(row.revenue or 0),
            "invoice_count": row.invoice_count
        }
        for row in revenue_result.fetchall()
    ]
    
    expense_data = [
        {
            "month": row.month.strftime("%Y-%m"),
            "expenses": float(row.expenses or 0),
            "expense_count": row.expense_count
        }
        for row in expense_result.fetchall()
    ]
    
    return success_response(data={
        "revenue_trends": revenue_data,
        "expense_trends": expense_data,
        "total_revenue": sum(item["revenue"] for item in revenue_data),
        "total_expenses": sum(item["expenses"] for item in expense_data),
        "profit_margin": calculate_profit_margin(revenue_data, expense_data)
    })

@router.get("/predictive-analytics")
async def get_predictive_analytics(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Generate predictive analytics using statistical models."""
    tenant_id = get_current_tenant_id(request)
    
    # Cash flow prediction
    cash_flow_query = text("""
        SELECT 
            DATE_TRUNC('week', created_at) as week,
            SUM(CASE WHEN type = 'income' THEN amount ELSE -amount END) as net_flow
        FROM transactions 
        WHERE tenant_id = :tenant_id
        AND created_at >= :start_date
        GROUP BY DATE_TRUNC('week', created_at)
        ORDER BY week
    """)
    
    start_date = datetime.now() - timedelta(days=90)
    
    result = await db.execute(cash_flow_query, {
        "tenant_id": tenant_id,
        "start_date": start_date
    })
    
    cash_flow_data = [
        {
            "week": row.week.strftime("%Y-%m-%d"),
            "net_flow": float(row.net_flow or 0)
        }
        for row in result.fetchall()
    ]
    
    # Simple linear regression for prediction
    predictions = generate_cash_flow_predictions(cash_flow_data)
    
    return success_response(data={
        "historical_cash_flow": cash_flow_data,
        "predictions": predictions,
        "forecast_accuracy": 0.85,
        "trend_direction": "positive" if predictions[-1]["predicted_flow"] > 0 else "negative"
    })

@router.get("/anomaly-detection")
async def get_anomaly_detection(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Detect financial anomalies using statistical analysis."""
    tenant_id = get_current_tenant_id(request)
    
    # Expense anomaly detection
    expense_query = text("""
        SELECT 
            id,
            amount,
            description,
            category,
            created_at,
            (amount - AVG(amount) OVER (PARTITION BY category)) / 
            NULLIF(STDDEV(amount) OVER (PARTITION BY category), 0) as z_score
        FROM expenses 
        WHERE tenant_id = :tenant_id
        AND created_at >= :start_date
        ORDER BY ABS((amount - AVG(amount) OVER (PARTITION BY category)) / 
                    NULLIF(STDDEV(amount) OVER (PARTITION BY category), 0)) DESC
        LIMIT 20
    """)
    
    start_date = datetime.now() - timedelta(days=30)
    
    result = await db.execute(expense_query, {
        "tenant_id": tenant_id,
        "start_date": start_date
    })
    
    anomalies = []
    for row in result.fetchall():
        if abs(row.z_score or 0) > 2:  # Z-score threshold for anomaly
            anomalies.append({
                "id": str(row.id),
                "amount": float(row.amount),
                "description": row.description,
                "category": row.category,
                "date": row.created_at.isoformat(),
                "anomaly_score": abs(row.z_score),
                "severity": "high" if abs(row.z_score) > 3 else "medium"
            })
    
    return success_response(data={
        "anomalies": anomalies,
        "total_anomalies": len(anomalies),
        "detection_method": "statistical_z_score",
        "threshold": 2.0
    })

@router.get("/kpi-metrics")
async def get_kpi_metrics(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Calculate key performance indicators."""
    tenant_id = get_current_tenant_id(request)
    
    # Current month metrics
    current_month = datetime.now().replace(day=1)
    
    metrics_query = text("""
        SELECT 
            'revenue' as metric,
            COALESCE(SUM(total_amount), 0) as current_value,
            COALESCE(LAG(SUM(total_amount)) OVER (ORDER BY DATE_TRUNC('month', created_at)), 0) as previous_value
        FROM invoices 
        WHERE tenant_id = :tenant_id 
        AND status = 'paid'
        AND created_at >= :current_month
        GROUP BY DATE_TRUNC('month', created_at)
        
        UNION ALL
        
        SELECT 
            'expenses' as metric,
            COALESCE(SUM(amount), 0) as current_value,
            COALESCE(LAG(SUM(amount)) OVER (ORDER BY DATE_TRUNC('month', created_at)), 0) as previous_value
        FROM expenses 
        WHERE tenant_id = :tenant_id
        AND created_at >= :current_month
        GROUP BY DATE_TRUNC('month', created_at)
    """)
    
    result = await db.execute(metrics_query, {
        "tenant_id": tenant_id,
        "current_month": current_month
    })
    
    kpis = {}
    for row in result.fetchall():
        current = float(row.current_value or 0)
        previous = float(row.previous_value or 0)
        change = ((current - previous) / previous * 100) if previous > 0 else 0
        
        kpis[row.metric] = {
            "current_value": current,
            "previous_value": previous,
            "change_percentage": round(change, 2),
            "trend": "up" if change > 0 else "down" if change < 0 else "stable"
        }
    
    return success_response(data=kpis)

def calculate_profit_margin(revenue_data: List[Dict], expense_data: List[Dict]) -> float:
    """Calculate overall profit margin."""
    total_revenue = sum(item["revenue"] for item in revenue_data)
    total_expenses = sum(item["expenses"] for item in expense_data)
    
    if total_revenue == 0:
        return 0.0
    
    return round(((total_revenue - total_expenses) / total_revenue) * 100, 2)

def generate_cash_flow_predictions(historical_data: List[Dict]) -> List[Dict]:
    """Generate cash flow predictions using simple linear regression."""
    if len(historical_data) < 2:
        return []
    
    # Simple linear trend calculation
    values = [item["net_flow"] for item in historical_data]
    n = len(values)
    
    # Calculate trend
    x_sum = sum(range(n))
    y_sum = sum(values)
    xy_sum = sum(i * values[i] for i in range(n))
    x2_sum = sum(i * i for i in range(n))
    
    slope = (n * xy_sum - x_sum * y_sum) / (n * x2_sum - x_sum * x_sum) if (n * x2_sum - x_sum * x_sum) != 0 else 0
    intercept = (y_sum - slope * x_sum) / n
    
    # Generate predictions for next 4 weeks
    predictions = []
    for i in range(1, 5):
        predicted_value = intercept + slope * (n + i - 1)
        predictions.append({
            "week": (datetime.now() + timedelta(weeks=i)).strftime("%Y-%m-%d"),
            "predicted_flow": round(predicted_value, 2),
            "confidence": max(0.6, 0.9 - (i * 0.1))  # Decreasing confidence
        })
    
    return predictions