from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.db.session import get_db
from app.models.core_models import FixedAsset, AssetCategory, MaintenanceRecord
import io
import csv

router = APIRouter()

# Simple dependency for current user - replace with proper auth later
def get_current_user():
    return {"id": "1", "email": "admin@paksa.com", "full_name": "Admin User"}

@router.get("/stats")
async def get_asset_stats(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    """Get fixed assets statistics from database"""
    # Get total assets count
    total_assets_result = await db.execute(select(func.count(FixedAsset.id)))
    total_assets = total_assets_result.scalar() or 0
    
    # Get cost totals
    cost_result = await db.execute(select(func.sum(FixedAsset.purchase_cost)))
    total_cost = cost_result.scalar() or 0
    
    # Get depreciation totals
    depreciation_result = await db.execute(select(func.sum(FixedAsset.accumulated_depreciation)))
    total_depreciation = depreciation_result.scalar() or 0
    
    # Get current value totals
    value_result = await db.execute(select(func.sum(FixedAsset.current_value)))
    total_current_value = value_result.scalar() or 0
    
    # Get maintenance due count
    maintenance_result = await db.execute(
        select(func.count(MaintenanceRecord.id))
        .where(MaintenanceRecord.status == "scheduled")
    )
    maintenance_due = maintenance_result.scalar() or 0
    
    return {
        "total_assets": total_assets,
        "total_cost": float(total_cost),
        "total_accumulated_depreciation": float(total_depreciation),
        "total_current_value": float(total_current_value),
        "monthly_depreciation": float(total_depreciation / 12) if total_depreciation > 0 else 0,
        "maintenance_due": maintenance_due
    }

@router.get("/assets")
async def get_assets(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get fixed assets with filtering and pagination"""
    query = select(FixedAsset)
    
    if search:
        query = query.where(
            FixedAsset.asset_name.ilike(f"%{search}%") |
            FixedAsset.asset_number.ilike(f"%{search}%")
        )
    
    if status:
        query = query.where(FixedAsset.status == status)
    
    # Get total count
    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar()
    
    # Apply pagination
    query = query.offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    assets = result.scalars().all()
    
    return {
        "assets": [
            {
                "id": str(asset.id),
                "asset_number": asset.asset_number,
                "asset_name": asset.asset_name,
                "purchase_cost": float(asset.purchase_cost),
                "current_value": float(asset.current_value or 0),
                "status": asset.status,
                "purchase_date": asset.purchase_date.isoformat() if asset.purchase_date else None
            }
            for asset in assets
        ],
        "total": total,
        "page": page,
        "limit": limit
    }

@router.get("/categories")
async def get_categories(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    """Get asset categories"""
    result = await db.execute(select(AssetCategory))
    categories = result.scalars().all()
    
    return [
        {
            "id": str(category.id),
            "name": category.name,
            "description": category.description,
            "default_useful_life": category.default_useful_life
        }
        for category in categories
    ]