"""
Comprehensive HRM API Endpoints
"""
from typing import Any, List, Optional
from uuid import UUID
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.session import get_db
from app.core.api_response import success_response, error_response
from app.services.hrm_service import hrm_service
from app.schemas.hrm.hrm_schemas import (
    EmployeeCreate, EmployeeUpdate, EmployeeResponse,
    DepartmentCreate, DepartmentUpdate, DepartmentResponse,
    LeaveRequestCreate, LeaveRequestUpdate, LeaveRequestResponse,
    AttendanceRecordCreate, AttendanceRecordUpdate, AttendanceRecordResponse,
    PerformanceReviewCreate, PerformanceReviewUpdate, PerformanceReviewResponse,
    TrainingRecordCreate, TrainingRecordUpdate, TrainingRecordResponse,
    PolicyCreate, PolicyUpdate, PolicyResponse,
    JobOpeningCreate, JobOpeningUpdate, JobOpeningResponse,
    CandidateCreate, CandidateUpdate, CandidateResponse,
    InterviewCreate, InterviewUpdate, InterviewResponse,
    HRAnalytics, EmployeeDashboard
)

router = APIRouter()

# Employee Management Endpoints
@router.post("/employees", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(
    *,
    db: AsyncSession = Depends(get_db),
    employee_in: EmployeeCreate,
) -> Any:
    """Create new employee."""
    try:
        employee = await hrm_service.create_employee(db, employee_in)
        return success_response(
            data=employee,
            message="Employee created successfully",
            status_code=status.HTTP_201_CREATED,
        )
    except Exception as e:
        return error_response(
            message=str(e),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

@router.get("/employees", response_model=List[EmployeeResponse])
async def get_employees(
    *,
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    department_id: Optional[UUID] = Query(None),
    is_active: Optional[bool] = Query(True),
    search: Optional[str] = Query(None),
) -> Any:
    """Get employees with filters."""
    try:
        employees = await hrm_service.get_employees(
            db, 
            skip=skip, 
            limit=limit, 
            department_id=department_id, 
            is_active=is_active,
            search=search
        )
        return success_response(data=employees)
    except Exception as e:
        return error_response(
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

@router.get("/employees/{employee_id}", response_model=EmployeeResponse)
async def get_employee(
    *,
    db: AsyncSession = Depends(get_db),
    employee_id: UUID,
) -> Any:
    """Get employee by ID."""
    try:
        employee = await hrm_service.get_employee_by_id(db, employee_id)
        if not employee:
            return error_response(
                message="Employee not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return success_response(data=employee)
    except Exception as e:
        return error_response(
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

@router.put("/employees/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    *,
    db: AsyncSession = Depends(get_db),
    employee_id: UUID,
    employee_in: EmployeeUpdate,
) -> Any:
    """Update employee."""
    try:
        employee = await hrm_service.update_employee(db, employee_id, employee_in)
        if not employee:
            return error_response(
                message="Employee not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return success_response(
            data=employee,
            message="Employee updated successfully",
        )
    except Exception as e:
        return error_response(
            message=str(e),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

@router.delete("/employees/{employee_id}")
async def delete_employee(
    *,
    db: AsyncSession = Depends(get_db),
    employee_id: UUID,
) -> Any:
    """Delete employee (soft delete)."""
    try:
        employee = await hrm_service.update_employee(
            db, employee_id, EmployeeUpdate(is_active=False)
        )
        if not employee:
            return error_response(
                message="Employee not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return success_response(message="Employee deleted successfully")
    except Exception as e:
        return error_response(
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

# Department Management Endpoints
@router.post("/departments", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
async def create_department(
    *,
    db: AsyncSession = Depends(get_db),
    department_in: DepartmentCreate,
) -> Any:
    """Create new department."""
    try:
        department = await hrm_service.create_department(db, department_in)
        return success_response(
            data=department,
            message="Department created successfully",
            status_code=status.HTTP_201_CREATED,
        )
    except Exception as e:
        return error_response(
            message=str(e),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

@router.get("/departments", response_model=List[DepartmentResponse])
async def get_departments(
    *,
    db: AsyncSession = Depends(get_db),
    include_inactive: bool = Query(False),
) -> Any:
    """Get all departments."""
    try:
        departments = await hrm_service.get_departments(db, include_inactive=include_inactive)
        return success_response(data=departments)
    except Exception as e:
        return error_response(
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

# Leave Management Endpoints
@router.post("/leave-requests", response_model=LeaveRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_leave_request(
    *,
    db: AsyncSession = Depends(get_db),
    leave_in: LeaveRequestCreate,
    employee_id: UUID = Query(..., description="Employee ID"),
) -> Any:
    """Create leave request."""
    try:
        leave_request = await hrm_service.create_leave_request(db, leave_in, employee_id)
        return success_response(
            data=leave_request,
            message="Leave request created successfully",
            status_code=status.HTTP_201_CREATED,
        )
    except Exception as e:
        return error_response(
            message=str(e),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

@router.get("/leave-requests", response_model=List[LeaveRequestResponse])
async def get_leave_requests(
    *,
    db: AsyncSession = Depends(get_db),
    employee_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
) -> Any:
    """Get leave requests with filters."""
    try:
        leave_requests = await hrm_service.get_leave_requests(
            db, 
            employee_id=employee_id, 
            status=status,
            start_date=start_date,
            end_date=end_date
        )
        return success_response(data=leave_requests)
    except Exception as e:
        return error_response(
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

@router.post("/leave-requests/{request_id}/approve")
async def approve_leave_request(
    *,
    db: AsyncSession = Depends(get_db),
    request_id: UUID,
    approved_by: UUID = Query(..., description="Approver ID"),
) -> Any:
    """Approve leave request."""
    try:
        leave_request = await hrm_service.approve_leave_request(db, request_id, approved_by)
        if not leave_request:
            return error_response(
                message="Leave request not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return success_response(
            data=leave_request,
            message="Leave request approved successfully",
        )
    except Exception as e:
        return error_response(
            message=str(e),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

# Attendance Management Endpoints
@router.post("/attendance", response_model=AttendanceRecordResponse, status_code=status.HTTP_201_CREATED)
async def record_attendance(
    *,
    db: AsyncSession = Depends(get_db),
    attendance_in: AttendanceRecordCreate,
    employee_id: UUID = Query(..., description="Employee ID"),
) -> Any:
    """Record attendance."""
    try:
        attendance = await hrm_service.record_attendance(db, attendance_in, employee_id)
        return success_response(
            data=attendance,
            message="Attendance recorded successfully",
            status_code=status.HTTP_201_CREATED,
        )
    except Exception as e:
        return error_response(
            message=str(e),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

@router.get("/attendance", response_model=List[AttendanceRecordResponse])
async def get_attendance_records(
    *,
    db: AsyncSession = Depends(get_db),
    employee_id: Optional[UUID] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
) -> Any:
    """Get attendance records."""
    try:
        records = await hrm_service.get_attendance_records(
            db, 
            employee_id=employee_id,
            start_date=start_date,
            end_date=end_date
        )
        return success_response(data=records)
    except Exception as e:
        return error_response(
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

# Performance Management Endpoints
@router.post("/performance-reviews", response_model=PerformanceReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_performance_review(
    *,
    db: AsyncSession = Depends(get_db),
    review_in: PerformanceReviewCreate,
    employee_id: UUID = Query(..., description="Employee ID"),
    reviewer_id: UUID = Query(..., description="Reviewer ID"),
) -> Any:
    """Create performance review."""
    try:
        review = await hrm_service.create_performance_review(db, review_in, employee_id, reviewer_id)
        return success_response(
            data=review,
            message="Performance review created successfully",
            status_code=status.HTTP_201_CREATED,
        )
    except Exception as e:
        return error_response(
            message=str(e),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

@router.get("/performance-reviews", response_model=List[PerformanceReviewResponse])
async def get_performance_reviews(
    *,
    db: AsyncSession = Depends(get_db),
    employee_id: Optional[UUID] = Query(None),
    year: Optional[int] = Query(None),
) -> Any:
    """Get performance reviews."""
    try:
        reviews = await hrm_service.get_performance_reviews(
            db, 
            employee_id=employee_id,
            year=year
        )
        return success_response(data=reviews)
    except Exception as e:
        return error_response(
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

# Policy Management Endpoints
@router.post("/policies", response_model=PolicyResponse, status_code=status.HTTP_201_CREATED)
async def create_policy(
    *,
    db: AsyncSession = Depends(get_db),
    policy_in: PolicyCreate,
) -> Any:
    """Create new policy."""
    try:
        policy = await hrm_service.create_policy(db, policy_in)
        return success_response(
            data=policy,
            message="Policy created successfully",
            status_code=status.HTTP_201_CREATED,
        )
    except Exception as e:
        return error_response(
            message=str(e),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

@router.get("/policies", response_model=List[PolicyResponse])
async def get_policies(
    *,
    db: AsyncSession = Depends(get_db),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
) -> Any:
    """Get policies with filters."""
    try:
        policies = await hrm_service.get_policies(db, category=category, status=status)
        return success_response(data=policies)
    except Exception as e:
        return error_response(
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

# Analytics Endpoints
@router.get("/analytics", response_model=HRAnalytics)
async def get_hr_analytics(
    *,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get HR analytics dashboard data."""
    try:
        analytics = await hrm_service.get_hr_analytics(db)
        return success_response(data=analytics)
    except Exception as e:
        return error_response(
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

# Employee Self-Service Endpoints
@router.get("/employees/{employee_id}/dashboard", response_model=EmployeeDashboard)
async def get_employee_dashboard(
    *,
    db: AsyncSession = Depends(get_db),
    employee_id: UUID,
) -> Any:
    """Get employee self-service dashboard."""
    try:
        # This would be implemented in the service
        dashboard_data = {
            "employee": await hrm_service.get_employee_by_id(db, employee_id),
            "pending_leave_requests": await hrm_service.get_leave_requests(db, employee_id=employee_id, status="PENDING"),
            "recent_attendance": await hrm_service.get_attendance_records(db, employee_id=employee_id),
            "upcoming_reviews": await hrm_service.get_performance_reviews(db, employee_id=employee_id),
            "training_progress": [],  # Would be implemented
            "team_members": []  # Would be implemented
        }
        return success_response(data=dashboard_data)
    except Exception as e:
        return error_response(
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )