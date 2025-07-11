"""
AI/ML endpoints for anomaly detection, forecasting, recommendations.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_async_db
from . import services, schemas

router = APIRouter(prefix="/ai-ml", tags=["ai-ml"])

@router.post("/anomaly-detection", response_model=schemas.AnomalyDetectionResult)
async def detect_anomalies(data: schemas.AnomalyDetectionRequest, db: AsyncSession = Depends(get_async_db)):
    return await services.AIService(db).detect_anomalies(data)

@router.post("/forecasting", response_model=schemas.ForecastingResult)
async def run_forecasting(data: schemas.ForecastingRequest, db: AsyncSession = Depends(get_async_db)):
    return await services.AIService(db).run_forecasting(data)

@router.post("/recommendations", response_model=schemas.RecommendationResult)
async def get_recommendations(data: schemas.RecommendationRequest, db: AsyncSession = Depends(get_async_db)):
    return await services.AIService(db).get_recommendations(data)
