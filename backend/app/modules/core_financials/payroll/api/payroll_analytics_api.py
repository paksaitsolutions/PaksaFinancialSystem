"""
Payroll analytics API endpoints for generating insights and trends.
"""
from datetime import date, datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
import statistics
from sqlalchemy import func, and_, or_, case
from pydantic import BaseModel, Field
from enum import Enum

from app.core.db.session import get_db
from app.modules.core_financials.payroll.models.payroll_processing import PayrollRun, PayrollItem
from app.modules.hrms.employees.models.employee import Employee
from app.modules.core_hrms.departments.models.department import Department

# The actual path will be /api/payroll/analytics because the parent router has prefix="/api/payroll"
router = APIRouter(prefix="/analytics", tags=["payroll-analytics"])

class TrendPeriod(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

class PayrollTrendAnalysis(BaseModel):
    period: str
    total_payroll: float
    employee_count: int
    average_salary: float
    overtime_cost: float
    benefits_cost: float
    tax_withheld: float
    net_pay: float
    trend: str
    change_percentage: float

class AnomalyType(str, Enum):
    OVERTIME = "overtime"
    TAX = "tax"
    BENEFITS = "benefits"
    SALARY = "salary"
    OTHER = "other"

class AnomalySeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class PayrollAnomaly(BaseModel):
    id: str
    type: AnomalyType
    severity: AnomalySeverity
    description: str
    amount: float
    expected_amount: Optional[float] = None
    variance: float
    date: date
    employee_id: Optional[str] = None
    employee_name: Optional[str] = None
    department: Optional[str] = None

class PayrollCostAnalysis(BaseModel):
    department: str
    total_payroll: float
    employee_count: int
    average_salary: float
    benefits_cost: float
    tax_cost: float
    overtime_cost: float
    payroll_percentage: float

@router.get("/trends", response_model=List[PayrollTrendAnalysis])
async def get_payroll_trends(
    period: TrendPeriod = Query(..., description="Time period for trend analysis"),
    limit: int = Query(12, description="Number of periods to return"),
    department_id: Optional[str] = Query(None, description="Filter by department ID"),
    db: Session = Depends(get_db)
):
    """
    Get payroll trend analysis over time.
    """
    end_date = datetime.utcnow().date()
    
    # Calculate start date based on period and limit
    if period == TrendPeriod.DAILY:
        start_date = end_date - timedelta(days=limit)
        date_format = "%Y-%m-%d"
        group_by = func.date(PayrollRun.pay_period_end)
    elif period == TrendPeriod.WEEKLY:
        start_date = end_date - timedelta(weeks=limit)
        date_format = "%Y-W%W"
        group_by = func.strftime("%Y-W%W", PayrollRun.pay_period_end)
    elif period == TrendPeriod.MONTHLY:
        start_date = end_date - timedelta(days=30*limit)
        date_format = "%Y-%m"
        group_by = func.strftime("%Y-%m", PayrollRun.pay_period_end)
    elif period == TrendPeriod.QUARTERLY:
        start_date = end_date - timedelta(days=90*limit)
        date_format = "%Y-Q"
        group_by = func.strftime("%Y-", PayrollRun.pay_period_end) + \
                  ((func.strftime("%m", PayrollRun.pay_period_end).cast(int) - 1) // 3 + 1).cast(str)
    else:  # YEARLY
        start_date = end_date - timedelta(days=365*limit)
        date_format = "%Y"
        group_by = func.strftime("%Y", PayrollRun.pay_period_end)

    # Base query
    query = db.query(
        group_by.label("period"),
        func.sum(PayrollItem.net_pay).label("total_payroll"),
        func.count(func.distinct(PayrollItem.employee_id)).label("employee_count"),
        func.avg(PayrollItem.gross_pay).label("average_salary"),
        func.sum(PayrollItem.overtime_pay).label("overtime_cost"),
        func.sum(PayrollItem.benefits_deductions).label("benefits_cost"),
        func.sum(PayrollItem.tax_withheld).label("tax_withheld"),
        func.sum(PayrollItem.net_pay).label("net_pay")
    ).join(
        PayrollRun, PayrollRun.id == PayrollItem.payroll_run_id
    ).filter(
        PayrollRun.pay_period_end.between(start_date, end_date),
        PayrollRun.status == "processed"
    ).group_by("period").order_by("period")

    # Apply department filter if provided
    if department_id:
        query = query.join(Employee, Employee.id == PayrollItem.employee_id).filter(
            Employee.department_id == department_id
        )

    results = query.all()
    
    # Format results and calculate trend
    trend_data = []
    previous_total = None
    
    for i, row in enumerate(results):
        period = row.period
        total = float(row.total_payroll or 0)
        
        if previous_total is not None and previous_total > 0:
            change = ((total - previous_total) / previous_total) * 100
            trend = "up" if change > 5 else "down" if change < -5 else "stable"
        else:
            change = 0
            trend = "stable"
            
        trend_data.append(PayrollTrendAnalysis(
            period=period,
            total_payroll=total,
            employee_count=row.employee_count or 0,
            average_salary=float(row.average_salary or 0),
            overtime_cost=float(row.overtime_cost or 0),
            benefits_cost=float(row.benefits_cost or 0),
            tax_withheld=float(row.tax_withheld or 0),
            net_pay=float(row.net_pay or 0),
            trend=trend,
            change_percentage=change
        ))
        
        previous_total = total
    
    return trend_data

@router.get("/anomalies", response_model=List[PayrollAnomaly])
async def detect_payroll_anomalies(
    start_date: date = Query(..., description="Start date for anomaly detection"),
    end_date: date = Query(..., description="End date for anomaly detection"),
    min_severity: AnomalySeverity = Query("medium", description="Minimum severity level to include"),
    department_id: Optional[str] = Query(None, description="Filter by department ID"),
    db: Session = Depends(get_db)
):
    """
    Detect anomalies in payroll data.
    """
    # Base query for payroll items in date range
    query = db.query(
        PayrollItem,
        Employee,
        Department
    ).join(
        PayrollRun, PayrollRun.id == PayrollItem.payroll_run_id
    ).join(
        Employee, Employee.id == PayrollItem.employee_id, isouter=True
    ).join(
        Department, Department.id == Employee.department_id, isouter=True
    ).filter(
        PayrollRun.pay_period_end.between(start_date, end_date),
        PayrollRun.status == "processed"
    )

    if department_id:
        query = query.filter(Employee.department_id == department_id)

    payroll_items = query.all()
    
    # In a real implementation, you would use statistical methods to detect anomalies
    # This is a simplified example that flags values beyond 2 standard deviations
    
    anomalies = []
    anomaly_id = 1
    
    # Example: Detect overtime anomalies
    overtime_values = [float(item.PayrollItem.overtime_pay or 0) for item in payroll_items]
    if overtime_values:
        avg_overtime = statistics.mean(overtime_values)
        std_overtime = statistics.stdev(overtime_values) if len(overtime_values) > 1 else 0
        
        for item in payroll_items:
            overtime = float(item.PayrollItem.overtime_pay or 0)
            if overtime > avg_overtime + 2 * std_overtime and overtime > 0:
                severity = "high" if overtime > avg_overtime + 3 * std_overtime else "medium"
                
                if severity >= min_severity:
                    anomalies.append(PayrollAnomaly(
                        id=f"ano-{anomaly_id}",
                        type="overtime",
                        severity=severity,
                        description=f"Unusually high overtime payment: ${overtime:,.2f}",
                        amount=overtime,
                        expected_amount=round(avg_overtime, 2),
                        variance=round((overtime - avg_overtime) / avg_overtime * 100 if avg_overtime > 0 else 100, 1),
                        date=item.PayrollRun.pay_period_end,
                        employee_id=item.PayrollItem.employee_id,
                        employee_name=f"{item.Employee.first_name} {item.Employee.last_name}" if item.Employee else None,
                        department=item.Department.name if item.Department else None
                    ))
                    anomaly_id += 1
    
    # Add more anomaly detection logic here (tax, benefits, salary, etc.)
    
    return anomalies

@router.get("/cost-analysis", response_model=List[PayrollCostAnalysis])
async def get_payroll_cost_analysis(
    period: str = Query("current_month", 
                       description="Time period for analysis: current_month, last_month, ytd, last_year, or custom"),
    group_by: str = Query("department", 
                         description="Group by: department, location, job_title, employee_type"),
    start_date: Optional[date] = Query(None, description="Required if period is 'custom'"),
    end_date: Optional[date] = Query(None, description="Required if period is 'custom'"),
    department_id: Optional[str] = Query(None, description="Filter by department ID"),
    db: Session = Depends(get_db)
):
    """
    Get payroll cost analysis grouped by the specified dimension.
    """
    # Calculate date range based on period
    today = datetime.utcnow().date()
    
    if period == "current_month":
        start = today.replace(day=1)
        end = today
    elif period == "last_month":
        if today.month == 1:
            start = today.replace(year=today.year-1, month=12, day=1)
        else:
            start = today.replace(month=today.month-1, day=1)
        end = (start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    elif period == "ytd":
        start = today.replace(month=1, day=1)
        end = today
    elif period == "last_year":
        start = today.replace(year=today.year-1, month=1, day=1)
        end = today.replace(year=today.year-1, month=12, day=31)
    elif period == "custom" and start_date and end_date:
        start = start_date
        end = end_date
    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid period or missing date range for custom period"
        )

    # Base query
    query = db.query(
        Department.name.label("department"),
        func.sum(PayrollItem.gross_pay).label("total_payroll"),
        func.count(func.distinct(PayrollItem.employee_id)).label("employee_count"),
        func.avg(PayrollItem.gross_pay).label("average_salary"),
        func.sum(PayrollItem.benefits_deductions).label("benefits_cost"),
        func.sum(PayrollItem.tax_withheld).label("tax_cost"),
        func.sum(PayrollItem.overtime_pay).label("overtime_cost")
    ).join(
        PayrollRun, PayrollRun.id == PayrollItem.payroll_run_id
    ).join(
        Employee, Employee.id == PayrollItem.employee_id, isouter=True
    ).join(
        Department, Department.id == Employee.department_id, isouter=True
    ).filter(
        PayrollRun.pay_period_end.between(start, end),
        PayrollRun.status == "processed"
    )

    # Apply department filter if provided
    if department_id:
        query = query.filter(Employee.department_id == department_id)

    # Group by the specified dimension
    if group_by == "department":
        query = query.group_by(Department.name)
    # Add other group_by options here (location, job_title, employee_type)
    else:
        query = query.group_by(Department.name)  # Default to department

    results = query.all()
    
    # Calculate total for percentage calculation
    total_payroll = sum(float(row.total_payroll or 0) for row in results)
    
    # Format results
    cost_analysis = []
    for row in results:
        department_total = float(row.total_payroll or 0)
        cost_analysis.append(PayrollCostAnalysis(
            department=row.department or "Unassigned",
            total_payroll=department_total,
            employee_count=row.employee_count or 0,
            average_salary=float(row.average_salary or 0),
            benefits_cost=float(row.benefits_cost or 0),
            tax_cost=float(row.tax_cost or 0),
            overtime_cost=float(row.overtime_cost or 0),
            payroll_percentage=(department_total / total_payroll * 100) if total_payroll > 0 else 0
        ))
    
    return cost_analysis
