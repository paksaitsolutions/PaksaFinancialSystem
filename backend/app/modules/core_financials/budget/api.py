from fastapi import APIRouter, Depends
from .services import BudgetService
from .schemas import BudgetSchema, BudgetItemSchema
from typing import List

router = APIRouter()

def get_service():
    # Placeholder for dependency injection
    pass

@router.get('/budgets', response_model=List[BudgetSchema])
def list_budgets(service: BudgetService = Depends(get_service)):
    return service.get_budgets()

@router.get('/budget-items', response_model=List[BudgetItemSchema])
def list_budget_items(service: BudgetService = Depends(get_service)):
    return service.get_budget_items()
