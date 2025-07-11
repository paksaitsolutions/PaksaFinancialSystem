from fastapi import APIRouter, Depends
from .services import ProjectAccountingService
from .schemas import ProjectSchema, ProjectExpenseSchema
from typing import List

router = APIRouter()

def get_service():
    # Placeholder for dependency injection
    pass

@router.get('/projects', response_model=List[ProjectSchema])
def list_projects(service: ProjectAccountingService = Depends(get_service)):
    return service.get_projects()

@router.get('/expenses', response_model=List[ProjectExpenseSchema])
def list_expenses(service: ProjectAccountingService = Depends(get_service)):
    return service.get_expenses()
