# -*- coding: utf-8 -*-
"""
Paksa Financial System
----------------------
Version: 1.0
Author: Paksa IT Solutions
Copyright © 2023 Paksa IT Solutions

This file is part of the Paksa Financial System.
It is subject to the terms and conditions defined in
file 'LICENSE', which is part of this source code package.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional, Any, Dict, Tuple

from .....dependencies import get_db
from .. import schemas, services
from ..exceptions import BudgetNotFound, BudgetItemNotFound

router = APIRouter()

def get_budget_service(db: Session = Depends(get_db)) -> services.BudgetService:
    return services.BudgetService(db)

@router.post("/", response_model=schemas.Budget, status_code=status.HTTP_201_CREATED)
def paksa_create_budget(
    budget: schemas.BudgetCreate,
    service: services.BudgetService = Depends(get_budget_service),
    current_user_id: UUID = UUID("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11") # Placeholder
) -> Any:
    """Create a new budget."""
    return service.paksa_create_budget(budget=budget, user_id=current_user_id)

@router.get("/{budget_id}", response_model=schemas.Budget)
def paksa_get_budget(
    budget_id: UUID,
    service: services.BudgetService = Depends(get_budget_service)
) -> Any:
    """Retrieve a specific budget by its ID."""
    try:
        return service.paksa_get_budget(budget_id=budget_id)
    except BudgetNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/", response_model=schemas.BudgetList)
def paksa_list_budgets(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = Query(None),
    budget_type: Optional[str] = Query(None),
    q: Optional[str] = Query(None, alias="search"),
    service: services.BudgetService = Depends(get_budget_service)
) -> Any:
    """Retrieve a list of budgets with optional filtering and pagination."""
    budgets, total = service.paksa_list_budgets(skip=skip, limit=limit, status=status, budget_type=budget_type, q=q)
    return {"items": budgets, "total": total}

@router.put("/{budget_id}", response_model=schemas.Budget)
def paksa_update_budget(
    budget_id: UUID,
    budget_update: schemas.BudgetUpdate,
    service: services.BudgetService = Depends(get_budget_service),
    current_user_id: UUID = UUID("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11") # Placeholder
) -> Any:
    """Update an existing budget."""
    try:
        return service.paksa_update_budget(budget_id=budget_id, budget_update=budget_update, user_id=current_user_id)
    except BudgetNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def paksa_delete_budget(
    budget_id: UUID,
    service: services.BudgetService = Depends(get_budget_service),
    current_user_id: UUID = UUID("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11") # Placeholder
):
    """Delete a budget."""
    try:
        service.paksa_delete_budget(budget_id=budget_id, user_id=current_user_id)
    except BudgetNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("/{budget_id}/items/", response_model=schemas.BudgetItem, status_code=status.HTTP_201_CREATED)
def paksa_add_budget_item(
    budget_id: UUID,
    item: schemas.BudgetItemCreate,
    service: services.BudgetService = Depends(get_budget_service),
    current_user_id: UUID = UUID("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11") # Placeholder
) -> Any:
    """Add a new item to a budget."""
    try:
        return service.paksa_add_budget_item(budget_id=budget_id, item=item, user_id=current_user_id)
    except BudgetNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.put("/items/{item_id}", response_model=schemas.BudgetItem)
def paksa_update_budget_item(
    item_id: UUID,
    item_update: schemas.BudgetItemUpdate,
    service: services.BudgetService = Depends(get_budget_service),
    current_user_id: UUID = UUID("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11") # Placeholder
) -> Any:
    """Update a budget item."""
    try:
        return service.paksa_update_budget_item(item_id=item_id, item_update=item_update, user_id=current_user_id)
    except BudgetItemNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def paksa_delete_budget_item(
    item_id: UUID,
    service: services.BudgetService = Depends(get_budget_service),
    current_user_id: UUID = UUID("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11") # Placeholder
):
    """Delete a budget item."""
    try:
        service.paksa_delete_budget_item(item_id=item_id, user_id=current_user_id)
    except BudgetItemNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/health-check", status_code=status.HTTP_200_OK)
def paksa_health_check(service: services.BudgetService = Depends(get_budget_service)) -> Dict[str, str]:
    """Perform a health check on the budget service."""
    return service.paksa_health_check()
