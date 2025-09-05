from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..core.deps import get_db
from ..crud import budget as budget_crud
from ..schemas.budget import Budget, BudgetCreate, BudgetUpdate, BudgetApprovalCreate, BudgetApproval

router = APIRouter()

@router.get("/", response_model=List[Budget])
def read_budgets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all budgets"""
    budgets = budget_crud.get_budgets(db, skip=skip, limit=limit)
    return budgets

@router.post("/", response_model=Budget)
def create_budget(budget: BudgetCreate, db: Session = Depends(get_db)):
    """Create a new budget"""
    return budget_crud.create_budget(db=db, budget=budget)

@router.get("/{budget_id}", response_model=Budget)
def read_budget(budget_id: int, db: Session = Depends(get_db)):
    """Get a specific budget"""
    db_budget = budget_crud.get_budget(db, budget_id=budget_id)
    if db_budget is None:
        raise HTTPException(status_code=404, detail="Budget not found")
    return db_budget

@router.put("/{budget_id}", response_model=Budget)
def update_budget(budget_id: int, budget: BudgetUpdate, db: Session = Depends(get_db)):
    """Update a budget"""
    db_budget = budget_crud.update_budget(db, budget_id=budget_id, budget_update=budget)
    if db_budget is None:
        raise HTTPException(status_code=404, detail="Budget not found")
    return db_budget

@router.delete("/{budget_id}")
def delete_budget(budget_id: int, db: Session = Depends(get_db)):
    """Delete a budget"""
    success = budget_crud.delete_budget(db, budget_id=budget_id)
    if not success:
        raise HTTPException(status_code=404, detail="Budget not found")
    return {"message": "Budget deleted successfully"}

@router.get("/fiscal-year/{fiscal_year}", response_model=List[Budget])
def read_budgets_by_fiscal_year(fiscal_year: int, db: Session = Depends(get_db)):
    """Get budgets by fiscal year"""
    return budget_crud.get_budget_by_fiscal_year(db, fiscal_year=fiscal_year)

@router.post("/{budget_id}/approve", response_model=BudgetApproval)
def approve_budget(budget_id: int, approval: BudgetApprovalCreate, db: Session = Depends(get_db)):
    """Approve or reject a budget"""
    return budget_crud.approve_budget(
        db=db,
        budget_id=budget_id,
        approver_id=approval.approver_id,
        status=approval.status,
        comments=approval.comments
    )