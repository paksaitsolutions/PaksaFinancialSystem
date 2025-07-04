"""
Budget Module - API Endpoints
"""
from datetime import date, datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.user import UserInDB
from . import schemas, models, services
from .exceptions import (
    BudgetNotFound,
    BudgetItemNotFound,
    BudgetAdjustmentError,
    BudgetTransactionError,
    BudgetValidationError
)

router = APIRouter(prefix="/budgets", tags=["budgets"])

# Dependency to get budget service
def get_budget_service(db: Session = Depends(get_db)) -> services.BudgetService:
    return services.BudgetService(db)

# Helper function to handle service exceptions
def handle_budget_exception(e: Exception):
    if isinstance(e, (BudgetNotFound, BudgetItemNotFound)):
        raise HTTPException(status_code=404, detail=str(e))
    elif isinstance(e, (BudgetValidationError, BudgetAdjustmentError, BudgetTransactionError)):
        raise HTTPException(status_code=400, detail=str(e))
    else:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

# Budget Endpoints
@router.post(
    "/",
    response_model=schemas.BudgetResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new budget",
    description="Create a new budget with the provided details"
)
async def create_budget(
    budget: schemas.BudgetCreate,
    service: services.BudgetService = Depends(get_budget_service),
    current_user: UserInDB = Depends(get_current_user)
):
    try:
        return service.create_budget(budget, current_user.id)
    except Exception as e:
        handle_budget_exception(e)

@router.get(
    "/{budget_id}",
    response_model=schemas.BudgetResponse,
    summary="Get budget by ID",
    description="Retrieve detailed information about a specific budget"
)
async def get_budget(
    budget_id: UUID,
    service: services.BudgetService = Depends(get_budget_service)
):
    try:
        return service.get_budget(budget_id)
    except Exception as e:
        handle_budget_exception(e)

@router.get(
    "/",
    response_model=schemas.PaginatedResponse[schemas.BudgetResponse],
    summary="List budgets",
    description="List all budgets with optional filtering and pagination"
)
async def list_budgets(
    request: Request,
    status: Optional[models.BudgetStatus] = Query(None, description="Filter by status"),
    budget_type: Optional[models.BudgetType] = Query(None, description="Filter by type"),
    department_id: Optional[UUID] = Query(None, description="Filter by department"),
    project_id: Optional[UUID] = Query(None, description="Filter by project"),
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    q: Optional[str] = Query(None, description="Search term for budget name/description"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    service: services.BudgetService = Depends(get_budget_service)
):
    try:
        skip = (page - 1) * page_size
        budgets, total = service.list_budgets(
            status=status,
            budget_type=budget_type,
            department_id=department_id,
            project_id=project_id,
            start_date=start_date,
            end_date=end_date,
            search_term=q,
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
            "data": budgets,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
            "links": {
                "first": build_url(1),
                "last": build_url((total + page_size - 1) // page_size) if total > 0 else build_url(1),
                "prev": build_url(page - 1) if page > 1 else None,
                "next": build_url(page + 1) if page * page_size < total else None
            }
        }
    except Exception as e:
        handle_budget_exception(e)

@router.put(
    "/{budget_id}",
    response_model=schemas.BudgetResponse,
    summary="Update a budget",
    description="Update an existing budget with the provided details"
)
async def update_budget(
    budget_id: UUID,
    budget_update: schemas.BudgetUpdate,
    service: services.BudgetService = Depends(get_budget_service),
    current_user: UserInDB = Depends(get_current_user)
):
    try:
        return service.update_budget(budget_id, budget_update, current_user.id)
    except Exception as e:
        handle_budget_exception(e)

@router.delete(
    "/{budget_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a budget",
    description="Delete a budget by ID. Only draft budgets can be deleted."
)
async def delete_budget(
    budget_id: UUID,
    service: services.BudgetService = Depends(get_budget_service),
    current_user: UserInDB = Depends(get_current_user)
):
    try:
        service.delete_budget(budget_id)
        return None
    except Exception as e:
        handle_budget_exception(e)

# Budget Item Endpoints
@router.post(
    "/{budget_id}/items",
    response_model=schemas.BudgetItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add item to budget",
    description="Add a new item to the specified budget"
)
async def add_budget_item(
    budget_id: UUID,
    item: schemas.BudgetItemCreate,
    service: services.BudgetService = Depends(get_budget_service),
    current_user: UserInDB = Depends(get_current_user)
):
    try:
        return service.add_budget_item(budget_id, item, current_user.id)
    except Exception as e:
        handle_budget_exception(e)

@router.put(
    "/items/{item_id}",
    response_model=schemas.BudgetItemResponse,
    summary="Update budget item",
    description="Update an existing budget item"
)
async def update_budget_item(
    item_id: UUID,
    item_update: schemas.BudgetItemUpdate,
    service: services.BudgetService = Depends(get_budget_service),
    current_user: UserInDB = Depends(get_current_user)
):
    try:
        return service.update_budget_item(item_id, item_update, current_user.id)
    except Exception as e:
        handle_budget_exception(e)

@router.delete(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete budget item",
    description="Delete a budget item by ID"
)
async def delete_budget_item(
    item_id: UUID,
    service: services.BudgetService = Depends(get_budget_service),
    current_user: UserInDB = Depends(get_current_user)
):
    try:
        service.delete_budget_item(item_id, current_user.id)
        return None
    except Exception as e:
        handle_budget_exception(e)

# Budget Adjustment Endpoints
@router.post(
    "/{budget_id}/adjustments",
    response_model=schemas.BudgetAdjustmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create budget adjustment",
    description="Create a new adjustment for an approved budget"
)
async def create_budget_adjustment(
    budget_id: UUID,
    adjustment: schemas.BudgetAdjustmentCreate,
    service: services.BudgetService = Depends(get_budget_service),
    current_user: UserInDB = Depends(get_current_user)
):
    try:
        return service.adjust_budget(budget_id, adjustment, current_user.id)
    except Exception as e:
        handle_budget_exception(e)

@router.get(
    "/{budget_id}/adjustments",
    response_model=List[schemas.BudgetAdjustmentResponse],
    summary="List budget adjustments",
    description="List all adjustments for a budget"
)
async def list_budget_adjustments(
    budget_id: UUID,
    service: services.BudgetService = Depends(get_budget_service)
):
    try:
        return service.list_budget_adjustments(budget_id)
    except Exception as e:
        handle_budget_exception(e)

# Budget Transaction Endpoints
@router.post(
    "/transactions",
    response_model=schemas.BudgetTransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record budget transaction",
    description="Record a new transaction against a budget item"
)
async def record_transaction(
    transaction: schemas.BudgetTransactionCreate,
    service: services.BudgetService = Depends(get_budget_service),
    current_user: UserInDB = Depends(get_current_user)
):
    try:
        return service.record_transaction(transaction, current_user.id)
    except Exception as e:
        handle_budget_exception(e)

# Reporting Endpoints
@router.get(
    "/{budget_id}/summary",
    response_model=schemas.BudgetSummary,
    summary="Get budget summary",
    description="Get a summary of budget vs. actuals with variance analysis"
)
async def get_budget_summary(
    budget_id: UUID,
    service: services.BudgetService = Depends(get_budget_service)
):
    try:
        return service.get_budget_summary(budget_id)
    except Exception as e:
        handle_budget_exception(e)

@router.get(
    "/reports/budget-vs-actual",
    response_model=schemas.BudgetVsActualReport,
    summary="Budget vs. Actual Report",
    description="Generate a budget vs. actual report for the specified period"
)
async def generate_budget_vs_actual_report(
    start_date: date = Query(..., description="Start date of the report period"),
    end_date: date = Query(..., description="End date of the report period"),
    budget_type: Optional[models.BudgetType] = Query(None, description="Filter by budget type"),
    department_id: Optional[UUID] = Query(None, description="Filter by department"),
    project_id: Optional[UUID] = Query(None, description="Filter by project"),
    group_by: str = Query("month", description="Group by period (day, week, month, quarter, year)"),
    service: services.BudgetService = Depends(get_budget_service)
):
    try:
        return service.generate_budget_vs_actual_report(
            start_date=start_date,
            end_date=end_date,
            budget_type=budget_type,
            department_id=department_id,
            project_id=project_id,
            group_by=group_by
        )
    except Exception as e:
        handle_budget_exception(e)

@router.get(
    "/reports/forecast",
    response_model=schemas.BudgetForecastReport,
    summary="Budget Forecast Report",
    description="Generate a forecast report based on current spending patterns"
)
async def generate_forecast_report(
    forecast_date: date = Query(..., description="Date to forecast until"),
    confidence_level: float = Query(0.95, ge=0.5, le=0.99, description="Confidence level for forecast intervals"),
    budget_id: Optional[UUID] = Query(None, description="Filter by specific budget"),
    service: services.BudgetService = Depends(get_budget_service)
):
    try:
        return service.generate_forecast_report(
            forecast_date=forecast_date,
            confidence_level=confidence_level,
            budget_id=budget_id
        )
    except Exception as e:
        handle_budget_exception(e)

# Dashboard Endpoints
@router.get(
    "/dashboards/overview",
    response_model=schemas.BudgetOverviewDashboard,
    summary="Budget Overview Dashboard",
    description="Get data for the budget overview dashboard"
)
async def get_budget_overview_dashboard(
    time_frame: str = Query("month", description="Time frame for the dashboard (week, month, quarter, year)"),
    service: services.BudgetService = Depends(get_budget_service)
):
    try:
        return service.get_budget_overview_dashboard(time_frame)
    except Exception as e:
        handle_budget_exception(e)

@router.get(
    "/dashboards/department",
    response_model=schemas.DepartmentBudgetDashboard,
    summary="Department Budget Dashboard",
    description="Get department-wise budget data for the dashboard"
)
async def get_department_budget_dashboard(
    department_id: Optional[UUID] = Query(None, description="Filter by department"),
    time_frame: str = Query("month", description="Time frame for the dashboard (week, month, quarter, year)"),
    service: services.BudgetService = Depends(get_budget_service)
):
    try:
        return service.get_department_budget_dashboard(department_id, time_frame)
    except Exception as e:
        handle_budget_exception(e)

# Export Endpoints
@router.get(
    "/{budget_id}/export",
    response_class=JSONResponse,
    summary="Export budget data",
    description="Export budget data in the specified format"
)
async def export_budget(
    budget_id: UUID,
    format: str = Query("json", description="Export format (json, csv, excel, pdf)"),
    include_items: bool = Query(True, description="Include budget items in export"),
    include_transactions: bool = Query(False, description="Include transactions in export"),
    service: services.BudgetService = Depends(get_budget_service)
):
    try:
        export_data = service.export_budget(
            budget_id=budget_id,
            format=format,
            include_items=include_items,
            include_transactions=include_transactions
        )
        
        # Set appropriate content type based on format
        content_type = "application/json"
        if format == "csv":
            content_type = "text/csv"
        elif format == "excel":
            content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        elif format == "pdf":
            content_type = "application/pdf"
        
        return JSONResponse(
            content=export_data,
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename=budget_export_{budget_id}.{format}"
            }
        )
    except Exception as e:
        handle_budget_exception(e)

# Bulk Operations
@router.post(
    "/bulk/create",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Bulk create budgets",
    description="Create multiple budgets in a single operation"
)
async def bulk_create_budgets(
    budgets: List[schemas.BudgetCreate],
    service: services.BudgetService = Depends(get_budget_service),
    current_user: UserInDB = Depends(get_current_user)
):
    try:
        result = service.bulk_create_budgets(budgets, current_user.id)
        return {"status": "processing", "job_id": result.job_id, "message": "Bulk create job started"}
    except Exception as e:
        handle_budget_exception(e)

@router.get(
    "/bulk/status/{job_id}",
    summary="Get bulk operation status",
    description="Get the status of a bulk operation"
)
async def get_bulk_operation_status(
    job_id: str,
    service: services.BudgetService = Depends(get_budget_service)
):
    try:
        return service.get_bulk_operation_status(job_id)
    except Exception as e:
        handle_budget_exception(e)

# Audit Logs
@router.get(
    "/{budget_id}/audit-logs",
    response_model=List[schemas.BudgetAuditLog],
    summary="Get budget audit logs",
    description="Get audit logs for a specific budget"
)
async def get_budget_audit_logs(
    budget_id: UUID,
    action: Optional[str] = Query(None, description="Filter by action type"),
    user_id: Optional[UUID] = Query(None, description="Filter by user ID"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    service: services.BudgetService = Depends(get_budget_service)
):
    try:
        return service.get_budget_audit_logs(
            budget_id=budget_id,
            action=action,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )
    except Exception as e:
        handle_budget_exception(e)

# Data Validation Endpoints
@router.get(
    "/{budget_id}/validate",
    response_model=schemas.BudgetValidationResult,
    summary="Validate budget data",
    description="Run validation checks on a budget and return any issues found"
)
async def validate_budget(
    budget_id: UUID,
    service: services.BudgetService = Depends(get_budget_service)
):
    try:
        return service.validate_budget(budget_id)
    except Exception as e:
        handle_budget_exception(e)

# Integration Endpoints
@router.post(
    "/integrations/import",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Import budget data",
    description="Import budget data from an external system"
)
async def import_budget_data(
    source: str = Query(..., description="Source system identifier"),
    data: Dict[str, Any] = None,
    service: services.BudgetService = Depends(get_budget_service),
    current_user: UserInDB = Depends(get_current_user)
):
    try:
        result = service.import_budget_data(source, data, current_user.id)
        return {
            "status": "processing",
            "import_id": result.import_id,
            "message": f"Import from {source} started"
        }
    except Exception as e:
        handle_budget_exception(e)

@router.get(
    "/integrations/export",
    summary="Export budget data for external systems",
    description="Export budget data in a format suitable for external systems"
)
async def export_budget_for_integration(
    target_system: str = Query(..., description="Target system identifier"),
    budget_id: Optional[UUID] = Query(None, description="Specific budget to export"),
    start_date: Optional[date] = Query(None, description="Start date for data export"),
    end_date: Optional[date] = Query(None, description="End date for data export"),
    service: services.BudgetService = Depends(get_budget_service)
):
    try:
        return service.export_budget_for_integration(
            target_system=target_system,
            budget_id=budget_id,
            start_date=start_date,
            end_date=end_date
        )
    except Exception as e:
        handle_budget_exception(e)

# Webhook Endpoints
@router.post(
    "/webhooks/{webhook_id}",
    status_code=status.HTTP_200_OK,
    summary="Handle budget webhook",
    description="Endpoint for receiving budget-related webhook events"
)
async def handle_budget_webhook(
    webhook_id: str,
    payload: Dict[str, Any],
    service: services.BudgetService = Depends(get_budget_service)
):
    try:
        result = service.handle_webhook(webhook_id, payload)
        return {"status": "processed", "event_id": result.event_id}
    except Exception as e:
        handle_budget_exception(e)

# Health Check Endpoint
@router.get(
    "/health",
    summary="Budget Service Health Check",
    description="Check the health status of the budget service"
)
async def health_check(
    service: services.BudgetService = Depends(get_budget_service)
):
    try:
        status = service.check_health()
        return {"status": "healthy" if status else "unhealthy"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
