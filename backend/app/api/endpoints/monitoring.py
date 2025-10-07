"""
Monitoring and health check endpoints.
"""
from typing import Any
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.session import get_db
from app.core.api_response import success_response
from app.core.monitoring import metrics, performance_monitor
from app.core.permissions import require_permission, Permission

router = APIRouter()

@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)) -> Any:
    """Health check endpoint."""
    try:
        # Test database connection
        await db.execute("SELECT 1")
        
        # Get system health
        health_data = performance_monitor.check_system_health()
        
        return {
            "status": "healthy",
            "timestamp": metrics.get_metrics()["timestamp"],
            "database": "connected",
            "system": health_data
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@router.get("/metrics")
async def get_metrics(
    _: bool = Depends(require_permission(Permission.ADMIN_READ))
) -> Any:
    """Get application metrics."""
    return success_response(data=metrics.get_metrics())

@router.get("/performance")
async def get_performance_data(
    _: bool = Depends(require_permission(Permission.ADMIN_READ))
) -> Any:
    """Get performance monitoring data."""
    health_data = performance_monitor.check_system_health()
    slow_queries = list(performance_monitor.slow_queries)
    
    return success_response(data={
        "health": health_data,
        "slow_queries": slow_queries[-10:],  # Last 10 slow queries
        "metrics": metrics.get_metrics()
    })