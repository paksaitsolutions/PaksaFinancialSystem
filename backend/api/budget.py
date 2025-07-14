from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from ..core.security import get_current_user
from ..database import get_db
from ..services.budget import BudgetService
from ..schemas.budget import (
    BudgetCreate,
    BudgetUpdate,
    BudgetApprovalCreate,
    BudgetResponse,
    BudgetListResponse
)

router = APIRouter(prefix="/budget", tags=["budget"])

@router.post("/", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
async def create_budget(
    budget_data: BudgetCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """
    Create a new budget with lines, allocations, and rules.
    """
    service = BudgetService(db)
    return service.create_budget(budget_data, current_user)

@router.get("/{budget_id}", response_model=BudgetResponse)
async def get_budget(
    budget_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a budget by ID.
    """
    service = BudgetService(db)
    return service.get_budget(budget_id)

@router.get("/", response_model=BudgetListResponse)
async def list_budgets(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all budgets with pagination.
    """
    service = BudgetService(db)
    return service.list_budgets(skip, limit)

@router.put("/{budget_id}", response_model=BudgetResponse)
async def update_budget(
    budget_id: int,
    budget_data: BudgetUpdate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """
    Update a budget's details, lines, allocations, and rules.
    """
    service = BudgetService(db)
    return service.update_budget(budget_id, budget_data, current_user)

@router.post("/{budget_id}/approve", response_model=BudgetResponse)
async def approve_budget(
    budget_id: int,
    approval_data: BudgetApprovalCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """
    Approve a budget.
    """
    service = BudgetService(db)
    return service.approve_budget(budget_id, approval_data, current_user)

@router.post("/{budget_id}/reject", response_model=BudgetResponse)
async def reject_budget(
    budget_id: int,
    notes: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """
    Reject a budget.
    """
    service = BudgetService(db)
    return service.reject_budget(budget_id, current_user, notes)

@router.post("/{budget_id}/archive", response_model=BudgetResponse)
async def archive_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """
    Archive a budget.
    """
    service = BudgetService(db)
    return service.archive_budget(budget_id, current_user)

@router.get("/report/summary")
async def get_budget_summary(
    db: Session = Depends(get_db)
):
    """
    Get budget summary report.
    """
    service = BudgetService(db)
    # TODO: Implement budget summary report logic
    pass

@router.get("/report/variance")
async def get_budget_variance(
    db: Session = Depends(get_db)
):
    """
    Get budget vs actual variance report.
    """
    service = BudgetService(db)
    # TODO: Implement variance report logic
    pass

@router.get("/report/department")
async def get_department_budget_report(
    department_id: int,
    db: Session = Depends(get_db)
):
    """
    Get budget report for a specific department.
    """
    service = BudgetService(db)
    # TODO: Implement department report logic
    pass

@router.get("/report/project")
async def get_project_budget_report(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    Get budget report for a specific project.
    """
    service = BudgetService(db)
    # TODO: Implement project report logic
    pass
