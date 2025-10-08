from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime, timedelta
from app.api import deps
from app.models.budget import Budget, BudgetLineItem, BudgetActual, BudgetApproval
from app.schemas.budget import (
    Budget as BudgetSchema,
    BudgetCreate,
    BudgetUpdate,
    BudgetSummary,
    BudgetVariance
)
from decimal import Decimal

router = APIRouter()

@router.get("/", response_model=List[BudgetSchema])
def get_budgets(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    type: str = None,
    db: Session = Depends(deps.get_db)
):
    query = db.query(Budget)
    if status:
        query = query.filter(Budget.status == status)
    if type:
        query = query.filter(Budget.type == type)
    budgets = query.offset(skip).limit(limit).all()
    return budgets

@router.post("/", response_model=BudgetSchema)
def create_budget(
    budget_in: BudgetCreate,
    db: Session = Depends(deps.get_db)
):
    budget = Budget(**budget_in.dict(exclude={"line_items"}))
    db.add(budget)
    db.commit()
    db.refresh(budget)
    
    for item_data in budget_in.line_items:
        item = BudgetLineItem(**item_data.dict(), budget_id=budget.id)
        db.add(item)
    
    db.commit()
    db.refresh(budget)
    return budget

@router.get("/{budget_id}", response_model=BudgetSchema)
def get_budget(
    budget_id: int,
    db: Session = Depends(deps.get_db)
):
    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    return budget

@router.put("/{budget_id}", response_model=BudgetSchema)
def update_budget(
    budget_id: int,
    budget_in: BudgetUpdate,
    db: Session = Depends(deps.get_db)
):
    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    for field, value in budget_in.dict(exclude_unset=True).items():
        setattr(budget, field, value)
    
    db.commit()
    db.refresh(budget)
    return budget

@router.delete("/{budget_id}")
def delete_budget(
    budget_id: int,
    db: Session = Depends(deps.get_db)
):
    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    db.delete(budget)
    db.commit()
    return {"message": "Budget deleted successfully"}

@router.get("/summary/dashboard", response_model=BudgetSummary)
def get_budget_summary(db: Session = Depends(deps.get_db)):
    total_budgets = db.query(Budget).count()
    total_amount = db.query(func.sum(Budget.amount)).scalar() or 0
    approved_amount = db.query(func.sum(Budget.amount)).filter(Budget.status == "APPROVED").scalar() or 0
    pending_amount = db.query(func.sum(Budget.amount)).filter(Budget.status == "PENDING_APPROVAL").scalar() or 0
    
    utilization_rate = (float(approved_amount) / float(total_amount) * 100) if total_amount > 0 else 0
    
    return BudgetSummary(
        total_budgets=total_budgets,
        total_amount=total_amount,
        approved_amount=approved_amount,
        pending_amount=pending_amount,
        utilization_rate=utilization_rate
    )

@router.get("/variance/analysis", response_model=List[BudgetVariance])
def get_budget_variance(db: Session = Depends(deps.get_db)):
    # Get budget vs actual data
    budgets = db.query(Budget).filter(Budget.status == "APPROVED").all()
    variances = []
    
    for budget in budgets:
        for line_item in budget.line_items:
            actual_amount = db.query(func.sum(BudgetActual.actual_amount)).filter(
                BudgetActual.budget_id == budget.id,
                BudgetActual.category == line_item.category
            ).scalar() or 0
            
            variance = float(line_item.amount) - float(actual_amount)
            variance_percent = (variance / float(line_item.amount) * 100) if line_item.amount > 0 else 0
            
            status = "Under Budget" if variance > 0 else "Over Budget" if variance < 0 else "On Budget"
            
            variances.append(BudgetVariance(
                category=line_item.category,
                budget=line_item.amount,
                actual=actual_amount,
                variance=variance,
                variance_percent=variance_percent,
                status=status
            ))
    
    return variances

@router.post("/{budget_id}/approve")
def approve_budget(
    budget_id: int,
    notes: str = "",
    db: Session = Depends(deps.get_db)
):
    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    budget.status = "APPROVED"
    
    approval = BudgetApproval(
        budget_id=budget_id,
        action="APPROVED",
        notes=notes,
        approved_by="Admin User"
    )
    db.add(approval)
    db.commit()
    
    return {"message": "Budget approved successfully"}

@router.post("/{budget_id}/reject")
def reject_budget(
    budget_id: int,
    notes: str = "",
    db: Session = Depends(deps.get_db)
):
    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    budget.status = "REJECTED"
    
    approval = BudgetApproval(
        budget_id=budget_id,
        action="REJECTED",
        notes=notes,
        approved_by="Admin User"
    )
    db.add(approval)
    db.commit()
    
    return {"message": "Budget rejected successfully"}

@router.get("/reports/budget-vs-actual")
def get_budget_vs_actual_report(db: Session = Depends(deps.get_db)):
    budgets = db.query(Budget).filter(Budget.status == "APPROVED").all()
    
    total_budget = sum(float(b.amount) for b in budgets)
    total_actual = 0
    details = []
    
    for budget in budgets:
        actual_amount = db.query(func.sum(BudgetActual.actual_amount)).filter(
            BudgetActual.budget_id == budget.id
        ).scalar() or 0
        
        total_actual += float(actual_amount)
        variance = float(budget.amount) - float(actual_amount)
        variance_percent = (variance / float(budget.amount) * 100) if budget.amount > 0 else 0
        
        details.append({
            "category": budget.name,
            "budget": float(budget.amount),
            "actual": float(actual_amount),
            "variance": variance,
            "variancePercent": variance_percent,
            "status": "Under Budget" if variance > 0 else "Over Budget" if variance < 0 else "On Budget"
        })
    
    total_variance = total_budget - total_actual
    total_variance_percent = (total_variance / total_budget * 100) if total_budget > 0 else 0
    
    return {
        "totalBudget": total_budget,
        "totalActual": total_actual,
        "variance": total_variance,
        "variancePercent": total_variance_percent,
        "details": details
    }