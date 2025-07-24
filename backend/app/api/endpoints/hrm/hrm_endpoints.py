"""
API endpoints for HRM.
"""
from typing import Any, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.session import get_db
from app.core.db.router import db_router
from app.core.api_response import success_response, error_response
from app.core.permissions import require_permission, Permission
from app.crud.hrm.hrm_crud import hrm_crud
from app.schemas.hrm.hrm_schemas import (
    EmployeeCreate, EmployeeUpdate, EmployeeResponse,
    LeaveRequestCreate, LeaveRequestUpdate, LeaveRequestResponse,
    AttendanceRecordCreate, AttendanceRecordResponse,
    PerformanceReviewCreate, PerformanceReviewResponse,
    HRAnalytics
)

router = APIRouter()

# Mock tenant and user IDs
MOCK_TENANT_ID = UUID("12345678-1234-5678-9012-123456789012")
MOCK_USER_ID = UUID("12345678-1234-5678-9012-123456789012")

# Employee endpoints
@router.post("/employees", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(
    *,
    db: AsyncSession = Depends(get_db),
    employee_in: EmployeeCreate,
    _: bool = Depends(require_permission(Permission.WRITE)),
) -> Any:
    """Create employee."""
    employee = await hrm_crud.create_employee(
        db, tenant_id=MOCK_TENANT_ID, obj_in=employee_in
    )
    return success_response(
        data=employee,
        message="Employee created successfully",
        status_code=status.HTTP_201_CREATED,
    )

@router.get("/employees", response_model=List[EmployeeResponse])
async def get_employees(
    *,
    db: AsyncSession = Depends(db_router.get_read_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(True),
    department: Optional[str] = Query(None),
    _: bool = Depends(require_permission(Permission.READ)),
) -> Any:
    """Get employees."""
    filters = {}
    if active_only:
        filters["is_active"] = True
    if department:
        filters["department"] = department
    
    employees = await hrm_crud.get_employees(
        db, tenant_id=MOCK_TENANT_ID, skip=skip, limit=limit, filters=filters
    )
    return success_response(data=employees)

# Leave Management endpoints
@router.post("/leave-requests", response_model=LeaveRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_leave_request(
    *,
    db: AsyncSession = Depends(get_db),
    leave_in: LeaveRequestCreate,
    employee_id: UUID = Query(..., description="Employee ID"),
    _: bool = Depends(require_permission(Permission.WRITE)),
) -> Any:
    """Create leave request."""
    try:
        leave_request = await hrm_crud.create_leave_request(
            db, employee_id=employee_id, obj_in=leave_in
        )
        return success_response(
            data=leave_request,
            message="Leave request created successfully",
            status_code=status.HTTP_201_CREATED,
        )
    except ValueError as e:
        return error_response(
            message=str(e),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

@router.post("/leave-requests/{request_id}/approve")
async def approve_leave_request(
    *,
    db: AsyncSession = Depends(get_db),
    request_id: UUID,
    _: bool = Depends(require_permission(Permission.WRITE)),
) -> Any:
    """Approve leave request."""
    # Get leave request (simplified - should use proper query)
    # leave_request = await hrm_crud.get_leave_request(db, id=request_id)
    leave_request = None  # Placeholder - implement proper query
    if not leave_request:
        return error_response(
            message="Leave request not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    
    try:
        leave_request = await hrm_crud.approve_leave_request(
            db, leave_request=leave_request, approved_by=MOCK_USER_ID
        )
        return success_response(
            data=leave_request,
            message="Leave request approved successfully",
        )
    except ValueError as e:
        return error_response(
            message=str(e),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

# Attendance endpoints
@router.post("/attendance", response_model=AttendanceRecordResponse, status_code=status.HTTP_201_CREATED)
async def record_attendance(
    *,
    db: AsyncSession = Depends(get_db),
    attendance_in: AttendanceRecordCreate,
    employee_id: UUID = Query(..., description="Employee ID"),
    _: bool = Depends(require_permission(Permission.WRITE)),
) -> Any:
    """Record attendance."""
    try:
        attendance = await hrm_crud.record_attendance(
            db, employee_id=employee_id, obj_in=attendance_in
        )
        return success_response(
            data=attendance,
            message="Attendance recorded successfully",
            status_code=status.HTTP_201_CREATED,
        )
    except ValueError as e:
        return error_response(
            message=str(e),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

# Performance Management endpoints
@router.post("/performance-reviews", response_model=PerformanceReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_performance_review(
    *,
    db: AsyncSession = Depends(get_db),
    review_in: PerformanceReviewCreate,
    employee_id: UUID = Query(..., description="Employee ID"),
    _: bool = Depends(require_permission(Permission.WRITE)),
) -> Any:
    """Create performance review."""
    review = await hrm_crud.create_performance_review(
        db, employee_id=employee_id, obj_in=review_in
    )
    return success_response(
        data=review,
        message="Performance review created successfully",
        status_code=status.HTTP_201_CREATED,
    )

# Employee Self-Service endpoints
@router.get("/employees/{employee_id}/dashboard")
async def get_employee_dashboard(
    *,
    db: AsyncSession = Depends(db_router.get_read_session),
    employee_id: UUID,
    _: bool = Depends(require_permission(Permission.READ)),
) -> Any:
    """Get employee self-service dashboard."""
    dashboard_data = await hrm_crud.get_employee_dashboard(
        db, employee_id=employee_id
    )
    return success_response(data=dashboard_data)

# Analytics endpoints
@router.get("/analytics", response_model=HRAnalytics)
async def get_hr_analytics(
    *,
    db: AsyncSession = Depends(db_router.get_read_session),
    _: bool = Depends(require_permission(Permission.READ)),
) -> Any:
    """Get HR analytics."""
    analytics = await hrm_crud.get_hr_analytics(
        db, tenant_id=MOCK_TENANT_ID
    )
    return success_response(data=analytics)