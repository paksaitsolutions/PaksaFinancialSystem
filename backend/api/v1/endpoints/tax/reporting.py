"""
Tax Reporting API Endpoints.

This module provides API endpoints for tax reporting functionality,
including generating tax reports and exporting them in various formats.
"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import deps
from app.core.tax.db_optimizer import TaxQueryOptimizer
from app.core.tax.export_service import TaxReportExporter, ExportFormat, ExportStatus
from app.core.tax.report_cache import report_cache
from app.models.user import User

router = APIRouter()

# Initialize services
tax_exporter = TaxReportExporter(deps.get_db())

@router.get("/liability", response_model=schemas.TaxLiabilityReportResponse)
async def get_tax_liability_report(
    start_date: date = Query(..., description="Start date of the report"),
    end_date: date = Query(..., description="End date of the report"),
    tax_types: Optional[List[str]] = Query(None, description="Filter by tax types"),
    jurisdiction_codes: Optional[List[str]] = Query(None, description="Filter by jurisdiction codes"),
    group_by: str = Query("month", description="Group by period (day, week, month, quarter, year)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(100, ge=1, le=1000, description="Items per page"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Generate a tax liability report with pagination.
    """
    # Validate date range
    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date must be before or equal to end date"
        )
    
    # Validate group_by parameter
    if group_by not in ["day", "week", "month", "quarter", "year"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid group_by parameter. Must be one of: day, week, month, quarter, year"
        )
    
    # Generate cache key
    cache_key = report_cache._generate_cache_key(
        "tax_liability_report",
        company_id=current_user.company_id,
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat(),
        tax_types=tax_types,
        jurisdiction_codes=jurisdiction_codes,
        group_by=group_by,
        page=page,
        page_size=page_size
    )
    
    # Try to get from cache
    cached_result = await report_cache.get(cache_key)
    if cached_result is not None:
        return cached_result
    
    # Generate report data
    query_optimizer = TaxQueryOptimizer(db)
    results, total_count = await query_optimizer.get_liability_report_data(
        company_id=current_user.company_id,
        start_date=start_date,
        end_date=end_date,
        tax_types=tax_types,
        jurisdiction_codes=jurisdiction_codes,
        group_by=group_by,
        page=page,
        page_size=page_size
    )
    
    # Format response
    response = {
        "data": results,
        "pagination": {
            "total": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": (total_count + page_size - 1) // page_size,
        },
        "filters": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "tax_types": tax_types,
            "jurisdiction_codes": jurisdiction_codes,
            "group_by": group_by
        }
    }
    
    # Cache the result
    await report_cache.set(
        cache_key,
        response,
        ttl=300  # 5 minutes
    )
    
    return response

@router.post("/export", response_model=schemas.TaxExportResponse)
async def export_tax_report(
    export_params: schemas.TaxExportCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Export a tax report in the specified format.
    
    This endpoint initiates a background task to generate the export
    and returns a task ID that can be used to check the status.
    """
    try:
        # Start the export process
        task_info = await tax_exporter.export_report(
            company_id=current_user.company_id,
            user=current_user,
            report_type=export_params.report_type,
            format=export_params.format,
            start_date=export_params.start_date,
            end_date=export_params.end_date,
            tax_types=export_params.tax_types,
            jurisdiction_codes=export_params.jurisdiction_codes,
            group_by=export_params.group_by,
            include_metadata=export_params.include_metadata,
            filename=export_params.filename,
            **export_params.export_options or {}
        )
        
        return {
            "task_id": task_info["task_id"],
            "status": task_info["status"],
            "message": task_info["message"],
            "download_url": task_info.get("download_url", "")
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start export: {str(e)}"
        )

@router.get("/export/status/{task_id}", response_model=schemas.TaxExportStatusResponse)
async def get_export_status(
    task_id: str,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get the status of a tax report export.
    """
    try:
        status_info = await tax_exporter.get_export_status(
            export_id=task_id,
            company_id=current_user.company_id,
            user_id=current_user.id
        )
        
        return status_info
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get export status: {str(e)}"
        )

@router.get("/export/download/{task_id}")
async def download_export(
    task_id: str,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Download an exported tax report.
    """
    try:
        export_info = await tax_exporter.get_export_file(
            export_id=task_id,
            company_id=current_user.company_id,
            user_id=current_user.id
        )
        
        # In a real implementation, this would stream the file from storage
        # For now, we'll just return a placeholder response
        return {
            "status": "success",
            "download_url": export_info["download_url"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download export: {str(e)}"
        )

@router.post("/cache/invalidate")
async def invalidate_cache(
    tags: List[str] = Query(..., description="Tags to invalidate"),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Invalidate cache entries with the specified tags.
    
    This endpoint requires superuser privileges.
    """
    try:
        count = await report_cache.invalidate_by_tags(tags)
        return {
            "status": "success",
            "message": f"Invalidated {count} cache entries",
            "tags": tags
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to invalidate cache: {str(e)}"
        )

@router.get("/formats", response_model=List[Dict[str, str]])
async def get_export_formats() -> Any:
    """
    Get a list of supported export formats.
    """
    return [
        {"format": fmt.value, "name": fmt.name, "description": ""}
        for fmt in ExportFormat
    ]

# Register the router with the API router
# This is typically done in the main FastAPI app setup
def register_router(api_router: APIRouter) -> None:
    """Register tax reporting routes with the main API router."""
    api_router.include_router(
        router,
        prefix="/tax/reports",
        tags=["tax-reports"]
    )
