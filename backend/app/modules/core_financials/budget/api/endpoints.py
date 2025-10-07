# -*- coding: utf-8 -*-
"""
Paksa Financial System - Budget API Endpoints
--------------------------------------------
Version: 1.0
Author: Paksa IT Solutions
Copyright © 2023 Paksa IT Solutions
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Any, Dict
from datetime import datetime

from app.core.deps import get_db, get_current_user
from app.models.user import User
from .. import schemas, models
from ..services import BudgetService

router = APIRouter()

def get_budget_service(db: Session = Depends(get_db)) -> BudgetService:
    return BudgetService(db)

@router.post("/", response_model=schemas.Budget, status_code=status.HTTP_201_CREATED)
def create_budget(
    budget: schemas.BudgetCreate,
    service: BudgetService = Depends(get_budget_service),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Create a new budget."""
    return service.create_budget(budget=budget, user_id=current_user.id)

@router.get("/{budget_id}", response_model=schemas.Budget)
def get_budget(
    budget_id: int,
    service: BudgetService = Depends(get_budget_service),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Retrieve a specific budget by its ID."""
    budget = service.get_budget(budget_id=budget_id)
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )
    return budget

@router.get("/", response_model=schemas.BudgetList)
def list_budgets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    service: BudgetService = Depends(get_budget_service),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Retrieve a list of budgets with optional filtering and pagination."""
    budgets, total = service.list_budgets(
        skip=skip, 
        limit=limit, 
        status=status, 
        budget_type=type, 
        search=search
    )
    return schemas.BudgetList(items=budgets, total=total)

@router.put("/{budget_id}", response_model=schemas.Budget)
def update_budget(
    budget_id: int,
    budget_update: schemas.BudgetUpdate,
    service: BudgetService = Depends(get_budget_service),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Update an existing budget."""
    budget = service.update_budget(
        budget_id=budget_id, 
        budget_update=budget_update, 
        user_id=current_user.id
    )
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )
    return budget

@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(
    budget_id: int,
    service: BudgetService = Depends(get_budget_service),
    current_user: User = Depends(get_current_user)
):
    """Delete a budget."""
    success = service.delete_budget(budget_id=budget_id, user_id=current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )

@router.post("/{budget_id}/submit", response_model=schemas.Budget)
def submit_budget_for_approval(
    budget_id: int,
    service: BudgetService = Depends(get_budget_service),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Submit a budget for approval."""
    budget = service.submit_for_approval(budget_id=budget_id, user_id=current_user.id)
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )
    return budget

@router.post("/{budget_id}/approve", response_model=schemas.Budget)
def approve_budget(
    budget_id: int,
    approval_data: Dict[str, Any] = None,
    service: BudgetService = Depends(get_budget_service),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Approve a budget."""
    notes = approval_data.get("notes") if approval_data else None
    budget = service.approve_budget(budget_id=budget_id, user_id=current_user.id, notes=notes)
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )
    return budget

@router.post("/{budget_id}/reject", response_model=schemas.Budget)
def reject_budget(
    budget_id: int,
    rejection_data: Dict[str, str],
    service: BudgetService = Depends(get_budget_service),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Reject a budget."""
    reason = rejection_data.get("reason", "")
    if not reason:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rejection reason is required"
        )
    
    budget = service.reject_budget(budget_id=budget_id, user_id=current_user.id, reason=reason)
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )
    return budget

@router.get("/{budget_id}/vs-actual")
def get_budget_vs_actual(
    budget_id: int,
    period: Optional[str] = Query(None),
    service: BudgetService = Depends(get_budget_service),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get budget vs actual comparison."""
    result = service.get_budget_vs_actual(budget_id=budget_id, period=period)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )
    return result

@router.post("/{budget_id}/line-items", response_model=schemas.BudgetLineItem, status_code=status.HTTP_201_CREATED)
def add_line_item(
    budget_id: int,
    line_item: schemas.BudgetLineItemCreate,
    service: BudgetService = Depends(get_budget_service),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Add a new line item to a budget."""
    result = service.add_line_item(budget_id=budget_id, line_item=line_item)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )
    return result

@router.put("/line-items/{line_item_id}", response_model=schemas.BudgetLineItem)
def update_line_item(
    line_item_id: int,
    line_item_update: schemas.BudgetLineItemCreate,
    service: BudgetService = Depends(get_budget_service),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Update a budget line item."""
    result = service.update_line_item(line_item_id=line_item_id, line_item_update=line_item_update)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Line item not found"
        )
    return result

@router.delete("/line-items/{line_item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_line_item(
    line_item_id: int,
    service: BudgetService = Depends(get_budget_service),
    current_user: User = Depends(get_current_user)
):
    """Delete a budget line item."""
    success = service.delete_line_item(line_item_id=line_item_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Line item not found"
        )

@router.get("/health-check", status_code=status.HTTP_200_OK)
def health_check(service: BudgetService = Depends(get_budget_service)) -> Dict[str, str]:
    """Perform a health check on the budget service."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}