"""
HRM API endpoints
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.crud.hrm.hrm_crud import hrm_crud
from app.schemas.hrm.employee import (
    Employee, EmployeeCreate, EmployeeUpdate, EmployeeInDB
)
from app.schemas.hrm.leave import (
    LeaveRequest, LeaveRequestCreate, LeaveRequestUpdate
)
from app.schemas.hrm.attendance import (
    AttendanceRecord, AttendanceRecordCreate
)

router = APIRouter()

# Employee Management
@router.get("/employees", response_model=List[EmployeeInDB])
async def get_employees(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    department: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all employees"""
    filters = {}
    if department:
        filters["department"] = department
    if status:
        filters["status"] = status
    
    employees = await hrm_crud.get_employees(
        db=db,
        tenant_id=current_user["tenant_id"],
        skip=skip,
        limit=limit,
        filters=filters
    )
    
    return [
        {
            "id": str(emp.id),
            "employeeId": emp.employee_id,
            "name": f"{emp.first_name} {emp.last_name}",
            "email": emp.email,
            "phone": emp.phone_number,
            "department": emp.department or "Unassigned",
            "position": emp.job_title,
            "status": "active" if emp.is_active else "inactive",
            "hireDate": emp.hire_date.isoformat() if emp.hire_date else None,
            "salary": float(emp.base_salary) if emp.base_salary else 0
        }
        for emp in employees
    ]

@router.post("/employees", response_model=EmployeeInDB)
async def create_employee(
    employee_data: EmployeeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create new employee"""
    try:
        employee = await hrm_crud.create_employee(
            db=db,
            tenant_id=current_user["tenant_id"],
            obj_in=employee_data
        )
        return {
            "id": str(employee.id),
            "employeeId": employee.employee_id,
            "name": f"{employee.first_name} {employee.last_name}",
            "email": employee.email,
            "phone": employee.phone_number,
            "department": employee.department or "Unassigned",
            "position": employee.job_title,
            "status": "active" if employee.is_active else "inactive"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/employees/{employee_id}", response_model=EmployeeInDB)
async def get_employee(
    employee_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get employee by ID"""
    employee = await hrm_crud.get_employee_by_id(db=db, employee_id=employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    return {
        "id": str(employee.id),
        "employeeId": employee.employee_id,
        "name": f"{employee.first_name} {employee.last_name}",
        "email": employee.email,
        "phone": employee.phone_number,
        "department": employee.department or "Unassigned",
        "position": employee.job_title,
        "status": "active" if employee.is_active else "inactive"
    }

@router.put("/employees/{employee_id}", response_model=EmployeeInDB)
async def update_employee(
    employee_id: UUID,
    employee_data: EmployeeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update employee"""
    employee = await hrm_crud.get_employee_by_id(db=db, employee_id=employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    updated_employee = await hrm_crud.update_employee(
        db=db, db_obj=employee, obj_in=employee_data
    )
    
    return {
        "id": str(updated_employee.id),
        "employeeId": updated_employee.employee_id,
        "name": f"{updated_employee.first_name} {updated_employee.last_name}",
        "email": updated_employee.email,
        "phone": updated_employee.phone_number,
        "department": updated_employee.department or "Unassigned",
        "position": updated_employee.job_title,
        "status": "active" if updated_employee.is_active else "inactive"
    }

@router.delete("/employees/{employee_id}")
async def delete_employee(
    employee_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete employee (soft delete)"""
    employee = await hrm_crud.get_employee_by_id(db=db, employee_id=employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Soft delete by setting is_active to False
    await hrm_crud.update_employee(
        db=db, 
        db_obj=employee, 
        obj_in=EmployeeUpdate(is_active=False)
    )
    
    return {"message": "Employee deleted successfully"}

# Leave Management
@router.get("/leave-requests", response_model=List[Dict[str, Any]])
async def get_leave_requests(
    employee_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get leave requests"""
    filters = {}
    if employee_id:
        filters["employee_id"] = employee_id
    if status:
        filters["status"] = status
    
    requests = await hrm_crud.get_leave_requests(
        db=db,
        tenant_id=current_user["tenant_id"],
        filters=filters
    )
    
    return [
        {
            "id": str(req.id),
            "employeeName": f"{req.employee.first_name} {req.employee.last_name}",
            "leaveType": req.leave_type,
            "startDate": req.start_date.isoformat(),
            "endDate": req.end_date.isoformat(),
            "days": float(req.days_requested),
            "reason": req.reason,
            "status": req.status,
            "submittedDate": req.created_at.isoformat()
        }
        for req in requests
    ]

@router.post("/leave-requests", response_model=Dict[str, Any])
async def create_leave_request(
    leave_data: LeaveRequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create leave request"""
    try:
        leave_request = await hrm_crud.create_leave_request(
            db=db,
            employee_id=leave_data.employee_id,
            obj_in=leave_data
        )
        return {
            "id": str(leave_request.id),
            "status": leave_request.status,
            "message": "Leave request created successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/leave-requests/{request_id}/approve")
async def approve_leave_request(
    request_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Approve leave request"""
    leave_request = await hrm_crud.get_leave_request_by_id(db=db, request_id=request_id)
    if not leave_request:
        raise HTTPException(status_code=404, detail="Leave request not found")
    
    try:
        approved_request = await hrm_crud.approve_leave_request(
            db=db,
            leave_request=leave_request,
            approved_by=current_user["user_id"]
        )
        return {
            "id": str(approved_request.id),
            "status": approved_request.status,
            "message": "Leave request approved"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/leave-requests/{request_id}/reject")
async def reject_leave_request(
    request_id: UUID,
    reason: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Reject leave request"""
    leave_request = await hrm_crud.get_leave_request_by_id(db=db, request_id=request_id)
    if not leave_request:
        raise HTTPException(status_code=404, detail="Leave request not found")
    
    rejected_request = await hrm_crud.reject_leave_request(
        db=db,
        leave_request=leave_request,
        rejected_by=current_user["user_id"],
        rejection_reason=reason
    )
    
    return {
        "id": str(rejected_request.id),
        "status": rejected_request.status,
        "message": "Leave request rejected"
    }

# Attendance Management
@router.get("/attendance", response_model=List[Dict[str, Any]])
async def get_attendance_records(
    employee_id: Optional[UUID] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get attendance records"""
    filters = {}
    if employee_id:
        filters["employee_id"] = employee_id
    if start_date:
        filters["start_date"] = start_date
    if end_date:
        filters["end_date"] = end_date
    
    records = await hrm_crud.get_attendance_records(
        db=db,
        tenant_id=current_user["tenant_id"],
        filters=filters
    )
    
    return [
        {
            "id": str(record.id),
            "employeeName": f"{record.employee.first_name} {record.employee.last_name}",
            "date": record.date.isoformat(),
            "checkIn": record.check_in_time.isoformat() if record.check_in_time else None,
            "checkOut": record.check_out_time.isoformat() if record.check_out_time else None,
            "hoursWorked": record.hours_worked,
            "status": record.status
        }
        for record in records
    ]

@router.post("/attendance", response_model=Dict[str, Any])
async def record_attendance(
    attendance_data: AttendanceRecordCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Record attendance"""
    try:
        attendance = await hrm_crud.record_attendance(
            db=db,
            employee_id=attendance_data.employee_id,
            obj_in=attendance_data
        )
        return {
            "id": str(attendance.id),
            "message": "Attendance recorded successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Departments
@router.get("/departments", response_model=List[Dict[str, Any]])
async def get_departments(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all departments"""
    departments = await hrm_crud.get_departments(
        db=db,
        tenant_id=current_user["tenant_id"]
    )
    
    return [
        {
            "id": str(dept.id),
            "name": dept.name,
            "description": dept.description,
            "manager": dept.manager_name if hasattr(dept, 'manager_name') else None,
            "employeeCount": dept.employee_count if hasattr(dept, 'employee_count') else 0
        }
        for dept in departments
    ]

# Analytics
@router.get("/analytics", response_model=Dict[str, Any])
async def get_hr_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get HR analytics"""
    analytics = await hrm_crud.get_hr_analytics(
        db=db,
        tenant_id=current_user["tenant_id"]
    )
    
    return {
        "totalEmployees": analytics.total_employees,
        "activeEmployees": analytics.active_employees,
        "pendingLeaveRequests": analytics.pending_leave_requests,
        "averageAttendance": analytics.average_attendance,
        "departmentBreakdown": analytics.department_breakdown,
        "recentHires": analytics.recent_hires
    }

# Employee Self-Service
@router.get("/employees/{employee_id}/dashboard", response_model=Dict[str, Any])
async def get_employee_dashboard(
    employee_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get employee self-service dashboard"""
    dashboard_data = await hrm_crud.get_employee_dashboard(
        db=db,
        employee_id=employee_id
    )
    
    return dashboard_data