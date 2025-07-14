from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.api import deps
from app.services.budget import BudgetService
from app.services.budget_integration import BudgetIntegrationService
from app.models import Budget, BudgetLine, BudgetAllocation
from app.schemas import (
    BudgetCreate,
    BudgetUpdate,
    Budget,
    BudgetLine,
    BudgetAllocation,
    BudgetStatus,
    BudgetType
)

router = APIRouter()

@router.post("/", response_model=Budget)
def create_budget(
    budget_in: BudgetCreate,
    db: Session = Depends(deps.get_db),
    budget_service: BudgetService = Depends(deps.get_budget_service),
    budget_integration_service: BudgetIntegrationService = Depends(deps.get_budget_integration_service)
):
    """
    Create a new budget.
    """
    if budget_in.status == BudgetStatus.APPROVED:
        # Check budget availability
        if not budget_integration_service.check_budget_availability(
            account_id=budget_in.lines[0].account_id,
            amount=sum(line.amount for line in budget_in.lines),
            department_id=budget_in.department_id,
            project_id=budget_in.project_id,
            date=budget_in.start_date
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient budget availability"
            )

    budget = budget_service.create_budget(budget_in)
    return budget

@router.get("/{budget_id}", response_model=Budget)
def get_budget(
    budget_id: int,
    db: Session = Depends(deps.get_db),
    budget_service: BudgetService = Depends(deps.get_budget_service)
):
    """
    Get a specific budget by ID.
    """
    budget = budget_service.get_budget(budget_id)
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )
    return budget

@router.put("/{budget_id}", response_model=Budget)
def update_budget(
    budget_id: int,
    budget_in: BudgetUpdate,
    db: Session = Depends(deps.get_db),
    budget_service: BudgetService = Depends(deps.get_budget_service),
    budget_integration_service: BudgetIntegrationService = Depends(deps.get_budget_integration_service)
):
    """
    Update a budget.
    """
    budget = budget_service.get_budget(budget_id)
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )

    if budget_in.status == BudgetStatus.APPROVED:
        # Check budget availability
        if not budget_integration_service.check_budget_availability(
            account_id=budget_in.lines[0].account_id,
            amount=sum(line.amount for line in budget_in.lines),
            department_id=budget_in.department_id,
            project_id=budget_in.project_id,
            date=budget_in.start_date
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient budget availability"
            )

    budget = budget_service.update_budget(budget_id, budget_in)
    return budget

@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(
    budget_id: int,
    db: Session = Depends(deps.get_db),
    budget_service: BudgetService = Depends(deps.get_budget_service)
):
    """
    Delete a budget.
    """
    budget = budget_service.get_budget(budget_id)
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )

    budget_service.delete_budget(budget_id)

@router.post("/{budget_id}/approve")
async def approve_budget(
    budget_id: int,
    db: Session = Depends(deps.get_db),
    budget_service: BudgetService = Depends(deps.get_budget_service),
    budget_integration_service: BudgetIntegrationService = Depends(deps.get_budget_integration_service)
):
    """
    Approve a budget.
    """
    budget = budget_service.get_budget(budget_id)
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )

    # Check budget availability
    if not budget_integration_service.check_budget_availability(
        account_id=budget.lines[0].account_id,
        amount=sum(line.amount for line in budget.lines),
        department_id=budget.department_id,
        project_id=budget.project_id,
        date=budget.start_date
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient budget availability"
        )

    budget = budget_service.approve_budget(budget_id)
    return budget

@router.post("/{budget_id}/reject")
def reject_budget(
    budget_id: int,
    reason: str,
    db: Session = Depends(deps.get_db),
    budget_service: BudgetService = Depends(deps.get_budget_service)
):
    """
    Reject a budget.
    """
    budget = budget_service.get_budget(budget_id)
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )

    budget = budget_service.reject_budget(budget_id, reason)
    return budget

@router.get("/stats")
def get_budget_stats(
    db: Session = Depends(deps.get_db),
    budget_integration_service: BudgetIntegrationService = Depends(deps.get_budget_integration_service)
):
    """
    Get budget statistics.
    """
    return budget_integration_service.get_budget_spending_report(
        account_id=None,
        department_id=None,
        project_id=None
    )

@router.post("/check-availability")
def check_budget_availability(
    account_id: int,
    amount: float,
    department_id: Optional[int] = None,
    project_id: Optional[int] = None,
    date: Optional[datetime] = None,
    db: Session = Depends(deps.get_db),
    budget_integration_service: BudgetIntegrationService = Depends(deps.get_budget_integration_service)
):
    """
    Check if budget amount is available.
    """
    return {
        "available": budget_integration_service.check_budget_availability(
            account_id,
            amount,
            department_id,
            project_id,
            date
        )
    }

@router.post("/allocate/{module}")
def allocate_budget(
    module: str,
    module_id: int,
    amount: float,
    account_id: int,
    department_id: Optional[int] = None,
    project_id: Optional[int] = None,
    description: str = "",
    db: Session = Depends(deps.get_db),
    budget_integration_service: BudgetIntegrationService = Depends(deps.get_budget_integration_service)
):
    """
    Allocate budget for a specific module.
    """
    allocation = budget_integration_service.allocate_budget(
        module_id=module_id,
        amount=amount,
        account_id=account_id,
        department_id=department_id,
        project_id=project_id,
        description=description
    )
    return allocation

@router.post("/export/pdf")
def export_budget_pdf(
    budget_ids: List[int],
    db: Session = Depends(deps.get_db),
    budget_service: BudgetService = Depends(deps.get_budget_service)
):
    """
    Export budgets to PDF.
    """
    budgets = budget_service.get_budgets_by_ids(budget_ids)
    # Generate PDF logic here
    return {
        "message": "PDF export initiated"
    }

@router.post("/export/excel")
def export_budget_excel(
    budget_ids: List[int],
    db: Session = Depends(deps.get_db),
    budget_service: BudgetService = Depends(deps.get_budget_service)
):
    """
    Export budgets to Excel.
    """
    budgets = budget_service.get_budgets_by_ids(budget_ids)
    # Generate Excel logic here
    return {
        "message": "Excel export initiated"
    }

@router.get("/analytics/performance")
def get_budget_performance(
    department_id: Optional[int] = None,
    project_id: Optional[int] = None,
    db: Session = Depends(deps.get_db),
    budget_integration_service: BudgetIntegrationService = Depends(deps.get_budget_integration_service)
):
    """
    Get budget performance metrics.
    """
    return budget_integration_service.get_budget_performance(
        department_id=department_id,
        project_id=project_id
    )

@router.get("/analytics/department")
def get_departmental_analysis(
    db: Session = Depends(deps.get_db),
    budget_integration_service: BudgetIntegrationService = Depends(deps.get_budget_integration_service)
):
    """
    Get budget analysis by department.
    """
    return budget_integration_service.get_departmental_analysis()

@router.get("/analytics/project")
def get_project_analysis(
    db: Session = Depends(deps.get_db),
    budget_integration_service: BudgetIntegrationService = Depends(deps.get_budget_integration_service)
):
    """
    Get budget analysis by project.
    """
    return budget_integration_service.get_project_analysis()

@router.get("/analytics/trend")
def get_trend_analysis(
    period: str = 'month',
    months: int = 12,
    db: Session = Depends(deps.get_db),
    budget_integration_service: BudgetIntegrationService = Depends(deps.get_budget_integration_service)
):
    """
    Get budget trend analysis.
    """
    return budget_integration_service.get_budget_trend_analysis(
        period=period,
        months=months
    )

@router.get("/analytics/allocation/{account_id}")
def get_allocation_analysis(
    account_id: int,
    db: Session = Depends(deps.get_db),
    budget_integration_service: BudgetIntegrationService = Depends(deps.get_budget_integration_service)
):
    """
    Get budget allocation analysis for a specific account.
    """
    return budget_integration_service.get_budget_allocation_analysis(
        account_id=account_id
    )

@router.get("/analytics/variance")
def get_variance_analysis(
    db: Session = Depends(deps.get_db),
    budget_integration_service: BudgetIntegrationService = Depends(deps.get_budget_integration_service)
):
    """
    Get budget variance analysis.
    """
    return budget_integration_service.get_budget_variance_analysis()
