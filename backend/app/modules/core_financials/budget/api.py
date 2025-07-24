from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.db import get_db
from .services import BudgetService
from .schemas import Budget, BudgetCreate, BudgetUpdate, BudgetVsActual

router = APIRouter()
budget_service = BudgetService()

@router.post("/", response_model=Budget, status_code=status.HTTP_201_CREATED)
async def create_budget(budget: BudgetCreate, db: AsyncSession = Depends(get_db)):
    return await budget_service.create(db, obj_in=budget)

@router.get("/", response_model=List[Budget])
async def get_budgets(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await budget_service.get_multi(db, skip=skip, limit=limit)

@router.get("/{budget_id}", response_model=Budget)
async def get_budget(budget_id: int, db: AsyncSession = Depends(get_db)):
    budget = await budget_service.get(db, budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    return budget

@router.put("/{budget_id}", response_model=Budget)
async def update_budget(budget_id: int, budget_update: BudgetUpdate, db: AsyncSession = Depends(get_db)):
    budget = await budget_service.get(db, budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    return await budget_service.update(db, db_obj=budget, obj_in=budget_update)

@router.delete("/{budget_id}")
async def delete_budget(budget_id: int, db: AsyncSession = Depends(get_db)):
    budget = await budget_service.get(db, budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    await budget_service.remove(db, id=budget_id)
    return {"message": "Budget deleted successfully"}

@router.post("/{budget_id}/approve", response_model=Budget)
async def approve_budget(budget_id: int, notes: str = None, db: AsyncSession = Depends(get_db)):
    return await budget_service.approve_budget(db, budget_id, notes)

@router.post("/{budget_id}/reject", response_model=Budget)
async def reject_budget(budget_id: int, reason: str, db: AsyncSession = Depends(get_db)):
    return await budget_service.reject_budget(db, budget_id, reason)

@router.post("/{budget_id}/submit", response_model=Budget)
async def submit_budget(budget_id: int, db: AsyncSession = Depends(get_db)):
    return await budget_service.submit_for_approval(db, budget_id)

@router.get("/{budget_id}/vs-actual", response_model=BudgetVsActual)
async def get_budget_vs_actual(budget_id: int, period: str, db: AsyncSession = Depends(get_db)):
    return await budget_service.get_budget_vs_actual(db, budget_id, period)