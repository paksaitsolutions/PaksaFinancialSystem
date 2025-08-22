"""
Allocation API endpoints.
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import models
from app.api import deps
from app.core.db.session import get_db
from app.schemas.allocation_schemas import (
    AllocationRuleCreate,
    AllocationRuleUpdate,
    AllocationRuleResponse,
    AllocationResponse
)
from app.services.allocation.allocation_engine import AllocationEngine

router = APIRouter()


def get_allocation_engine(db: Session = Depends(get_db)) -> AllocationEngine:
    """Get an instance of the allocation engine."""
    return AllocationEngine(db)


@router.post(
    "/rules",
    response_model=AllocationRuleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create allocation rule",
    description="Create a new allocation rule for automatic transaction allocation.",
    tags=["Allocation Rules"]
)
async def create_allocation_rule(
    rule: AllocationRuleCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> AllocationRuleResponse:
    """Create a new allocation rule."""
    engine = get_allocation_engine(db)
    
    try:
        return engine.create_allocation_rule(rule.dict(), current_user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/rules/{rule_id}",
    response_model=AllocationRuleResponse,
    summary="Get allocation rule",
    description="Get an allocation rule by ID.",
    tags=["Allocation Rules"]
)
async def get_allocation_rule(
    rule_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> AllocationRuleResponse:
    """Get an allocation rule by ID."""
    engine = get_allocation_engine(db)
    
    rule = engine.get_allocation_rule(rule_id)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Allocation rule {rule_id} not found"
        )
    
    return rule


@router.get(
    "/rules",
    response_model=List[AllocationRuleResponse],
    summary="List allocation rules",
    description="List allocation rules with optional filters.",
    tags=["Allocation Rules"]
)
async def list_allocation_rules(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> List[AllocationRuleResponse]:
    """List allocation rules."""
    engine = get_allocation_engine(db)
    
    return engine.get_allocation_rules(skip=skip, limit=limit)


@router.post(
    "/process/{journal_entry_id}",
    response_model=Optional[AllocationResponse],
    summary="Process allocation",
    description="Process allocation for a journal entry based on matching rules.",
    tags=["Allocations"]
)
async def process_allocation(
    journal_entry_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Optional[AllocationResponse]:
    """Process allocation for a journal entry."""
    engine = get_allocation_engine(db)
    
    try:
        return engine.process_allocation(journal_entry_id, current_user.id)
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )