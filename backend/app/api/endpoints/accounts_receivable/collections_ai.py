"""
API endpoints for AI-powered collections insights.
"""
from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.session import get_db
from app.core.api_response import success_response
from app.crud.accounts_receivable.collections_ai import collections_ai_crud
from app.schemas.accounts_receivable.collections_ai import (
    CustomerRiskProfile, CollectionPrediction, CollectionsInsights, CollectionStrategy
)

router = APIRouter()

@router.get("/risk-profiles", response_model=List[CustomerRiskProfile])
async def get_customer_risk_profiles(
    *,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get AI-powered customer risk profiles.
    """
    profiles = await collections_ai_crud.get_customer_risk_profiles(db)
    return success_response(data=profiles)

@router.get("/predictions", response_model=List[CollectionPrediction])
async def get_collection_predictions(
    *,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get AI-powered collection predictions.
    """
    predictions = await collections_ai_crud.get_collection_predictions(db)
    return success_response(data=predictions)

@router.get("/insights", response_model=CollectionsInsights)
async def get_collections_insights(
    *,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get comprehensive AI-powered collections insights.
    """
    insights = await collections_ai_crud.get_collections_insights(db)
    return success_response(data=insights)

@router.get("/strategies/{customer_id}", response_model=List[CollectionStrategy])
async def get_collection_strategies(
    *,
    db: AsyncSession = Depends(get_db),
    customer_id: UUID,
) -> Any:
    """
    Get AI-recommended collection strategies for a customer.
    """
    strategies = await collections_ai_crud.get_collection_strategies(db, customer_id=customer_id)
    return success_response(data=strategies)