from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.api import deps
from app.models.user import User
import io
import json

router = APIRouter()

# Mock data
MOCK_REPORTS = [
    {"id": "trial-balance", "name": "Trial Balance", "type": "Financial", "module": "general-ledger", "description": "Trial balance report", "created_at": "2024-01-01T00:00:00Z", "updated_at": "2024-01-01T00:00:00Z", "created_by": "System", "is_scheduled": False},
    {"id": "ap-aging", "name": "AP Aging Report", "type": "Aging", "module": "accounts-payable", "description": "Accounts payable aging", "created_at": "2024-01-01T00:00:00Z", "updated_at": "2024-01-01T00:00:00Z", "created_by": "System", "is_scheduled": True},
    {"id": "ar-aging", "name": "AR Aging Report", "type": "Aging", "module": "accounts-receivable", "description": "Accounts receivable aging", "created_at": "2024-01-01T00:00:00Z", "updated_at": "2024-01-01T00:00:00Z", "created_by": "System", "is_scheduled": True},
    {"id": "cash-flow", "name": "Cash Flow Statement", "type": "Financial", "module": "cash-management", "description": "Cash flow statement", "created_at": "2024-01-01T00:00:00Z", "updated_at": "2024-01-01T00:00:00Z", "created_by": "System", "is_scheduled": False},
    {"id": "inventory-valuation", "name": "Inventory Valuation", "type": "Valuation", "module": "inventory", "description": "Inventory valuation report", "created_at": "2024-01-01T00:00:00Z", "updated_at": "2024-01-01T00:00:00Z", "created_by": "System", "is_scheduled": False}
]

MOCK_MODULES = [
    {"id": "general-ledger", "name": "General Ledger", "icon": "pi pi-book", "color": "#2196F3", "report_count": 6},
    {"id": "accounts-payable", "name": "Accounts Payable", "icon": "pi pi-shopping-cart", "color": "#4CAF50", "report_count": 5},
    {"id": "accounts-receivable", "name": "Accounts Receivable", "icon": "pi pi-credit-card", "color": "#FF9800", "report_count": 5},
    {"id": "cash-management", "name": "Cash Management", "icon": "pi pi-wallet", "color": "#9C27B0", "report_count": 4},
    {"id": "inventory", "name": "Inventory", "icon": "pi pi-box", "color": "#607D8B", "report_count": 4},
    {"id": "payroll", "name": "Payroll", "icon": "pi pi-users", "color": "#795548", "report_count": 4},
    {"id": "budget", "name": "Budget Management", "icon": "pi pi-calculator", "color": "#E91E63", "report_count": 3},
    {"id": "tax", "name": "Tax Management", "icon": "pi pi-percentage", "color": "#FF5722", "report_count": 3}
]

MOCK_ACTIVITY = [
    {"id": "1", "timestamp": "2024-01-15T10:30:00Z", "user": "John Doe", "action": "generated", "report_name": "Trial Balance", "module": "General Ledger", "status": "completed", "execution_time": 2.5},
    {"id": "2", "timestamp": "2024-01-15T09:15:00Z", "user": "Jane Smith", "action": "scheduled", "report_name": "AP Aging Report", "module": "Accounts Payable", "status": "active"},
    {"id": "3", "timestamp": "2024-01-15T08:45:00Z", "user": "Mike Johnson", "action": "exported", "report_name": "Cash Flow Statement", "module": "Cash Management", "status": "completed", "execution_time": 5.2},
    {"id": "4", "timestamp": "2024-01-14T16:20:00Z", "user": "Sarah Wilson", "action": "generated", "report_name": "Inventory Valuation", "module": "Inventory", "status": "completed", "execution_time": 3.8}
]

MOCK_SCHEDULES = [
    {"id": "1", "report_id": "ap-aging", "frequency": "weekly", "time": "09:00", "day_of_week": 1, "is_active": True, "next_run": "2024-01-22T09:00:00Z", "last_run": "2024-01-15T09:00:00Z"},
    {"id": "2", "report_id": "ar-aging", "frequency": "weekly", "time": "09:00", "day_of_week": 1, "is_active": True, "next_run": "2024-01-22T09:00:00Z", "last_run": "2024-01-15T09:00:00Z"}
]

@router.get("/stats")
async def get_report_stats(current_user: User = Depends(deps.get_current_active_user)):
    """Get report statistics for dashboard"""
    total_reports = len(MOCK_REPORTS)
    scheduled_reports = len([r for r in MOCK_REPORTS if r["is_scheduled"]])
    
    return {
        "total_reports": total_reports,
        "scheduled_reports": scheduled_reports,
        "reports_this_month": 47,
        "active_users": 12,
        "executions_today": 8,
        "failed_executions": 1
    }

@router.get("/modules")
async def get_report_modules(current_user: User = Depends(deps.get_current_active_user)):
    """Get report modules with their reports"""
    modules_with_reports = []
    
    for module in MOCK_MODULES:
        module_reports = [r for r in MOCK_REPORTS if r["module"] == module["id"]]
        modules_with_reports.append({
            **module,
            "reports": module_reports
        })
    
    return modules_with_reports

@router.get("/activity")
async def get_recent_activity(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Get recent report activity"""
    return MOCK_ACTIVITY[:limit]

@router.get("")
async def get_reports(
    module: Optional[str] = None,
    type: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Get reports with filtering and pagination"""
    reports = MOCK_REPORTS.copy()
    
    if module:
        reports = [r for r in reports if r["module"] == module]
    
    if type:
        reports = [r for r in reports if r["type"] == type]
    
    total = len(reports)
    start = (page - 1) * limit
    end = start + limit
    
    return {
        "reports": reports[start:end],
        "total": total,
        "page": page,
        "limit": limit
    }

@router.get("/{report_id}")
async def get_report(
    report_id: str,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Get specific report"""
    report = next((r for r in MOCK_REPORTS if r["id"] == report_id), None)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

@router.post("")
async def create_report(
    report_data: dict,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Create new report"""
    new_report = {
        "id": f"custom-{len(MOCK_REPORTS) + 1}",
        **report_data,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "created_by": current_user.full_name,
        "is_scheduled": False
    }
    MOCK_REPORTS.append(new_report)
    return new_report

@router.post("/{report_id}/execute")
async def execute_report(
    report_id: str,
    execution_data: dict,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Execute a report"""
    report = next((r for r in MOCK_REPORTS if r["id"] == report_id), None)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    execution = {
        "id": f"exec-{datetime.now().timestamp()}",
        "report_id": report_id,
        "status": "completed",
        "started_at": datetime.now().isoformat(),
        "completed_at": (datetime.now() + timedelta(seconds=3)).isoformat(),
        "file_url": f"/reports/files/{report_id}-{datetime.now().timestamp()}.pdf",
        "file_size": 1024000,
        "executed_by": current_user.full_name
    }
    
    # Add to activity
    MOCK_ACTIVITY.insert(0, {
        "id": str(len(MOCK_ACTIVITY) + 1),
        "timestamp": datetime.now().isoformat(),
        "user": current_user.full_name,
        "action": "generated",
        "report_name": report["name"],
        "module": report["module"].replace("-", " ").title(),
        "status": "completed",
        "execution_time": 3.0
    })
    
    return execution

@router.get("/schedules")
async def get_scheduled_reports(current_user: User = Depends(deps.get_current_active_user)):
    """Get scheduled reports"""
    schedules_with_reports = []
    
    for schedule in MOCK_SCHEDULES:
        report = next((r for r in MOCK_REPORTS if r["id"] == schedule["report_id"]), None)
        if report:
            schedules_with_reports.append({
                **schedule,
                "report_name": report["name"],
                "module": report["module"].replace("-", " ").title()
            })
    
    return schedules_with_reports

@router.post("/schedules")
async def create_schedule(
    schedule_data: dict,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Create report schedule"""
    new_schedule = {
        "id": str(len(MOCK_SCHEDULES) + 1),
        **schedule_data,
        "is_active": True,
        "next_run": (datetime.now() + timedelta(days=1)).isoformat(),
        "last_run": None
    }
    MOCK_SCHEDULES.append(new_schedule)
    return new_schedule

@router.post("/schedules/{schedule_id}/pause")
async def pause_schedule(
    schedule_id: str,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Pause report schedule"""
    schedule = next((s for s in MOCK_SCHEDULES if s["id"] == schedule_id), None)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    schedule["is_active"] = False
    return schedule

@router.post("/schedules/{schedule_id}/resume")
async def resume_schedule(
    schedule_id: str,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Resume report schedule"""
    schedule = next((s for s in MOCK_SCHEDULES if s["id"] == schedule_id), None)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    schedule["is_active"] = True
    return schedule

# Financial Reports
@router.post("/financial/balance-sheet")
async def generate_balance_sheet(
    params: dict,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Generate balance sheet"""
    return {
        "id": f"bs-{datetime.now().timestamp()}",
        "type": "balance_sheet",
        "period_start": params.get("as_of_date"),
        "period_end": params.get("as_of_date"),
        "data": {
            "assets": {
                "current_assets": {"cash": 100000, "accounts_receivable": 50000, "inventory": 75000},
                "fixed_assets": {"equipment": 200000, "accumulated_depreciation": -50000}
            },
            "liabilities": {
                "current_liabilities": {"accounts_payable": 30000, "accrued_expenses": 10000},
                "long_term_liabilities": {"loans": 100000}
            },
            "equity": {"retained_earnings": 200000, "capital": 75000}
        },
        "generated_at": datetime.now().isoformat()
    }

@router.post("/financial/income-statement")
async def generate_income_statement(
    params: dict,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Generate income statement"""
    return {
        "id": f"is-{datetime.now().timestamp()}",
        "type": "income_statement",
        "period_start": params.get("period_start"),
        "period_end": params.get("period_end"),
        "data": {
            "revenue": {"sales": 500000, "other_income": 10000},
            "expenses": {"cost_of_goods_sold": 300000, "operating_expenses": 150000, "depreciation": 20000},
            "net_income": 40000
        },
        "generated_at": datetime.now().isoformat()
    }

@router.post("/aging/ap")
async def generate_ap_aging(
    params: dict,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Generate AP aging report"""
    return {
        "as_of_date": params.get("as_of_date"),
        "aging_periods": [30, 60, 90, 120],
        "vendors": [
            {"vendor_name": "Vendor A", "current": 5000, "30_days": 2000, "60_days": 1000, "90_days": 500, "over_90": 0, "total": 8500},
            {"vendor_name": "Vendor B", "current": 3000, "30_days": 1500, "60_days": 0, "90_days": 0, "over_90": 0, "total": 4500}
        ],
        "totals": {"current": 8000, "30_days": 3500, "60_days": 1000, "90_days": 500, "over_90": 0, "total": 13000}
    }

@router.post("/aging/ar")
async def generate_ar_aging(
    params: dict,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Generate AR aging report"""
    return {
        "as_of_date": params.get("as_of_date"),
        "aging_periods": [30, 60, 90, 120],
        "customers": [
            {"customer_name": "Customer A", "current": 10000, "30_days": 5000, "60_days": 2000, "90_days": 1000, "over_90": 0, "total": 18000},
            {"customer_name": "Customer B", "current": 7000, "30_days": 3000, "60_days": 0, "90_days": 0, "over_90": 0, "total": 10000}
        ],
        "totals": {"current": 17000, "30_days": 8000, "60_days": 2000, "90_days": 1000, "over_90": 0, "total": 28000}
    }

@router.get("/templates")
async def get_report_templates(current_user: User = Depends(deps.get_current_active_user)):
    """Get report templates"""
    return [
        {"id": "financial-summary", "name": "Financial Summary Template", "category": "Financial", "description": "Standard financial summary template"},
        {"id": "custom-aging", "name": "Custom Aging Template", "category": "Aging", "description": "Customizable aging report template"},
        {"id": "operational-kpi", "name": "Operational KPI Template", "category": "Operational", "description": "Key performance indicators template"}
    ]