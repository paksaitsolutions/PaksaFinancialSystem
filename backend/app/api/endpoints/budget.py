from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from ..core.deps import get_db
from app.core.api_response import success_response, paginated_response, error_response
from app.core.pagination import PaginationParams, paginate_query
from ..crud import budget as budget_crud
from ..schemas.budget import Budget, BudgetCreate, BudgetUpdate, BudgetApprovalCreate, BudgetApproval

router = APIRouter()

@router.get("/")
def read_budgets(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all budgets with pagination"""
    try:
        # Mock pagination for now - replace with actual database query
        budgets = budget_crud.get_budgets(db, skip=0, limit=1000)  # Get all for simulation
        
        # Simulate pagination
        start = (page - 1) * page_size
        end = start + page_size
        paginated_budgets = budgets[start:end]
        
        pagination_meta = {
            "total": len(budgets),
            "page": page,
            "page_size": page_size,
            "pages": (len(budgets) + page_size - 1) // page_size,
            "has_next": end < len(budgets),
            "has_prev": page > 1
        }
        
        return paginated_response(
            data=paginated_budgets,
            pagination_meta=pagination_meta,
            message="Budgets retrieved successfully"
        )
    except Exception as e:
        return error_response(message=str(e), status_code=500)

@router.post("/")
def create_budget(budget: BudgetCreate, db: Session = Depends(get_db)):
    """Create a new budget"""
    try:
        new_budget = budget_crud.create_budget(db=db, budget=budget)
        return success_response(data=new_budget, message="Budget created successfully")
    except Exception as e:
        return error_response(message=str(e), status_code=400)

@router.get("/{budget_id}")
def read_budget(budget_id: int, db: Session = Depends(get_db)):
    """Get a specific budget"""
    try:
        db_budget = budget_crud.get_budget(db, budget_id=budget_id)
        if db_budget is None:
            return error_response(message="Budget not found", status_code=404)
        return success_response(data=db_budget, message="Budget retrieved successfully")
    except Exception as e:
        return error_response(message=str(e), status_code=500)

@router.put("/{budget_id}")
def update_budget(budget_id: int, budget: BudgetUpdate, db: Session = Depends(get_db)):
    """Update a budget"""
    try:
        db_budget = budget_crud.update_budget(db, budget_id=budget_id, budget_update=budget)
        if db_budget is None:
            return error_response(message="Budget not found", status_code=404)
        return success_response(data=db_budget, message="Budget updated successfully")
    except Exception as e:
        return error_response(message=str(e), status_code=400)

@router.delete("/{budget_id}")
def delete_budget(budget_id: int, db: Session = Depends(get_db)):
    """Delete a budget"""
    try:
        success = budget_crud.delete_budget(db, budget_id=budget_id)
        if not success:
            return error_response(message="Budget not found", status_code=404)
        return success_response(message="Budget deleted successfully")
    except Exception as e:
        return error_response(message=str(e), status_code=500)

@router.get("/fiscal-year/{fiscal_year}")
def read_budgets_by_fiscal_year(
    fiscal_year: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get budgets by fiscal year with pagination"""
    try:
        budgets = budget_crud.get_budget_by_fiscal_year(db, fiscal_year=fiscal_year)
        
        # Simulate pagination
        start = (page - 1) * page_size
        end = start + page_size
        paginated_budgets = budgets[start:end]
        
        pagination_meta = {
            "total": len(budgets),
            "page": page,
            "page_size": page_size,
            "pages": (len(budgets) + page_size - 1) // page_size,
            "has_next": end < len(budgets),
            "has_prev": page > 1
        }
        
        return paginated_response(
            data=paginated_budgets,
            pagination_meta=pagination_meta,
            message=f"Budgets for fiscal year {fiscal_year} retrieved successfully"
        )
    except Exception as e:
        return error_response(message=str(e), status_code=500)

@router.post("/{budget_id}/approve")
def approve_budget(budget_id: int, approval: BudgetApprovalCreate, db: Session = Depends(get_db)):
    """Approve or reject a budget"""
    try:
        approval_result = budget_crud.approve_budget(
            db=db,
            budget_id=budget_id,
            approver_id=approval.approver_id,
            status=approval.status,
            comments=approval.comments
        )
        return success_response(data=approval_result, message="Budget approval processed successfully")
    except Exception as e:
        return error_response(message=str(e), status_code=400)