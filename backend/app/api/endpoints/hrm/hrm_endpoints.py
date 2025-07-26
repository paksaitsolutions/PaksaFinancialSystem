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
from app.services.hrm.performance_service import PerformanceService
from app.services.hrm.succession_service import SuccessionService

router = APIRouter()

# Mock tenant and user IDs
MOCK_TENANT_ID = UUID("12345678-1234-5678-9012-123456789012")
MOCK_USER_ID = UUID("12345678-1234-5678-9012-123456789012")

# Initialize services
performance_service = PerformanceService()
succession_service = SuccessionService()

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

# Advanced Performance Management endpoints
@router.post("/performance-reviews/{review_id}/complete")
async def complete_performance_review(
    *,
    db: AsyncSession = Depends(get_db),
    review_id: UUID,
    completion_data: dict,
    _: bool = Depends(require_permission(Permission.WRITE)),
) -> Any:
    """Complete performance review."""
    performance_service = PerformanceService()
    try:
        review = await performance_service.complete_performance_review(
            db, review_id=review_id, completion_data=completion_data
        )
        return success_response(
            data=review,
            message="Performance review completed successfully"
        )
    except ValueError as e:
        return error_response(
            message=str(e),
            status_code=status.HTTP_400_BAD_REQUEST
        )

@router.post("/employees/{employee_id}/goals")
async def create_employee_goal(
    *,
    db: AsyncSession = Depends(get_db),
    employee_id: UUID,
    goal_data: dict,
    _: bool = Depends(require_permission(Permission.WRITE)),
) -> Any:
    """Create employee goal."""
    performance_service = PerformanceService()
    goal = await performance_service.create_employee_goal(
        db, employee_id=employee_id, goal_data=goal_data
    )
    return success_response(
        data=goal,
        message="Goal created successfully",
        status_code=status.HTTP_201_CREATED
    )

@router.get("/employees/{employee_id}/performance-summary")
async def get_employee_performance_summary(
    *,
    db: AsyncSession = Depends(db_router.get_read_session),
    employee_id: UUID,
    year: Optional[int] = Query(None),
    _: bool = Depends(require_permission(Permission.READ)),
) -> Any:
    """Get employee performance summary."""
    performance_service = PerformanceService()
    summary = await performance_service.get_employee_performance_summary(
        db, employee_id=employee_id, year=year
    )
    return success_response(data=summary)

@router.get("/performance/team-analytics")
async def get_team_performance_analytics(
    *,
    db: AsyncSession = Depends(db_router.get_read_session),
    department: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    _: bool = Depends(require_permission(Permission.READ)),
) -> Any:
    """Get team performance analytics."""
    performance_service = PerformanceService()
    analytics = await performance_service.get_team_performance_analytics(
        db, tenant_id=MOCK_TENANT_ID, department=department, year=year
    )
    return success_response(data=analytics)

# Succession Planning endpoints
@router.post("/succession-plans")
async def create_succession_plan(
    *,
    db: AsyncSession = Depends(get_db),
    plan_data: dict,
    _: bool = Depends(require_permission(Permission.WRITE)),
) -> Any:
    """Create succession plan."""
    succession_service = SuccessionService()
    plan = await succession_service.create_succession_plan(
        db, tenant_id=MOCK_TENANT_ID, plan_data=plan_data
    )
    return success_response(
        data=plan,
        message="Succession plan created successfully",
        status_code=status.HTTP_201_CREATED
    )

@router.get("/succession-plans")
async def get_succession_plans(
    *,
    db: AsyncSession = Depends(db_router.get_read_session),
    department: Optional[str] = Query(None),
    risk_level: Optional[str] = Query(None),
    _: bool = Depends(require_permission(Permission.READ)),
) -> Any:
    """Get succession plans."""
    succession_service = SuccessionService()
    plans = await succession_service.get_succession_plans(
        db, tenant_id=MOCK_TENANT_ID, department=department, risk_level=risk_level
    )
    return success_response(data=plans)

@router.post("/succession-plans/{plan_id}/candidates")
async def add_succession_candidate(
    *,
    db: AsyncSession = Depends(get_db),
    plan_id: UUID,
    employee_id: UUID = Query(...),
    candidate_data: dict,
    _: bool = Depends(require_permission(Permission.WRITE)),
) -> Any:
    """Add succession candidate."""
    succession_service = SuccessionService()
    candidate = await succession_service.add_succession_candidate(
        db, succession_plan_id=plan_id, employee_id=employee_id, candidate_data=candidate_data
    )
    return success_response(
        data=candidate,
        message="Succession candidate added successfully",
        status_code=status.HTTP_201_CREATED
    )

@router.get("/succession/readiness-report")
async def get_succession_readiness_report(
    *,
    db: AsyncSession = Depends(db_router.get_read_session),
    _: bool = Depends(require_permission(Permission.READ)),
) -> Any:
    """Get succession readiness report."""
    succession_service = SuccessionService()
    report = await succession_service.get_succession_readiness_report(
        db, tenant_id=MOCK_TENANT_ID
    )
    return success_response(data=report)

# Development Planning endpoints
@router.post("/employees/{employee_id}/development-plans")
async def create_development_plan(
    *,
    db: AsyncSession = Depends(get_db),
    employee_id: UUID,
    plan_data: dict,
    _: bool = Depends(require_permission(Permission.WRITE)),
) -> Any:
    """Create employee development plan."""
    succession_service = SuccessionService()
    plan = await succession_service.create_development_plan(
        db, employee_id=employee_id, plan_data=plan_data
    )
    return success_response(
        data=plan,
        message="Development plan created successfully",
        status_code=status.HTTP_201_CREATED
    )

@router.get("/employees/{employee_id}/development-dashboard")
async def get_employee_development_dashboard(
    *,
    db: AsyncSession = Depends(db_router.get_read_session),
    employee_id: UUID,
    _: bool = Depends(require_permission(Permission.READ)),
) -> Any:
    """Get employee development dashboard."""
    succession_service = SuccessionService()
    dashboard = await succession_service.get_employee_development_dashboard(
        db, employee_id=employee_id
    )
    return success_response(data=dashboard)