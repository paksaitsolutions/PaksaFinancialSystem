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
