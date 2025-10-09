from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date, timedelta
import uuid

from ....database import get_db
from ....models.inventory import FixedAsset, AssetDepreciation, AssetMaintenance
from ....schemas.fixed_assets import (
    FixedAssetCreate, FixedAssetUpdate, FixedAssetResponse,
    AssetDepreciationCreate, AssetDepreciationResponse,
    AssetMaintenanceCreate, AssetMaintenanceUpdate, AssetMaintenanceResponse,
    AssetStatsResponse, AssetDisposalRequest
)
from ....core.auth import get_current_user
from ....models.user import User

router = APIRouter()

# Assets endpoints
@router.get("/assets", response_model=List[FixedAssetResponse])
async def get_assets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(FixedAsset).filter(FixedAsset.company_id == current_user.company_id)
    
    if category:
        query = query.filter(FixedAsset.asset_category == category)
    
    if status:
        query = query.filter(FixedAsset.status == status)
    
    assets = query.offset(skip).limit(limit).all()
    return assets

@router.post("/assets", response_model=FixedAssetResponse)
async def create_asset(
    asset: FixedAssetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Calculate current value
    current_value = asset.purchase_cost - (asset.accumulated_depreciation or 0)
    
    db_asset = FixedAsset(
        id=str(uuid.uuid4()),
        company_id=current_user.company_id,
        current_value=current_value,
        **asset.dict()
    )
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    return db_asset

@router.get("/assets/{asset_id}", response_model=FixedAssetResponse)
async def get_asset(
    asset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    asset = db.query(FixedAsset).filter(
        FixedAsset.id == asset_id,
        FixedAsset.company_id == current_user.company_id
    ).first()
    
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    return asset

@router.put("/assets/{asset_id}", response_model=FixedAssetResponse)
async def update_asset(
    asset_id: str,
    asset_update: FixedAssetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_asset = db.query(FixedAsset).filter(
        FixedAsset.id == asset_id,
        FixedAsset.company_id == current_user.company_id
    ).first()
    
    if not db_asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    for field, value in asset_update.dict(exclude_unset=True).items():
        setattr(db_asset, field, value)
    
    # Recalculate current value if needed
    if hasattr(asset_update, 'purchase_cost') or hasattr(asset_update, 'accumulated_depreciation'):
        db_asset.current_value = db_asset.purchase_cost - (db_asset.accumulated_depreciation or 0)
    
    db.commit()
    db.refresh(db_asset)
    return db_asset

@router.delete("/assets/{asset_id}")
async def delete_asset(
    asset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_asset = db.query(FixedAsset).filter(
        FixedAsset.id == asset_id,
        FixedAsset.company_id == current_user.company_id
    ).first()
    
    if not db_asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    db.delete(db_asset)
    db.commit()
    return {"message": "Asset deleted successfully"}

@router.post("/assets/{asset_id}/dispose")
async def dispose_asset(
    asset_id: str,
    disposal: AssetDisposalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_asset = db.query(FixedAsset).filter(
        FixedAsset.id == asset_id,
        FixedAsset.company_id == current_user.company_id
    ).first()
    
    if not db_asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    db_asset.status = "disposed"
    db_asset.current_value = disposal.disposal_amount
    
    db.commit()
    db.refresh(db_asset)
    return db_asset

# Depreciation endpoints
@router.get("/assets/{asset_id}/depreciation", response_model=List[AssetDepreciationResponse])
async def get_asset_depreciation(
    asset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify asset exists and belongs to user's company
    asset = db.query(FixedAsset).filter(
        FixedAsset.id == asset_id,
        FixedAsset.company_id == current_user.company_id
    ).first()
    
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    depreciation_records = db.query(AssetDepreciation).filter(
        AssetDepreciation.asset_id == asset_id
    ).order_by(AssetDepreciation.depreciation_date.desc()).all()
    
    return depreciation_records

@router.post("/assets/{asset_id}/depreciation", response_model=AssetDepreciationResponse)
async def create_depreciation_entry(
    asset_id: str,
    depreciation: AssetDepreciationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify asset exists and belongs to user's company
    asset = db.query(FixedAsset).filter(
        FixedAsset.id == asset_id,
        FixedAsset.company_id == current_user.company_id
    ).first()
    
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    db_depreciation = AssetDepreciation(
        id=str(uuid.uuid4()),
        asset_id=asset_id,
        **depreciation.dict()
    )
    
    # Update asset's accumulated depreciation
    asset.accumulated_depreciation = (asset.accumulated_depreciation or 0) + depreciation.depreciation_amount
    asset.current_value = asset.purchase_cost - asset.accumulated_depreciation
    
    db.add(db_depreciation)
    db.commit()
    db.refresh(db_depreciation)
    return db_depreciation

# Maintenance endpoints
@router.get("/maintenance", response_model=List[AssetMaintenanceResponse])
async def get_maintenance_records(
    asset_id: Optional[str] = None,
    upcoming_days: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Base query - join with assets to filter by company
    query = db.query(AssetMaintenance).join(FixedAsset).filter(
        FixedAsset.company_id == current_user.company_id
    )
    
    if asset_id:
        query = query.filter(AssetMaintenance.asset_id == asset_id)
    
    if upcoming_days:
        future_date = datetime.now().date() + timedelta(days=upcoming_days)
        query = query.filter(
            AssetMaintenance.maintenance_date <= future_date,
            AssetMaintenance.maintenance_date >= datetime.now().date()
        )
    
    maintenance_records = query.offset(skip).limit(limit).all()
    return maintenance_records

@router.post("/maintenance", response_model=AssetMaintenanceResponse)
async def create_maintenance_record(
    maintenance: AssetMaintenanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify asset exists and belongs to user's company
    asset = db.query(FixedAsset).filter(
        FixedAsset.id == maintenance.asset_id,
        FixedAsset.company_id == current_user.company_id
    ).first()
    
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    db_maintenance = AssetMaintenance(
        id=str(uuid.uuid4()),
        created_by=current_user.id,
        **maintenance.dict()
    )
    db.add(db_maintenance)
    db.commit()
    db.refresh(db_maintenance)
    return db_maintenance

@router.put("/maintenance/{maintenance_id}", response_model=AssetMaintenanceResponse)
async def update_maintenance_record(
    maintenance_id: str,
    maintenance_update: AssetMaintenanceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get maintenance record and verify asset belongs to user's company
    db_maintenance = db.query(AssetMaintenance).join(FixedAsset).filter(
        AssetMaintenance.id == maintenance_id,
        FixedAsset.company_id == current_user.company_id
    ).first()
    
    if not db_maintenance:
        raise HTTPException(status_code=404, detail="Maintenance record not found")
    
    for field, value in maintenance_update.dict(exclude_unset=True).items():
        setattr(db_maintenance, field, value)
    
    db.commit()
    db.refresh(db_maintenance)
    return db_maintenance

# Statistics endpoint
@router.get("/stats", response_model=AssetStatsResponse)
async def get_asset_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    assets = db.query(FixedAsset).filter(FixedAsset.company_id == current_user.company_id).all()
    
    total_assets = len(assets)
    total_cost = sum(asset.purchase_cost for asset in assets)
    total_accumulated_depreciation = sum(asset.accumulated_depreciation or 0 for asset in assets)
    total_current_value = sum(asset.current_value or 0 for asset in assets)
    
    # Calculate monthly depreciation (simplified)
    monthly_depreciation = sum(
        (asset.purchase_cost - (asset.salvage_value or 0)) / (asset.useful_life_years * 12)
        for asset in assets if asset.useful_life_years and asset.status == 'active'
    )
    
    # Count maintenance due (next 30 days)
    from datetime import timedelta
    future_date = datetime.now().date() + timedelta(days=30)
    maintenance_due = db.query(AssetMaintenance).join(FixedAsset).filter(
        FixedAsset.company_id == current_user.company_id,
        AssetMaintenance.maintenance_date <= future_date,
        AssetMaintenance.maintenance_date >= datetime.now().date()
    ).count()
    
    return AssetStatsResponse(
        total_assets=total_assets,
        total_cost=total_cost,
        total_accumulated_depreciation=total_accumulated_depreciation,
        total_current_value=total_current_value,
        monthly_depreciation=monthly_depreciation,
        maintenance_due=maintenance_due
    )

# Categories endpoint
@router.get("/categories")
async def get_asset_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get unique categories from existing assets
    categories = db.query(FixedAsset.asset_category).filter(
        FixedAsset.company_id == current_user.company_id,
        FixedAsset.asset_category.isnot(None)
    ).distinct().all()
    
    return [{"name": cat[0], "value": cat[0]} for cat in categories if cat[0]]