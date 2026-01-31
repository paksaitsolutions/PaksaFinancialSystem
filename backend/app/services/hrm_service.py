"""
Comprehensive HRM Service
"""
from datetime import date, datetime, timedelta
from typing import List, Optional, Dict, Any

from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from uuid import UUID

from app.models.hrm_models import (
from app.schemas.hrm.hrm_schemas import (


    Employee, Department, LeaveRequest, AttendanceRecord, 
    PerformanceReview, TrainingRecord, Policy, JobOpening, 
    Candidate, Interview
)
    EmployeeCreate, EmployeeUpdate, DepartmentCreate,
    LeaveRequestCreate, AttendanceRecordCreate, 
    PerformanceReviewCreate, PolicyCreate
)

class HRMService:
    """Comprehensive HRM Service with real-time data integration"""
    
    def __init__(self):
        """  Init  ."""
        self.mock_tenant_id = UUID("12345678-1234-5678-9012-123456789012")
    
    # Employee Management
    async def create_employee(
        self, 
        db: AsyncSession, 
        employee_data: EmployeeCreate,
        tenant_id: UUID = None
    ) -> Employee:
        """Create Employee."""
        """Create a new employee"""
        tenant_id = tenant_id or self.mock_tenant_id
        
        employee = Employee(
            tenant_id=tenant_id,
            employee_id=employee_data.employee_id,
            first_name=employee_data.first_name,
            middle_name=employee_data.middle_name,
            last_name=employee_data.last_name,
            email=employee_data.email,
            phone_number=employee_data.phone_number,
            date_of_birth=employee_data.date_of_birth,
            gender=employee_data.gender,
            job_title=employee_data.job_title,
            department_id=employee_data.department_id,
            hire_date=employee_data.hire_date,
            employment_type=employee_data.employment_type,
            base_salary=employee_data.base_salary,
            manager_id=employee_data.manager_id
        )
        
        db.add(employee)
        await db.commit()
        await db.refresh(employee)
        return employee
    
    async def get_employees(
        self,
        db: AsyncSession,
        tenant_id: UUID = None,
        skip: int = 0,
        limit: int = 100,
        department_id: UUID = None,
        is_active: bool = True,
        search: str = None
    ) -> List[Employee]:
        """Get Employees."""
        """Get employees with filters"""
        tenant_id = tenant_id or self.mock_tenant_id
        
        query = select(Employee).options(
            selectinload(Employee.department),
            selectinload(Employee.manager)
        ).where(Employee.tenant_id == tenant_id)
        
        if is_active is not None:
            query = query.where(Employee.is_active == is_active)
        
        if department_id:
            query = query.where(Employee.department_id == department_id)
        
        if search:
            search_filter = or_(
                Employee.first_name.ilike(f"%{search}%"),
                Employee.last_name.ilike(f"%{search}%"),
                Employee.email.ilike(f"%{search}%"),
                Employee.employee_id.ilike(f"%{search}%")
            )
            query = query.where(search_filter)
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_employee_by_id(
        self, 
        db: AsyncSession, 
        employee_id: UUID,
        tenant_id: UUID = None
    ) -> Optional[Employee]:
        """Get Employee By Id."""
        """Get employee by ID"""
        tenant_id = tenant_id or self.mock_tenant_id
        
        query = select(Employee).options(
            selectinload(Employee.department),
            selectinload(Employee.manager),
            selectinload(Employee.direct_reports)
        ).where(
            and_(Employee.id == employee_id, Employee.tenant_id == tenant_id)
        )
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def update_employee(
        self,
        db: AsyncSession,
        employee_id: UUID,
        employee_data: EmployeeUpdate,
        tenant_id: UUID = None
    ) -> Optional[Employee]:
        """Update Employee."""
        """Update employee"""
        employee = await self.get_employee_by_id(db, employee_id, tenant_id)
        if not employee:
            return None
        
        for field, value in employee_data.dict(exclude_unset=True).items():
            setattr(employee, field, value)
        
        employee.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(employee)
        return employee
    
    # Department Management
    async def create_department(
        self,
        db: AsyncSession,
        department_data: DepartmentCreate,
        tenant_id: UUID = None
    ) -> Department:
        """Create Department."""
        """Create a new department"""
        tenant_id = tenant_id or self.mock_tenant_id
        
        department = Department(
            tenant_id=tenant_id,
            name=department_data.name,
            description=department_data.description,
            manager_id=department_data.manager_id,
            parent_department_id=department_data.parent_department_id,
            budget=department_data.budget
        )
        
        db.add(department)
        await db.commit()
        await db.refresh(department)
        return department
    
    async def get_departments(
        self,
        db: AsyncSession,
        tenant_id: UUID = None,
        include_inactive: bool = False
    ) -> List[Department]:
        """Get Departments."""
        """Get all departments"""
        tenant_id = tenant_id or self.mock_tenant_id
        
        query = select(Department).options(
            selectinload(Department.manager),
            selectinload(Department.employees)
        ).where(Department.tenant_id == tenant_id)
        
        if not include_inactive:
            query = query.where(Department.is_active == True)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    # Leave Management
    async def create_leave_request(
        self,
        db: AsyncSession,
        leave_data: LeaveRequestCreate,
        employee_id: UUID,
        tenant_id: UUID = None
    ) -> LeaveRequest:
        """Create Leave Request."""
        """Create a leave request"""
        tenant_id = tenant_id or self.mock_tenant_id
        
        # Calculate days
        days_requested = (leave_data.end_date - leave_data.start_date).days + 1
        
        leave_request = LeaveRequest(
            tenant_id=tenant_id,
            employee_id=employee_id,
            leave_type=leave_data.leave_type,
            start_date=leave_data.start_date,
            end_date=leave_data.end_date,
            days_requested=days_requested,
            reason=leave_data.reason
        )
        
        db.add(leave_request)
        await db.commit()
        await db.refresh(leave_request)
        return leave_request
    
    async def get_leave_requests(
        self,
        db: AsyncSession,
        tenant_id: UUID = None,
        employee_id: UUID = None,
        status: str = None,
        start_date: date = None,
        end_date: date = None
    ) -> List[LeaveRequest]:
        """Get Leave Requests."""
        """Get leave requests with filters"""
        tenant_id = tenant_id or self.mock_tenant_id
        
        query = select(LeaveRequest).options(
            selectinload(LeaveRequest.employee),
            selectinload(LeaveRequest.approver)
        ).where(LeaveRequest.tenant_id == tenant_id)
        
        if employee_id:
            query = query.where(LeaveRequest.employee_id == employee_id)
        
        if status:
            query = query.where(LeaveRequest.status == status)
        
        if start_date:
            query = query.where(LeaveRequest.start_date >= start_date)
        
        if end_date:
            query = query.where(LeaveRequest.end_date <= end_date)
        
        query = query.order_by(desc(LeaveRequest.created_at))
        result = await db.execute(query)
        return result.scalars().all()
    
    async def approve_leave_request(
        self,
        db: AsyncSession,
        request_id: UUID,
        approved_by: UUID,
        tenant_id: UUID = None
    ) -> Optional[LeaveRequest]:
        """Approve Leave Request."""
        """Approve a leave request"""
        tenant_id = tenant_id or self.mock_tenant_id
        
        query = select(LeaveRequest).where(
            and_(
                LeaveRequest.id == request_id,
                LeaveRequest.tenant_id == tenant_id
            )
        )
        result = await db.execute(query)
        leave_request = result.scalar_one_or_none()
        
        if leave_request:
            leave_request.status = "APPROVED"
            leave_request.approved_by = approved_by
            leave_request.approved_at = datetime.utcnow()
            await db.commit()
            await db.refresh(leave_request)
        
        return leave_request
    
    # Attendance Management
    async def record_attendance(
        self,
        db: AsyncSession,
        attendance_data: AttendanceRecordCreate,
        employee_id: UUID,
        tenant_id: UUID = None
    ) -> AttendanceRecord:
        """Record Attendance."""
        """Record attendance"""
        tenant_id = tenant_id or self.mock_tenant_id
        
        # Check if record already exists for this date
        existing_query = select(AttendanceRecord).where(
            and_(
                AttendanceRecord.employee_id == employee_id,
                AttendanceRecord.date == attendance_data.date,
                AttendanceRecord.tenant_id == tenant_id
            )
        )
        result = await db.execute(existing_query)
        existing_record = result.scalar_one_or_none()
        
        if existing_record:
            # Update existing record
            for field, value in attendance_data.dict(exclude_unset=True).items():
                setattr(existing_record, field, value)
            
            # Calculate total hours if both check-in and check-out are present
            if existing_record.check_in_time and existing_record.check_out_time:
                duration = existing_record.check_out_time - existing_record.check_in_time
                total_hours = duration.total_seconds() / 3600
                if existing_record.break_duration:
                    total_hours -= existing_record.break_duration / 60
                existing_record.total_hours = round(total_hours, 2)
            
            await db.commit()
            await db.refresh(existing_record)
            return existing_record
        else:
            # Create new record
            attendance = AttendanceRecord(
                tenant_id=tenant_id,
                employee_id=employee_id,
                **attendance_data.dict()
            )
            
            db.add(attendance)
            await db.commit()
            await db.refresh(attendance)
            return attendance
    
    async def get_attendance_records(
        self,
        db: AsyncSession,
        tenant_id: UUID = None,
        employee_id: UUID = None,
        start_date: date = None,
        end_date: date = None
    ) -> List[AttendanceRecord]:
        """Get Attendance Records."""
        """Get attendance records"""
        tenant_id = tenant_id or self.mock_tenant_id
        
        query = select(AttendanceRecord).options(
            selectinload(AttendanceRecord.employee)
        ).where(AttendanceRecord.tenant_id == tenant_id)
        
        if employee_id:
            query = query.where(AttendanceRecord.employee_id == employee_id)
        
        if start_date:
            query = query.where(AttendanceRecord.date >= start_date)
        
        if end_date:
            query = query.where(AttendanceRecord.date <= end_date)
        
        query = query.order_by(desc(AttendanceRecord.date))
        result = await db.execute(query)
        return result.scalars().all()
    
    # Performance Management
    async def create_performance_review(
        self,
        db: AsyncSession,
        review_data: PerformanceReviewCreate,
        employee_id: UUID,
        reviewer_id: UUID,
        tenant_id: UUID = None
    ) -> PerformanceReview:
        """Create Performance Review."""
        """Create performance review"""
        tenant_id = tenant_id or self.mock_tenant_id
        
        review = PerformanceReview(
            tenant_id=tenant_id,
            employee_id=employee_id,
            reviewer_id=reviewer_id,
            **review_data.dict()
        )
        
        db.add(review)
        await db.commit()
        await db.refresh(review)
        return review
    
    async def get_performance_reviews(
        self,
        db: AsyncSession,
        tenant_id: UUID = None,
        employee_id: UUID = None,
        year: int = None
    ) -> List[PerformanceReview]:
        """Get Performance Reviews."""
        """Get performance reviews"""
        tenant_id = tenant_id or self.mock_tenant_id
        
        query = select(PerformanceReview).options(
            selectinload(PerformanceReview.employee),
            selectinload(PerformanceReview.reviewer)
        ).where(PerformanceReview.tenant_id == tenant_id)
        
        if employee_id:
            query = query.where(PerformanceReview.employee_id == employee_id)
        
        if year:
            start_date = date(year, 1, 1)
            end_date = date(year, 12, 31)
            query = query.where(
                and_(
                    PerformanceReview.review_date >= start_date,
                    PerformanceReview.review_date <= end_date
                )
            )
        
        query = query.order_by(desc(PerformanceReview.review_date))
        result = await db.execute(query)
        return result.scalars().all()
    
    # Analytics and Reporting
    async def get_hr_analytics(
        self,
        db: AsyncSession,
        tenant_id: UUID = None
    ) -> Dict[str, Any]:
        """Get Hr Analytics."""
        """Get HR analytics dashboard data"""
        tenant_id = tenant_id or self.mock_tenant_id
        
        # Employee counts
        total_employees_query = select(func.count(Employee.id)).where(
            Employee.tenant_id == tenant_id
        )
        active_employees_query = select(func.count(Employee.id)).where(
            and_(Employee.tenant_id == tenant_id, Employee.is_active == True)
        )
        
        # Leave requests
        pending_leave_query = select(func.count(LeaveRequest.id)).where(
            and_(
                LeaveRequest.tenant_id == tenant_id,
                LeaveRequest.status == "PENDING"
            )
        )
        
        # Department breakdown
        dept_breakdown_query = select(
            Department.name,
            func.count(Employee.id).label('employee_count')
        ).select_from(
            Department
        ).outerjoin(Employee).where(
            and_(
                Department.tenant_id == tenant_id,
                Department.is_active == True
            )
        ).group_by(Department.name)
        
        # Recent hires (last 30 days)
        thirty_days_ago = date.today() - timedelta(days=30)
        recent_hires_query = select(Employee).where(
            and_(
                Employee.tenant_id == tenant_id,
                Employee.hire_date >= thirty_days_ago,
                Employee.is_active == True
            )
        ).order_by(desc(Employee.hire_date)).limit(10)
        
        # Execute queries
        total_employees = (await db.execute(total_employees_query)).scalar()
        active_employees = (await db.execute(active_employees_query)).scalar()
        pending_leave = (await db.execute(pending_leave_query)).scalar()
        dept_breakdown = (await db.execute(dept_breakdown_query)).all()
        recent_hires = (await db.execute(recent_hires_query)).scalars().all()
        
        return {
            "total_employees": total_employees or 0,
            "active_employees": active_employees or 0,
            "inactive_employees": (total_employees or 0) - (active_employees or 0),
            "pending_leave_requests": pending_leave or 0,
            "department_breakdown": [
                {"department": row.name, "count": row.employee_count}
                for row in dept_breakdown
            ],
            "recent_hires": [
                {
                    "name": emp.full_name,
                    "position": emp.job_title,
                    "hire_date": emp.hire_date.isoformat(),
                    "department": emp.department.name if emp.department else None
                }
                for emp in recent_hires
            ],
            "average_tenure_months": await self._calculate_average_tenure(db, tenant_id)
        }
    
    async def _calculate_average_tenure(
        self, 
        db: AsyncSession, 
        tenant_id: UUID
    ) -> float:
        """Calculate Average Tenure."""
        """Calculate average employee tenure in months"""
        query = select(Employee.hire_date).where(
            and_(Employee.tenant_id == tenant_id, Employee.is_active == True)
        )
        result = await db.execute(query)
        hire_dates = result.scalars().all()
        
        if not hire_dates:
            return 0.0
        
        today = date.today()
        total_months = sum(
            (today.year - hire_date.year) * 12 + (today.month - hire_date.month)
            for hire_date in hire_dates
        )
        
        return round(total_months / len(hire_dates), 1)
    
    # Policy Management
    async def create_policy(
        self,
        db: AsyncSession,
        policy_data: PolicyCreate,
        tenant_id: UUID = None
    ) -> Policy:
        """Create Policy."""
        """Create a new policy"""
        tenant_id = tenant_id or self.mock_tenant_id
        
        policy = Policy(
            tenant_id=tenant_id,
            **policy_data.dict()
        )
        
        db.add(policy)
        await db.commit()
        await db.refresh(policy)
        return policy
    
    async def get_policies(
        self,
        db: AsyncSession,
        tenant_id: UUID = None,
        category: str = None,
        status: str = None
    ) -> List[Policy]:
        """Get Policies."""
        """Get policies with filters"""
        tenant_id = tenant_id or self.mock_tenant_id
        
        query = select(Policy).where(Policy.tenant_id == tenant_id)
        
        if category:
            query = query.where(Policy.category == category)
        
        if status:
            query = query.where(Policy.status == status)
        
        query = query.order_by(desc(Policy.created_at))
        result = await db.execute(query)
        return result.scalars().all()

# Create service instance
hrm_service = HRMService()