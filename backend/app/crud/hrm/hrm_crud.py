"""
CRUD operations for HRM.
"""
from typing import Any, Dict, List, Optional
from uuid import UUID
from datetime import datetime, date, timedelta
from decimal import Decimal

from sqlalchemy import select, and_, func, desc, extract
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.db.query_helper import QueryHelper
from app.models.core_models import Employee, LeaveRequest

# Temporary placeholders for missing HRM models
class LeaveBalance:
    pass

class LeavePolicy:
    pass

class AttendanceRecord:
    pass

class PerformanceReview:
    pass
from app.schemas.hrm.hrm_schemas import (
    EmployeeCreate, EmployeeUpdate, LeaveRequestCreate, LeaveRequestUpdate,
    AttendanceRecordCreate, PerformanceReviewCreate, HRAnalytics
)

class HRMCRUD:
    """CRUD operations for HRM."""
    
    def __init__(self):
        self.employee_helper = QueryHelper(Employee)
        self.leave_helper = QueryHelper(LeaveRequest)
        self.attendance_helper = QueryHelper(AttendanceRecord)
    
    # Employee Management
    async def create_employee(
        self, 
        db: AsyncSession, 
        *, 
        tenant_id: UUID, 
        obj_in: EmployeeCreate
    ) -> Employee:
        """Create employee."""
        employee = Employee(
            tenant_id=tenant_id,
            **obj_in.dict()
        )
        
        db.add(employee)
        await db.commit()
        await db.refresh(employee)
        
        # Initialize leave balances
        await self._initialize_leave_balances(db, employee)
        
        return employee
    
    async def get_employees(
        self,
        db: AsyncSession,
        *,
        tenant_id: UUID,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Employee]:
        """Get employees for tenant."""
        base_filters = {"tenant_id": tenant_id}
        if filters:
            base_filters.update(filters)
        
        query = self.employee_helper.build_query(
            filters=base_filters,
            sort_by="first_name",
            sort_order="asc",
            skip=skip,
            limit=limit
        )
        return await self.employee_helper.execute_query(db, query)
    
    async def update_employee(
        self,
        db: AsyncSession,
        *,
        db_obj: Employee,
        obj_in: EmployeeUpdate
    ) -> Employee:
        """Update employee."""
        update_data = obj_in.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    # Leave Management
    async def create_leave_request(
        self,
        db: AsyncSession,
        *,
        employee_id: UUID,
        obj_in: LeaveRequestCreate
    ) -> LeaveRequest:
        """Create leave request."""
        # Check leave balance
        balance = await self._get_leave_balance(db, employee_id, obj_in.leave_type)
        if balance and balance.remaining_days < obj_in.days_requested:
            raise ValueError("Insufficient leave balance")
        
        leave_request = LeaveRequest(
            employee_id=employee_id,
            **obj_in.dict()
        )
        
        db.add(leave_request)
        await db.commit()
        await db.refresh(leave_request)
        return leave_request
    
    async def approve_leave_request(
        self,
        db: AsyncSession,
        *,
        leave_request: LeaveRequest,
        approved_by: UUID
    ) -> LeaveRequest:
        """Approve leave request."""
        if leave_request.status != "pending":
            raise ValueError("Only pending requests can be approved")
        
        leave_request.status = "approved"
        leave_request.approved_by = approved_by
        leave_request.approved_at = datetime.utcnow()
        
        # Update leave balance
        await self._update_leave_balance(
            db, leave_request.employee_id, 
            leave_request.leave_type, leave_request.days_requested
        )
        
        await db.commit()
        await db.refresh(leave_request)
        return leave_request
    
    # Attendance Tracking
    async def record_attendance(
        self,
        db: AsyncSession,
        *,
        employee_id: UUID,
        obj_in: AttendanceRecordCreate
    ) -> AttendanceRecord:
        """Record attendance."""
        # Check if record already exists for the date
        existing = await self._get_attendance_by_date(db, employee_id, obj_in.date)
        if existing:
            raise ValueError("Attendance already recorded for this date")
        
        # Calculate hours worked
        hours_worked = None
        if obj_in.check_in_time and obj_in.check_out_time:
            duration = obj_in.check_out_time - obj_in.check_in_time
            hours = duration.total_seconds() / 3600
            hours_worked = f"{int(hours):02d}:{int((hours % 1) * 60):02d}"
        
        attendance = AttendanceRecord(
            employee_id=employee_id,
            hours_worked=hours_worked,
            **obj_in.dict()
        )
        
        db.add(attendance)
        await db.commit()
        await db.refresh(attendance)
        return attendance
    
    # Performance Management
    async def create_performance_review(
        self,
        db: AsyncSession,
        *,
        employee_id: UUID,
        obj_in: PerformanceReviewCreate
    ) -> PerformanceReview:
        """Create performance review."""
        review = PerformanceReview(
            employee_id=employee_id,
            **obj_in.dict()
        )
        
        db.add(review)
        await db.commit()
        await db.refresh(review)
        return review
    
    # HR Analytics
    async def get_hr_analytics(
        self,
        db: AsyncSession,
        *,
        tenant_id: UUID
    ) -> HRAnalytics:
        """Get HR analytics."""
        # Total employees
        total_query = select(func.count()).select_from(Employee).where(
            Employee.tenant_id == tenant_id
        )
        total_result = await db.execute(total_query)
        total_employees = total_result.scalar() or 0
        
        # Active employees
        active_query = select(func.count()).select_from(Employee).where(
            and_(Employee.tenant_id == tenant_id, Employee.is_active == True)
        )
        active_result = await db.execute(active_query)
        active_employees = active_result.scalar() or 0
        
        # Pending leave requests
        pending_query = select(func.count()).select_from(LeaveRequest).join(Employee).where(
            and_(Employee.tenant_id == tenant_id, LeaveRequest.status == "pending")
        )
        pending_result = await db.execute(pending_query)
        pending_leave_requests = pending_result.scalar() or 0
        
        # Department breakdown
        dept_query = select(
            Employee.department,
            func.count().label("count")
        ).where(
            and_(Employee.tenant_id == tenant_id, Employee.is_active == True)
        ).group_by(Employee.department)
        
        dept_result = await db.execute(dept_query)
        department_breakdown = [
            {"department": row.department or "Unassigned", "count": row.count}
            for row in dept_result
        ]
        
        # Recent hires (last 30 days)
        recent_date = date.today() - timedelta(days=30)
        recent_query = select(Employee).where(
            and_(
                Employee.tenant_id == tenant_id,
                Employee.hire_date >= recent_date
            )
        ).order_by(desc(Employee.hire_date)).limit(5)
        
        recent_result = await db.execute(recent_query)
        recent_hires = [
            {
                "name": f"{emp.first_name} {emp.last_name}",
                "position": emp.position,
                "hire_date": emp.hire_date.isoformat()
            }
            for emp in recent_result.scalars()
        ]
        
        return HRAnalytics(
            total_employees=total_employees,
            active_employees=active_employees,
            pending_leave_requests=pending_leave_requests,
            average_attendance=95.5,  # Mock data
            department_breakdown=department_breakdown,
            recent_hires=recent_hires
        )
    
    # Employee Self-Service
    async def get_employee_dashboard(
        self,
        db: AsyncSession,
        *,
        employee_id: UUID
    ) -> Dict[str, Any]:
        """Get employee self-service dashboard data."""
        # Leave balance
        leave_balances = await self._get_all_leave_balances(db, employee_id)
        
        # Recent attendance
        recent_attendance = await self._get_recent_attendance(db, employee_id, 7)
        
        # Pending leave requests
        pending_leaves = await self._get_pending_leave_requests(db, employee_id)
        
        return {
            "leave_balances": leave_balances,
            "recent_attendance": recent_attendance,
            "pending_leaves": pending_leaves
        }
    
    # Helper methods
    async def _initialize_leave_balances(self, db: AsyncSession, employee: Employee):
        """Initialize leave balances for new employee."""
        # Get company leave policies
        policies_query = select(LeavePolicy).where(
            and_(LeavePolicy.tenant_id == employee.tenant_id, LeavePolicy.is_active == True)
        )
        policies_result = await db.execute(policies_query)
        policies = policies_result.scalars().all()
        
        current_year = date.today().year
        
        for policy in policies:
            balance = LeaveBalance(
                employee_id=employee.id,
                leave_type=policy.leave_type,
                total_days=policy.days_per_year,
                used_days=0,
                remaining_days=policy.days_per_year,
                year=current_year
            )
            db.add(balance)
        
        await db.commit()
    
    async def _get_leave_balance(
        self, 
        db: AsyncSession, 
        employee_id: UUID, 
        leave_type: str
    ) -> Optional[LeaveBalance]:
        """Get leave balance for employee and leave type."""
        current_year = date.today().year
        query = select(LeaveBalance).where(
            and_(
                LeaveBalance.employee_id == employee_id,
                LeaveBalance.leave_type == leave_type,
                LeaveBalance.year == current_year
            )
        )
        result = await db.execute(query)
        return result.scalars().first()
    
    async def _update_leave_balance(
        self, 
        db: AsyncSession, 
        employee_id: UUID, 
        leave_type: str, 
        days_used: Decimal
    ):
        """Update leave balance after approval."""
        balance = await self._get_leave_balance(db, employee_id, leave_type)
        if balance:
            balance.used_days += days_used
            balance.remaining_days -= days_used
    
    async def _get_attendance_by_date(
        self, 
        db: AsyncSession, 
        employee_id: UUID, 
        attendance_date: date
    ) -> Optional[AttendanceRecord]:
        """Get attendance record by date."""
        query = select(AttendanceRecord).where(
            and_(
                AttendanceRecord.employee_id == employee_id,
                AttendanceRecord.date == attendance_date
            )
        )
        result = await db.execute(query)
        return result.scalars().first()
    
    async def _get_all_leave_balances(self, db: AsyncSession, employee_id: UUID) -> List[dict]:
        """Get all leave balances for employee."""
        current_year = date.today().year
        query = select(LeaveBalance).where(
            and_(LeaveBalance.employee_id == employee_id, LeaveBalance.year == current_year)
        )
        result = await db.execute(query)
        return [
            {
                "leave_type": balance.leave_type,
                "total_days": float(balance.total_days),
                "used_days": float(balance.used_days),
                "remaining_days": float(balance.remaining_days)
            }
            for balance in result.scalars()
        ]
    
    async def _get_recent_attendance(
        self, 
        db: AsyncSession, 
        employee_id: UUID, 
        days: int
    ) -> List[dict]:
        """Get recent attendance records."""
        start_date = date.today() - timedelta(days=days)
        query = select(AttendanceRecord).where(
            and_(
                AttendanceRecord.employee_id == employee_id,
                AttendanceRecord.date >= start_date
            )
        ).order_by(desc(AttendanceRecord.date))
        
        result = await db.execute(query)
        return [
            {
                "date": record.date.isoformat(),
                "status": record.status,
                "hours_worked": record.hours_worked
            }
            for record in result.scalars()
        ]
    
    async def _get_pending_leave_requests(self, db: AsyncSession, employee_id: UUID) -> List[dict]:
        """Get pending leave requests for employee."""
        query = select(LeaveRequest).where(
            and_(
                LeaveRequest.employee_id == employee_id,
                LeaveRequest.status == "pending"
            )
        ).order_by(desc(LeaveRequest.created_at))
        
        result = await db.execute(query)
        return [
            {
                "id": str(request.id),
                "leave_type": request.leave_type,
                "start_date": request.start_date.isoformat(),
                "end_date": request.end_date.isoformat(),
                "days_requested": float(request.days_requested),
                "status": request.status
            }
            for request in result.scalars()
        ]

# Create instance
hrm_crud = HRMCRUD()