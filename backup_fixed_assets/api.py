"""
Fixed assets API placeholder (conflicts resolved).
"""
"""
Fixed Assets Module - API Endpoints
"""
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status, Request, UploadFile, File
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.user import UserInDB
from . import schemas, models, services
from .exceptions import (
    AssetNotFound,
    AssetCategoryNotFound,
    MaintenanceRecordNotFound,
    DepreciationError,
    AssetValidationError
)

router = APIRouter(prefix="/fixed-assets", tags=["fixed-assets"])

# Dependency to get fixed asset service
def get_fixed_asset_service(db: Session = Depends(get_db)) -> services.FixedAssetService:
    return services.FixedAssetService(db)

# Helper function to handle service exceptions
def handle_asset_exception(e: Exception):
    if isinstance(e, (AssetNotFound, AssetCategoryNotFound, MaintenanceRecordNotFound)):
        raise HTTPException(status_code=404, detail=str(e))
    elif isinstance(e, (AssetValidationError, DepreciationError)):
        raise HTTPException(status_code=400, detail=str(e))
    else:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

# Asset Category Endpoints
@router.post(
    "/categories",
    response_model=schemas.AssetCategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new asset category",
    description="Create a new category for classifying fixed assets"
)
async def create_asset_category(
    category: schemas.AssetCategoryCreate,
    service: services.FixedAssetService = Depends(get_fixed_asset_service),
    current_user: UserInDB = Depends(get_current_user)
):
    try:
        return service.create_asset_category(category, current_user.id)
    except Exception as e:
        handle_asset_exception(e)

@router.get(
    "/categories/{category_id}",
    response_model=schemas.AssetCategoryResponse,
    summary="Get asset category by ID",
    description="Retrieve detailed information about a specific asset category"
)
async def get_asset_category(
    category_id: UUID,
    service: services.FixedAssetService = Depends(get_fixed_asset_service)
):
    try:
        return service.get_asset_category(category_id)
    except Exception as e:
        handle_asset_exception(e)

@router.get(
    "/categories",
    response_model=schemas.PaginatedResponse[schemas.AssetCategoryResponse],
    summary="List asset categories",
    description="List all asset categories with optional search and pagination"
)
async def list_asset_categories(
    request: Request,
    search: Optional[str] = Query(None, description="Search term for category name or description"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    service: services.FixedAssetService = Depends(get_fixed_asset_service)
):
    try:
        skip = (page - 1) * page_size
        categories, total = service.list_asset_categories(
            skip=skip,
            limit=page_size,
            search=search
        )
        
        # Build pagination URLs
        base_url = str(request.base_url).rstrip('/')
        path = request.url.path
        params = request.query_params.multi_items()
        
        def build_url(p: int):
            query_params = [f"{k}={v}" for k, v in params if k not in ['page', 'page_size']]
            query_params.append(f"page={p}")
            query_params.append(f"page_size={page_size}")
            return f"{base_url}{path}?{'&'.join(query_params)}"
        
        return {
            "data": categories,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size if total > 0 else 1,
            "links": {
                "first": build_url(1),
                "last": build_url((total + page_size - 1) // page_size) if total > 0 else build_url(1),
                "prev": build_url(page - 1) if page > 1 else None,
                "next": build_url(page + 1) if page * page_size < total else None
            }
        }
    except Exception as e:
        handle_asset_exception(e)

@router.put(
    "/categories/{category_id}",
    response_model=schemas.AssetCategoryResponse,
    summary="Update an asset category",
    description="Update an existing asset category with the provided details"
)
async def update_asset_category(
    category_id: UUID,
    category_update: schemas.AssetCategoryUpdate,
    service: services.FixedAssetService = Depends(get_fixed_asset_service),
    current_user: UserInDB = Depends(get_current_user)
):
    try:
        return service.update_asset_category(category_id, category_update, current_user.id)
    except Exception as e:
        handle_asset_exception(e)

@router.delete(
    "/categories/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an asset category",
    description="Delete an asset category. Categories with associated assets cannot be deleted."
)
async def delete_asset_category(
    category_id: UUID,
    service: services.FixedAssetService = Depends(get_fixed_asset_service),
    current_user: UserInDB = Depends(get_current_user)
):
    try:
        service.delete_asset_category(category_id)
        return None
    except Exception as e:
        handle_asset_exception(e)

# Asset Endpoints
@router.post(
    "/assets",
    response_model=schemas.AssetResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new fixed asset",
    description="Create a new fixed asset with the provided details"
)
async def create_asset(
    asset: schemas.AssetCreate,
    service: services.FixedAssetService = Depends(get_fixed_asset_service),
    current_user: UserInDB = Depends(get_current_user)
):
    try:
        return service.create_asset(asset, current_user.id)
    except Exception as e:
        handle_asset_exception(e)

@router.get(
    "/assets/{asset_id}",
    response_model=schemas.AssetResponse,
    summary="Get asset by ID",
    description="Retrieve detailed information about a specific fixed asset"
)
async def get_asset(
    asset_id: UUID,
    include_details: bool = Query(False, description="Include related records like maintenance and depreciation"),
    service: services.FixedAssetService = Depends(get_fixed_asset_service)
):
    try:
        return service.get_asset(asset_id, include_details=include_details)
    except Exception as e:
        handle_asset_exception(e)

@router.get(
    "/assets",
    response_model=schemas.PaginatedResponse[schemas.AssetResponse],
    summary="List fixed assets",
    description="List all fixed assets with filtering and pagination"
)
async def list_assets(
    request: Request,
    category_id: Optional[UUID] = Query(None, description="Filter by category ID"),
    status: Optional[schemas.AssetStatus] = Query(None, description="Filter by asset status"),
    location: Optional[str] = Query(None, description="Filter by location"),
    department: Optional[str] = Query(None, description="Filter by department"),
    acquired_after: Optional[date] = Query(None, description="Filter by acquisition date after"),
    acquired_before: Optional[date] = Query(None, description="Filter by acquisition date before"),
    search: Optional[str] = Query(None, description="Search term for asset name, number, or description"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    service: services.FixedAssetService = Depends(get_fixed_asset_service)
):
    try:
        skip = (page - 1) * page_size
        assets, total = service.list_assets(
            category_id=category_id,
            status=status,
            location=location,
            department=department,
            acquired_after=acquired_after,
            acquired_before=acquired_before,
            search=search,
            skip=skip,
            limit=page_size
        )
        
        # Build pagination URLs
        base_url = str(request.base_url).rstrip('/')
        path = request.url.path
        params = request.query_params.multi_items()
        
        def build_url(p: int):
            query_params = [f"{k}={v}" for k, v in params if k not in ['page', 'page_size']]
            query_params.append(f"page={p}")
            query_params.append(f"page_size={page_size}")
            return f"{base_url}{path}?{'&'.join(query_params)}"
        
        return {
            "data": assets,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size if total > 0 else 1,
            "links": {
                "first": build_url(1),
                "last": build_url((total + page_size - 1) // page_size) if total > 0 else build_url(1),
                "prev": build_url(page - 1) if page > 1 else None,
                "next": build_url(page + 1) if page * page_size < total else None
            }
        }
    except Exception as e:
        handle_asset_exception(e)

@router.put(
    "/assets/{asset_id}",
    response_model=schemas.AssetResponse,
    summary="Update a fixed asset",
    description="Update an existing fixed asset with the provided details"
)
async def update_asset(
    asset_id: UUID,
    asset_update: schemas.AssetUpdate,
    service: services.FixedAssetService = Depends(get_fixed_asset_service),
    current_user: UserInDB = Depends(get_current_user)
):
    try:
        return service.update_asset(asset_id, asset_update, current_user.id)
    except Exception as e:
        handle_asset_exception(e)

@router.delete(
    "/assets/{asset_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a fixed asset",
    description="Delete a fixed asset. Assets with transactions cannot be deleted."
)
async def delete_asset(
    asset_id: UUID,
    service: services.FixedAssetService = Depends(get_fixed_asset_service),
    current_user: UserInDB = Depends(get_current_user)
):
    try:
        service.delete_asset(asset_id)
        return None
    except Exception as e:
        handle_asset_exception(e)

# Maintenance Record Endpoints
@router.post(
    "/maintenance-records",
    response_model=schemas.MaintenanceRecordResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a maintenance record",
    description="Create a new maintenance record for a fixed asset"
)
async def create_maintenance_record(
    record: schemas.MaintenanceRecordCreate,
    service: services.FixedAssetService = Depends(get_fixed_asset_service),
    current_user: UserInDB = Depends(get_current_user)
):
    try:
        return service.create_maintenance_record(record, current_user.id)
    except Exception as e:
        handle_asset_exception(e)

@router.get(
    "/maintenance-records/{record_id}",
    response_model=schemas.MaintenanceRecordResponse,
    summary="Get maintenance record by ID",
    description="Retrieve detailed information about a specific maintenance record"
)
async def get_maintenance_record(
    record_id: UUID,
    service: services.FixedAssetService = Depends(get_fixed_asset_service)
):
    try:
        return service.get_maintenance_record(record_id)
    except Exception as e:
        handle_asset_exception(e)

@router.get(
    "/maintenance-records",
    response_model=schemas.PaginatedResponse[schemas.MaintenanceRecordResponse],
    summary="List maintenance records",
    description="List all maintenance records with filtering and pagination"
)
async def list_maintenance_records(
    request: Request,
    asset_id: Optional[UUID] = Query(None, description="Filter by asset ID"),
    maintenance_type: Optional[str] = Query(None, description="Filter by maintenance type"),
    start_date: Optional[date] = Query(None, description="Filter by maintenance date after"),
    end_date: Optional[date] = Query(None, description="Filter by maintenance date before"),
    status: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    service: services.FixedAssetService = Depends(get_fixed_asset_service)
):
    try:
        skip = (page - 1) * page_size
        records, total = service.list_maintenance_records(
            asset_id=asset_id,
            maintenance_type=maintenance_type,
            start_date=start_date,
            end_date=end_date,
            status=status,
            skip=skip,
            limit=page_size
        )
        
        # Build pagination URLs
        base_url = str(request.base_url).rstrip('/')
        path = request.url.path
        params = request.query_params.multi_items()
        
        def build_url(p: int):
            query_params = [f"{k}={v}" for k, v in params if k not in ['page', 'page_size']]
            query_params.append(f"page={p}")
            query_params.append(f"page_size={page_size}")
            return f"{base_url}{path}?{'&'.join(query_params)}"
        
        return {
            "data": records,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size if total > 0 else 1,
            "links": {
                "first": build_url(1),
                "last": build_url((total + page_size - 1) // page_size) if total > 0 else build_url(1),
                "prev": build_url(page - 1) if page > 1 else None,
                "next": build_url(page + 1) if page * page_size < total else None
            }
        }
    except Exception as e:
        handle_asset_exception(e)

@router.put(
    "/maintenance-records/{record_id}",
    response_model=schemas.MaintenanceRecordResponse,
    summary="Update a maintenance record",
    description="Update an existing maintenance record with the provided details"
)
async def update_maintenance_record(
    record_id: UUID,
    record_update: schemas.MaintenanceRecordUpdate,
    service: services.FixedAssetService = Depends(get_fixed_asset_service),
    current_user: UserInDB = Depends(get_current_user)
):
    try:
        return service.update_maintenance_record(record_id, record_update, current_user.id)
    except Exception as e:
        handle_asset_exception(e)

@router.delete(
    "/maintenance-records/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a maintenance record",
    description="Delete a maintenance record"
)
async def delete_maintenance_record(
    record_id: UUID,
    service: services.FixedAssetService = Depends(get_fixed_asset_service),
    current_user: UserInDB = Depends(get_current_user)
):
    try:
        service.delete_maintenance_record(record_id)
        return None
    except Exception as e:
        handle_asset_exception(e)

# Depreciation Endpoints
@router.post(
    "/assets/{asset_id}/depreciation-schedule",
    response_model=List[schemas.DepreciationScheduleResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Generate depreciation schedule",
    description="Generate or regenerate the depreciation schedule for an asset"
)
async def generate_depreciation_schedule(
    asset_id: UUID,
    service: services.FixedAssetService = Depends(get_fixed_asset_service),
    current_user: UserInDB = Depends(get_current_user)
):
    try:
        return service.generate_depreciation_schedule(asset_id, current_user.id)
    except Exception as e:
        handle_asset_exception(e)

@router.get(
    "/assets/{asset_id}/depreciation-schedule",
    response_model=schemas.PaginatedResponse[schemas.DepreciationScheduleResponse],
    summary="Get depreciation schedule",
    description="Get the depreciation schedule for an asset"
)
async def get_depreciation_schedule(
    asset_id: UUID,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    service: services.FixedAssetService = Depends(get_fixed_asset_service)
):
    try:
        # This would be implemented in the service to return paginated results
        # For now, we'll return all records with pagination handled by the database
        schedules = service.db.query(models.DepreciationSchedule).filter(
            models.DepreciationSchedule.asset_id == asset_id
        ).order_by(
            models.DepreciationSchedule.fiscal_year,
            models.DepreciationSchedule.period
        ).offset((page - 1) * page_size).limit(page_size).all()
        
        total = service.db.query(models.DepreciationSchedule).filter(
            models.DepreciationSchedule.asset_id == asset_id
        ).count()
        
        return {
            "data": schedules,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size if total > 0 else 1
        }
    except Exception as e:
        handle_asset_exception(e)

@router.post(
    "/depreciation/run",
    response_model=List[schemas.DepreciationScheduleResponse],
    summary="Run depreciation",
    description="Run depreciation for a specific period"
)
async def run_depreciation(
    period_date: date = Query(..., description="End date of the period to run depreciation for"),
    asset_ids: Optional[List[UUID]] = Query(None, description="Optional list of asset IDs to process"),
    service: services.FixedAssetService = Depends(get_fixed_asset_service),
    current_user: UserInDB = Depends(get_current_user)
):
    try:
        return service.post_depreciation(period_date, current_user.id, asset_ids)
    except Exception as e:
        handle_asset_exception(e)

# Report Endpoints
@router.post(
    "/reports/depreciation",
    summary="Generate depreciation report",
    description="Generate a depreciation report for the specified period"
)
async def generate_depreciation_report(
    report_request: schemas.DepreciationReportRequest,
    service: services.FixedAssetService = Depends(get_fixed_asset_service)
):
    try:
        # This would be implemented to generate a formatted report
        # For now, we'll return a placeholder response
        return {"message": "Depreciation report generation not yet implemented"}
    except Exception as e:
        handle_asset_exception(e)

@router.post(
    "/reports/maintenance",
    summary="Generate maintenance report",
    description="Generate a maintenance report for the specified period"
)
async def generate_maintenance_report(
    report_request: schemas.MaintenanceReportRequest,
    service: services.FixedAssetService = Depends(get_fixed_asset_service)
):
    try:
        # This would be implemented to generate a formatted report
        # For now, we'll return a placeholder response
        return {"message": "Maintenance report generation not yet implemented"}
    except Exception as e:
        handle_asset_exception(e)

@router.post(
    "/reports/asset-valuation",
    summary="Generate asset valuation report",
    description="Generate an asset valuation report as of a specific date"
)
async def generate_asset_valuation_report(
    report_request: schemas.AssetValuationReportRequest,
    service: services.FixedAssetService = Depends(get_fixed_asset_service)
):
    try:
        # This would be implemented to generate a formatted report
        # For now, we'll return a placeholder response
        return {"message": "Asset valuation report generation not yet implemented"}
    except Exception as e:
        handle_asset_exception(e)

# Import/Export Endpoints
@router.post(
    "/import",
    summary="Import assets",
    description="Import assets from a file"
)
async def import_assets(
    file: UploadFile = File(...),
    service: services.FixedAssetService = Depends(get_fixed_asset_service),
    current_user: UserInDB = Depends(get_current_user)
):
    try:
        # This would be implemented to process the uploaded file
        # For now, we'll return a placeholder response
        return {"message": "Asset import not yet implemented"}
    except Exception as e:
        handle_asset_exception(e)

@router.get(
    "/export",
    summary="Export assets",
    description="Export assets to a file"
)
async def export_assets(
    format: str = Query("csv", description="Export format (csv, excel, json)"),
    service: services.FixedAssetService = Depends(get_fixed_asset_service)
):
    try:
        # This would be implemented to generate the export file
        # For now, we'll return a placeholder response
        return {"message": "Asset export not yet implemented"}
    except Exception as e:
        handle_asset_exception(e)

# Dashboard Endpoints
@router.get(
    "/dashboard/summary",
    summary="Get fixed assets dashboard summary",
    description="Get summary statistics for the fixed assets dashboard"
)
async def get_dashboard_summary(
    service: services.FixedAssetService = Depends(get_fixed_asset_service)
):
    try:
        # This would be implemented to return dashboard statistics
        # For now, we'll return a placeholder response
        return {
            "total_assets": 0,
            "total_value": 0,
            "depreciation_this_month": 0,
            "pending_maintenance": 0,
            "assets_by_category": [],
            "recent_activities": []
        }
    except Exception as e:
        handle_asset_exception(e)

# Health Check Endpoint
@router.get("/health", summary="Health check", description="Check if the fixed assets module is healthy")
async def health_check():
    return {"status": "healthy"}
=======
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
>>>>>>> e96df7278ce4216131b6c65d411c0723f4de7f91
