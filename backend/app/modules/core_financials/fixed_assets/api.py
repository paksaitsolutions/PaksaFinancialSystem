from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import date
from app.core.db import get_db
from .services import FixedAssetService, MaintenanceService, AssetCategoryService
from .disposal_service import AssetDisposalService
from .bulk_operations import BulkOperationsService
from .advanced_depreciation import AdvancedDepreciationService
from .schemas import (
    FixedAsset, FixedAssetCreate, FixedAssetUpdate,
    DepreciationEntry, MaintenanceRecord, MaintenanceRecordCreate, MaintenanceRecordUpdate,
    AssetCategory, AssetCategoryCreate, AssetDisposalRequest, AssetReport,
    AssetDisposalResult, BulkAssetUpdate, BulkDepreciationRequest, AssetTransferRequest
)

router = APIRouter()

# Initialize services
asset_service = FixedAssetService()
maintenance_service = MaintenanceService()
category_service = AssetCategoryService()
disposal_service = AssetDisposalService()
bulk_service = BulkOperationsService()
depreciation_service = AdvancedDepreciationService()

# Fixed Asset endpoints
@router.post("/assets/", response_model=FixedAsset, status_code=status.HTTP_201_CREATED)
async def create_asset(asset: FixedAssetCreate, db: AsyncSession = Depends(get_db)):
    existing = await asset_service.get_by_asset_number(db, asset.asset_number)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Asset number already exists"
        )
    return await asset_service.create(db, obj_in=asset)

@router.get("/assets/", response_model=List[FixedAsset])
async def get_assets(
    skip: int = 0,
    limit: int = 100,
    category: str = None,
    status: str = None,
    db: AsyncSession = Depends(get_db)
):
    if category:
        return await asset_service.get_assets_by_category(db, category)
    if status:
        return await asset_service.get_assets_by_status(db, status)
    return await asset_service.get_multi(db, skip=skip, limit=limit)

@router.get("/assets/{asset_id}", response_model=FixedAsset)
async def get_asset(asset_id: int, db: AsyncSession = Depends(get_db)):
    asset = await asset_service.get(db, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset

@router.put("/assets/{asset_id}", response_model=FixedAsset)
async def update_asset(
    asset_id: int,
    asset_update: FixedAssetUpdate,
    db: AsyncSession = Depends(get_db)
):
    asset = await asset_service.get(db, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return await asset_service.update(db, db_obj=asset, obj_in=asset_update)

@router.delete("/assets/{asset_id}")
async def delete_asset(asset_id: int, db: AsyncSession = Depends(get_db)):
    asset = await asset_service.get(db, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    await asset_service.remove(db, id=asset_id)
    return {"message": "Asset deleted successfully"}

# Depreciation endpoints
@router.post("/assets/{asset_id}/depreciation", response_model=DepreciationEntry)
async def create_depreciation_entry(
    asset_id: int,
    period_date: date,
    db: AsyncSession = Depends(get_db)
):
    entry = await asset_service.create_depreciation_entry(db, asset_id, period_date)
    if not entry:
        raise HTTPException(status_code=400, detail="Could not create depreciation entry")
    return entry

@router.post("/assets/{asset_id}/dispose", response_model=FixedAsset)
async def dispose_asset(
    asset_id: int,
    disposal_request: AssetDisposalRequest,
    db: AsyncSession = Depends(get_db)
):
    asset = await asset_service.dispose_asset(db, asset_id, disposal_request)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset

# Maintenance endpoints
@router.post("/maintenance/", response_model=MaintenanceRecord, status_code=status.HTTP_201_CREATED)
async def create_maintenance_record(
    maintenance: MaintenanceRecordCreate,
    db: AsyncSession = Depends(get_db)
):
    return await maintenance_service.create(db, obj_in=maintenance)

@router.get("/maintenance/", response_model=List[MaintenanceRecord])
async def get_maintenance_records(
    asset_id: int = None,
    upcoming_days: int = None,
    db: AsyncSession = Depends(get_db)
):
    if asset_id:
        return await maintenance_service.get_by_asset(db, asset_id)
    if upcoming_days:
        return await maintenance_service.get_upcoming_maintenance(db, upcoming_days)
    return await maintenance_service.get_multi(db)

@router.get("/maintenance/{maintenance_id}", response_model=MaintenanceRecord)
async def get_maintenance_record(maintenance_id: int, db: AsyncSession = Depends(get_db)):
    record = await maintenance_service.get(db, maintenance_id)
    if not record:
        raise HTTPException(status_code=404, detail="Maintenance record not found")
    return record

@router.put("/maintenance/{maintenance_id}", response_model=MaintenanceRecord)
async def update_maintenance_record(
    maintenance_id: int,
    maintenance_update: MaintenanceRecordUpdate,
    db: AsyncSession = Depends(get_db)
):
    record = await maintenance_service.get(db, maintenance_id)
    if not record:
        raise HTTPException(status_code=404, detail="Maintenance record not found")
    return await maintenance_service.update(db, db_obj=record, obj_in=maintenance_update)

# Category endpoints
@router.post("/categories/", response_model=AssetCategory, status_code=status.HTTP_201_CREATED)
async def create_category(category: AssetCategoryCreate, db: AsyncSession = Depends(get_db)):
    existing = await category_service.get_by_name(db, category.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category name already exists"
        )
    return await category_service.create(db, obj_in=category)

@router.get("/categories/", response_model=List[AssetCategory])
async def get_categories(db: AsyncSession = Depends(get_db)):
    return await category_service.get_multi(db)

# Advanced disposal endpoints
@router.post("/assets/{asset_id}/dispose-advanced", response_model=AssetDisposalResult)
async def dispose_asset_advanced(
    asset_id: int,
    disposal_request: AssetDisposalRequest,
    db: AsyncSession = Depends(get_db)
):
    return await disposal_service.initiate_disposal(db, asset_id, disposal_request, 1)

@router.post("/assets/bulk-dispose", response_model=List[AssetDisposalResult])
async def bulk_dispose_assets(
    asset_ids: List[int],
    disposal_request: AssetDisposalRequest,
    db: AsyncSession = Depends(get_db)
):
    return await disposal_service.bulk_dispose_assets(db, asset_ids, disposal_request, 1)

# Bulk operations endpoints
@router.put("/assets/bulk-update")
async def bulk_update_assets(
    asset_ids: List[int],
    update_data: BulkAssetUpdate,
    db: AsyncSession = Depends(get_db)
):
    return await bulk_service.bulk_update_assets(db, asset_ids, update_data)

@router.post("/depreciation/bulk-calculate")
async def bulk_calculate_depreciation(
    request: BulkDepreciationRequest,
    db: AsyncSession = Depends(get_db)
):
    return await bulk_service.bulk_calculate_depreciation(db, request)

@router.post("/assets/bulk-transfer")
async def bulk_transfer_assets(
    transfer_request: AssetTransferRequest,
    db: AsyncSession = Depends(get_db)
):
    return await bulk_service.bulk_transfer_assets(
        db, transfer_request.asset_ids, transfer_request.new_location, 
        transfer_request.transfer_date, 1
    )

# Advanced depreciation endpoints
@router.get("/assets/{asset_id}/depreciation-schedule")
async def get_depreciation_schedule(
    asset_id: int,
    method: str = None,
    db: AsyncSession = Depends(get_db)
):
    asset = await asset_service.get(db, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    from .models import DepreciationMethod
    depreciation_method = None
    if method:
        depreciation_method = DepreciationMethod(method)
    
    return depreciation_service.get_depreciation_schedule(asset, depreciation_method)

# Reports
@router.get("/reports/summary", response_model=AssetReport)
async def get_asset_report(db: AsyncSession = Depends(get_db)):
    return await asset_service.get_asset_report(db)