from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any

from app.core.security import get_current_user
from app.db.session import get_db
from app.modules.cross_cutting.bi_ai.services.ai_service import AIService
from app.modules.cross_cutting.bi_ai.schemas import (
    AIModelCreate, AIModelUpdate, AIModelVersionCreate,
    ModelPredictionRequest, ModelPredictionResponse
)

router = APIRouter()

@router.post("/models", response_model=Dict[str, Any])
async def create_model(
    model_data: AIModelCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new AI model."""
    ai_service = AIService(db)
    return await ai_service.create_model(model_data)

@router.put("/models/{model_id}", response_model=Dict[str, Any])
async def update_model(
    model_id: str,
    update_data: AIModelUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update an existing AI model."""
    ai_service = AIService(db)
    return await ai_service.update_model(model_id, update_data)

@router.post("/models/{model_id}/versions", response_model=Dict[str, Any])
async def create_model_version(
    model_id: str,
    version_data: AIModelVersionCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new version of an AI model."""
    ai_service = AIService(db)
    return await ai_service.create_model_version(model_id, version_data)

@router.post("/models/{model_id}/deploy", response_model=Dict[str, Any])
async def deploy_model(
    model_id: str,
    deployment_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Deploy a model version."""
    ai_service = AIService(db)
    return await ai_service.create_deployment(deployment_data)

@router.post("/insights", response_model=Dict[str, Any])
async def generate_insights(
    data: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Generate AI insights based on input data."""
    ai_service = AIService(db)
    return await ai_service.generate_insights(data)

@router.post("/models/{model_id}/predict", response_model=ModelPredictionResponse)
async def predict(
    model_id: str,
    request: ModelPredictionRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Make a prediction using a deployed model."""
    ai_service = AIService(db)
    return await ai_service.predict(request)
