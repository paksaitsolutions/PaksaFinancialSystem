from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.deps import get_db, get_current_user
from app.models.user import User
from .services import BudgetService
from .schemas import Budget, BudgetCreate, BudgetUpdate, BudgetVsActual

router = APIRouter()

@router.post("/", response_model=Budget, status_code=status.HTTP_201_CREATED)
async def create_budget(
    budget: BudgetCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    budget_service = BudgetService(db)
    return await budget_service.create(obj_in=budget, created_by=current_user.id)

@router.get("/", response_model=List[Budget])
async def get_budgets(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    budget_service = BudgetService(db)
    return await budget_service.get_multi(skip=skip, limit=limit, company_id=current_user.company_id)

@router.get("/{budget_id}", response_model=Budget)
async def get_budget(
    budget_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    budget_service = BudgetService(db)
    budget = await budget_service.get(budget_id, company_id=current_user.company_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    return budget

@router.put("/{budget_id}", response_model=Budget)
async def update_budget(
    budget_id: int, 
    budget_update: BudgetUpdate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    budget_service = BudgetService(db)
    budget = await budget_service.get(budget_id, company_id=current_user.company_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    return await budget_service.update(db_obj=budget, obj_in=budget_update, updated_by=current_user.id)

@router.delete("/{budget_id}")
async def delete_budget(
    budget_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    budget_service = BudgetService(db)
    budget = await budget_service.get(budget_id, company_id=current_user.company_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    await budget_service.remove(id=budget_id)
    return {"message": "Budget deleted successfully"}

@router.post("/{budget_id}/approve", response_model=Budget)
async def approve_budget(
    budget_id: int, 
    notes: str = None, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    budget_service = BudgetService(db)
    return await budget_service.approve_budget(budget_id, notes, approved_by=current_user.id)

@router.post("/{budget_id}/reject", response_model=Budget)
async def reject_budget(
    budget_id: int, 
    reason: str, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    budget_service = BudgetService(db)
    return await budget_service.reject_budget(budget_id, reason, rejected_by=current_user.id)

@router.post("/{budget_id}/submit", response_model=Budget)
async def submit_budget(
    budget_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    budget_service = BudgetService(db)
    return await budget_service.submit_for_approval(budget_id, submitted_by=current_user.id)

@router.get("/{budget_id}/vs-actual", response_model=BudgetVsActual)
async def get_budget_vs_actual(
    budget_id: int, 
    period: str, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    budget_service = BudgetService(db)
    return await budget_service.get_budget_vs_actual(budget_id, period, company_id=current_user.company_id)