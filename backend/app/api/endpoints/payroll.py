from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.api import deps
from app.models.user import User
import io
import csv

router = APIRouter()

# Mock data
MOCK_EMPLOYEES = [
    {
        "id": 1, "employee_number": "EMP001", "first_name": "John", "last_name": "Doe", "full_name": "John Doe",
        "email": "john.doe@company.com", "phone": "+1-555-0101", "department": "Engineering", "position": "Senior Developer",
        "hire_date": "2022-01-15", "employment_type": "full_time", "status": "active", "salary_type": "salary",
        "base_salary": 85000.00, "pay_frequency": "bi_weekly", "tax_id": "123-45-6789",
        "created_at": "2022-01-15T10:00:00Z", "updated_at": "2024-01-15T10:00:00Z"
    },
    {
        "id": 2, "employee_number": "EMP002", "first_name": "Jane", "last_name": "Smith", "full_name": "Jane Smith",
        "email": "jane.smith@company.com", "phone": "+1-555-0102", "department": "Marketing", "position": "Marketing Manager",
        "hire_date": "2021-06-10", "employment_type": "full_time", "status": "active", "salary_type": "salary",
        "base_salary": 75000.00, "pay_frequency": "bi_weekly", "tax_id": "987-65-4321",
        "created_at": "2021-06-10T10:00:00Z", "updated_at": "2024-01-15T10:00:00Z"
    },
    {
        "id": 3, "employee_number": "EMP003", "first_name": "Mike", "last_name": "Johnson", "full_name": "Mike Johnson",
        "email": "mike.johnson@company.com", "department": "Operations", "position": "Operations Specialist",
        "hire_date": "2023-03-20", "employment_type": "part_time", "status": "active", "salary_type": "hourly",
        "hourly_rate": 25.00, "pay_frequency": "weekly", "tax_id": "456-78-9012",
        "created_at": "2023-03-20T10:00:00Z", "updated_at": "2024-01-15T10:00:00Z"
    }
]

MOCK_PAY_RUNS = [
    {
        "id": 1, "pay_period_start": "2024-01-01", "pay_period_end": "2024-01-15", "pay_date": "2024-01-20",
        "status": "paid", "total_gross_pay": 12500.00, "total_deductions": 2500.00, "total_net_pay": 10000.00,
        "employee_count": 2, "created_by": "Admin User", "created_at": "2024-01-16T10:00:00Z",
        "approved_at": "2024-01-18T14:00:00Z", "paid_at": "2024-01-20T09:00:00Z"
    },
    {
        "id": 2, "pay_period_start": "2024-01-16", "pay_period_end": "2024-01-31", "pay_date": "2024-02-05",
        "status": "approved", "total_gross_pay": 13200.00, "total_deductions": 2640.00, "total_net_pay": 10560.00,
        "employee_count": 3, "created_by": "Admin User", "created_at": "2024-02-01T10:00:00Z",
        "approved_at": "2024-02-03T14:00:00Z"
    }
]

MOCK_PAYSLIPS = [
    {
        "id": 1, "pay_run_id": 1, "employee_id": 1, "employee_name": "John Doe",
        "pay_period_start": "2024-01-01", "pay_period_end": "2024-01-15", "pay_date": "2024-01-20",
        "gross_pay": 6538.46, "total_deductions": 1307.69, "net_pay": 5230.77, "hours_worked": 80,
        "status": "paid",
        "earnings": [
            {"id": 1, "type": "base_salary", "description": "Base Salary", "amount": 6538.46, "hours": 80, "rate": 81.73}
        ],
        "deductions": [
            {"id": 1, "type": "health_insurance", "description": "Health Insurance", "amount": 200.00, "is_pre_tax": True},
            {"id": 2, "type": "retirement", "description": "401(k)", "amount": 327.00, "is_pre_tax": True}
        ],
        "taxes": [
            {"id": 1, "tax_type": "federal_income", "description": "Federal Income Tax", "taxable_amount": 6011.46, "tax_rate": 0.12, "tax_amount": 721.38},
            {"id": 2, "tax_type": "social_security", "description": "Social Security", "taxable_amount": 6538.46, "tax_rate": 0.062, "tax_amount": 405.38}
        ]
    }
]

MOCK_DEDUCTIONS_BENEFITS = [
    {"id": 1, "name": "Health Insurance", "type": "deduction", "category": "health", "calculation_type": "fixed", "amount": 200.00, "is_pre_tax": True, "is_mandatory": False, "is_active": True},
    {"id": 2, "name": "401(k)", "type": "deduction", "category": "retirement", "calculation_type": "percentage", "percentage": 5.0, "is_pre_tax": True, "is_mandatory": False, "employer_contribution": 3.0, "is_active": True},
    {"id": 3, "name": "Dental Insurance", "type": "deduction", "category": "health", "calculation_type": "fixed", "amount": 50.00, "is_pre_tax": True, "is_mandatory": False, "is_active": True}
]

@router.get("/dashboard/kpis")
async def get_payroll_kpis(current_user: User = Depends(deps.get_current_active_user)):
    """Get payroll dashboard KPIs"""
    total_payroll = sum(pr["total_gross_pay"] for pr in MOCK_PAY_RUNS)
    total_employees = len([e for e in MOCK_EMPLOYEES if e["status"] == "active"])
    average_salary = sum(e["base_salary"] for e in MOCK_EMPLOYEES if e.get("base_salary")) / len([e for e in MOCK_EMPLOYEES if e.get("base_salary")])
    
    return {
        "total_payroll": total_payroll,
        "payroll_change": 5.2,
        "total_employees": total_employees,
        "employee_change": 2.3,
        "average_salary": average_salary,
        "salary_change": -1.5,
        "upcoming_payroll": 98200.00
    }

@router.get("/dashboard/summary")
async def get_payroll_summary(
    months: int = Query(6, ge=1, le=12),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Get payroll summary for dashboard chart"""
    monthly_data = []
    base_budget = 120000
    base_actual = 115000
    
    for i in range(months):
        month_date = datetime.now() - timedelta(days=30 * (months - i - 1))
        monthly_data.append({
            "month": month_date.strftime("%b"),
            "budget": base_budget + (i * 5000),
            "actual": base_actual + (i * 7000)
        })
    
    return {
        "monthly_data": monthly_data,
        "total_budget": sum(d["budget"] for d in monthly_data),
        "total_actual": sum(d["actual"] for d in monthly_data)
    }

@router.get("/dashboard/activity")
async def get_recent_activity(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Get recent payroll activity"""
    activities = [
        {"id": 1, "type": "payroll_processed", "title": "Payroll Processed", "details": "Bi-weekly payroll for 85 employees", "timestamp": "2024-01-20T10:00:00Z", "user": "Admin User"},
        {"id": 2, "type": "employee_added", "title": "New Employee Added", "details": "John Doe - Senior Developer", "timestamp": "2024-01-19T14:30:00Z", "user": "HR Manager"},
        {"id": 3, "type": "tax_filing", "title": "Tax Filing", "details": "Q4 2023 Tax Report submitted", "timestamp": "2024-01-18T09:15:00Z", "user": "Payroll Admin"},
        {"id": 4, "type": "bonus_processed", "title": "Bonus Processed", "details": "Q4 Performance Bonuses", "timestamp": "2024-01-15T16:45:00Z", "user": "Admin User"}
    ]
    return activities[:limit]

@router.get("/employees")
async def get_employees(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    department: Optional[str] = None,
    status: Optional[str] = None,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Get employees with filtering and pagination"""
    employees = MOCK_EMPLOYEES.copy()
    
    if search:
        employees = [e for e in employees if search.lower() in e["full_name"].lower() or search.lower() in e["employee_number"].lower()]
    
    if department:
        employees = [e for e in employees if e["department"] == department]
    
    if status:
        employees = [e for e in employees if e["status"] == status]
    
    total = len(employees)
    start = (page - 1) * limit
    end = start + limit
    
    return {
        "employees": employees[start:end],
        "total": total,
        "page": page,
        "limit": limit
    }

@router.get("/employees/{employee_id}")
async def get_employee(
    employee_id: int,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Get specific employee"""
    employee = next((e for e in MOCK_EMPLOYEES if e["id"] == employee_id), None)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

@router.post("/employees")
async def create_employee(
    employee_data: dict,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Create new employee"""
    new_employee = {
        "id": max(e["id"] for e in MOCK_EMPLOYEES) + 1,
        **employee_data,
        "full_name": f"{employee_data['first_name']} {employee_data['last_name']}",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    MOCK_EMPLOYEES.append(new_employee)
    return new_employee

@router.put("/employees/{employee_id}")
async def update_employee(
    employee_id: int,
    employee_data: dict,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Update employee"""
    employee_index = next((i for i, e in enumerate(MOCK_EMPLOYEES) if e["id"] == employee_id), None)
    if employee_index is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    MOCK_EMPLOYEES[employee_index].update(employee_data)
    if "first_name" in employee_data or "last_name" in employee_data:
        MOCK_EMPLOYEES[employee_index]["full_name"] = f"{MOCK_EMPLOYEES[employee_index]['first_name']} {MOCK_EMPLOYEES[employee_index]['last_name']}"
    MOCK_EMPLOYEES[employee_index]["updated_at"] = datetime.now().isoformat()
    
    return MOCK_EMPLOYEES[employee_index]

@router.delete("/employees/{employee_id}")
async def delete_employee(
    employee_id: int,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Delete employee"""
    employee_index = next((i for i, e in enumerate(MOCK_EMPLOYEES) if e["id"] == employee_id), None)
    if employee_index is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    MOCK_EMPLOYEES.pop(employee_index)
    return {"message": "Employee deleted successfully"}

@router.get("/pay-runs")
async def get_pay_runs(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = None,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Get pay runs"""
    pay_runs = MOCK_PAY_RUNS.copy()
    
    if status:
        pay_runs = [pr for pr in pay_runs if pr["status"] == status]
    
    total = len(pay_runs)
    start = (page - 1) * limit
    end = start + limit
    
    return {
        "pay_runs": pay_runs[start:end],
        "total": total,
        "page": page,
        "limit": limit
    }

@router.post("/pay-runs")
async def create_pay_run(
    pay_run_data: dict,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Create new pay run"""
    new_pay_run = {
        "id": max(pr["id"] for pr in MOCK_PAY_RUNS) + 1,
        **pay_run_data,
        "status": "draft",
        "total_gross_pay": 0.00,
        "total_deductions": 0.00,
        "total_net_pay": 0.00,
        "employee_count": 0,
        "created_by": current_user.full_name,
        "created_at": datetime.now().isoformat()
    }
    MOCK_PAY_RUNS.append(new_pay_run)
    return new_pay_run

@router.post("/pay-runs/{pay_run_id}/process")
async def process_pay_run(
    pay_run_id: int,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Process pay run"""
    pay_run_index = next((i for i, pr in enumerate(MOCK_PAY_RUNS) if pr["id"] == pay_run_id), None)
    if pay_run_index is None:
        raise HTTPException(status_code=404, detail="Pay run not found")
    
    MOCK_PAY_RUNS[pay_run_index]["status"] = "processing"
    # Simulate processing calculations
    MOCK_PAY_RUNS[pay_run_index]["total_gross_pay"] = 15000.00
    MOCK_PAY_RUNS[pay_run_index]["total_deductions"] = 3000.00
    MOCK_PAY_RUNS[pay_run_index]["total_net_pay"] = 12000.00
    MOCK_PAY_RUNS[pay_run_index]["employee_count"] = len(MOCK_EMPLOYEES)
    
    return MOCK_PAY_RUNS[pay_run_index]

@router.get("/payslips")
async def get_payslips(
    pay_run_id: Optional[int] = None,
    employee_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Get payslips"""
    payslips = MOCK_PAYSLIPS.copy()
    
    if pay_run_id:
        payslips = [ps for ps in payslips if ps["pay_run_id"] == pay_run_id]
    
    if employee_id:
        payslips = [ps for ps in payslips if ps["employee_id"] == employee_id]
    
    total = len(payslips)
    start = (page - 1) * limit
    end = start + limit
    
    return {
        "payslips": payslips[start:end],
        "total": total,
        "page": page,
        "limit": limit
    }

@router.get("/deductions-benefits")
async def get_deductions_benefits(current_user: User = Depends(deps.get_current_active_user)):
    """Get deductions and benefits"""
    return MOCK_DEDUCTIONS_BENEFITS

@router.post("/deductions-benefits")
async def create_deduction_benefit(
    item_data: dict,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Create deduction/benefit"""
    new_item = {
        "id": max(db["id"] for db in MOCK_DEDUCTIONS_BENEFITS) + 1,
        **item_data,
        "is_active": True
    }
    MOCK_DEDUCTIONS_BENEFITS.append(new_item)
    return new_item

@router.get("/analytics")
async def get_payroll_analytics(
    start_date: str = Query(...),
    end_date: str = Query(...),
    group_by: str = Query("month", regex="^(month|department|employee)$"),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Get payroll analytics"""
    total_payroll = sum(pr["total_gross_pay"] for pr in MOCK_PAY_RUNS)
    average_salary = total_payroll / len(MOCK_EMPLOYEES) if MOCK_EMPLOYEES else 0
    
    return {
        "total_payroll": total_payroll,
        "average_salary": average_salary,
        "by_period": [
            {"period": "2024-01", "amount": 12500.00},
            {"period": "2024-02", "amount": 13200.00}
        ],
        "by_department": [
            {"department": "Engineering", "amount": 85000.00, "employee_count": 1},
            {"department": "Marketing", "amount": 75000.00, "employee_count": 1},
            {"department": "Operations", "amount": 25000.00, "employee_count": 1}
        ],
        "top_earners": [
            {"employee_name": "John Doe", "amount": 85000.00},
            {"employee_name": "Jane Smith", "amount": 75000.00}
        ]
    }

@router.post("/employees/import")
async def import_employees(
    file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Import employees from CSV/Excel file"""
    if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Only CSV and Excel files are supported")
    
    return {"success": 15, "errors": ["Row 8: Invalid email format", "Row 12: Missing required field 'department'"]}

@router.get("/employees/export")
async def export_employees(
    format: str = Query("csv", regex="^(csv|excel)$"),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Export employees to CSV or Excel"""
    if format == "csv":
        output = io.StringIO()
        if MOCK_EMPLOYEES:
            writer = csv.DictWriter(output, fieldnames=MOCK_EMPLOYEES[0].keys())
            writer.writeheader()
            writer.writerows(MOCK_EMPLOYEES)
        
        response = StreamingResponse(
            io.BytesIO(output.getvalue().encode()),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=employees.csv"}
        )
        return response
    
    return {"message": "Excel export would be implemented here"}