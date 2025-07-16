from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.session import get_db
from app.modules.tax.services.analytics_service import TaxAnalyticsService
from app.modules.tax.schemas import TaxAnalyticsRequest, TaxAnalyticsResponse

router = APIRouter()

@router.post("/analytics", response_model=TaxAnalyticsResponse)
async def get_tax_analytics(
    request: TaxAnalyticsRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get comprehensive tax analytics and insights."""
    try:
        service = TaxAnalyticsService(db)
        return await service.get_tax_analytics(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/metrics")
async def get_tax_metrics(
    period: str = "current_month",
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get tax metrics for the specified period."""
    try:
        service = TaxAnalyticsService(db)
        # Create a minimal request object
        request = TaxAnalyticsRequest(period=period)
        response = await service.get_tax_analytics(request)
        return response.metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/insights")
async def get_tax_insights(
    period: str = "current_month",
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get AI-powered tax insights for the specified period."""
    try:
        service = TaxAnalyticsService(db)
        # Create a minimal request object
        request = TaxAnalyticsRequest(period=period)
        response = await service.get_tax_analytics(request)
        return response.insights
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
