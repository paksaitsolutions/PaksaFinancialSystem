"""
API endpoints for inventory reports and analytics.
"""
from typing import Any, List, Optional
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.session import get_db
from app.core.api_response import success_response
from app.crud.inventory.reports import inventory_reports_crud
from app.schemas.inventory.reports import (
    InventoryValueReport,
    StockLevelReport,
    TransactionSummary,
    InventoryAnalytics,
)

router = APIRouter()

@router.get("/valuation", response_model=List[InventoryValueReport])
async def get_inventory_valuation(
    *,
    db: AsyncSession = Depends(get_db),
    category_id: Optional[str] = Query(None, description="Filter by category"),
    location_id: Optional[str] = Query(None, description="Filter by location"),
) -> Any:
    """
    Get inventory valuation report.
    """
    report = await inventory_reports_crud.get_inventory_valuation(
        db, category_id=category_id, location_id=location_id
    )
    return success_response(data=report)

@router.get("/stock-levels", response_model=List[StockLevelReport])
async def get_stock_levels(
    *,
    db: AsyncSession = Depends(get_db),
    low_stock_only: bool = Query(False, description="Show only low stock items"),
) -> Any:
    """
    Get stock level report.
    """
    report = await inventory_reports_crud.get_stock_levels(
        db, low_stock_only=low_stock_only
    )
    return success_response(data=report)

@router.get("/transaction-summary", response_model=List[TransactionSummary])
async def get_transaction_summary(
    *,
    db: AsyncSession = Depends(get_db),
    from_date: Optional[date] = Query(None, description="Start date"),
    to_date: Optional[date] = Query(None, description="End date"),
) -> Any:
    """
    Get transaction summary by type.
    """
    report = await inventory_reports_crud.get_transaction_summary(
        db, from_date=from_date, to_date=to_date
    )
    return success_response(data=report)

@router.get("/analytics", response_model=InventoryAnalytics)
async def get_analytics_dashboard(
    *,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get inventory analytics for dashboard.
    """
    analytics = await inventory_reports_crud.get_analytics_dashboard(db)
    return success_response(data=analytics)