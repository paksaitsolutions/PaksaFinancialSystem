"""
Period close API endpoints.
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models
from app.api import deps
from app.core.db.session import get_db
from app.schemas.period_close_schemas import (
    AccountingPeriodCreate,
    AccountingPeriodResponse,
    PeriodCloseResponse,
    PeriodCloseTaskResponse
)
from app.services.period_close.period_close_service import PeriodCloseService

router = APIRouter()


def get_period_close_service(db: Session = Depends(get_db)) -> PeriodCloseService:
    """Get an instance of the period close service."""
    return PeriodCloseService(db)


@router.post(
    "/periods",
    response_model=AccountingPeriodResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create accounting period",
    description="Create a new accounting period.",
    tags=["Accounting Periods"]
)
async def create_accounting_period(
    period: AccountingPeriodCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> AccountingPeriodResponse:
    """Create a new accounting period."""
    service = get_period_close_service(db)
    
    try:
        return service.create_accounting_period(period.dict(), current_user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/periods",
    response_model=List[AccountingPeriodResponse],
    summary="List accounting periods",
    description="List accounting periods.",
    tags=["Accounting Periods"]
)
async def list_accounting_periods(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> List[AccountingPeriodResponse]:
    """List accounting periods."""
    service = get_period_close_service(db)
    
    return service.list_accounting_periods(skip=skip, limit=limit)


@router.post(
    "/periods/{period_id}/close",
    response_model=PeriodCloseResponse,
    summary="Initiate period close",
    description="Initiate the close process for an accounting period.",
    tags=["Period Close"]
)
async def initiate_period_close(
    period_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> PeriodCloseResponse:
    """Initiate period close process."""
    service = get_period_close_service(db)
    
    try:
        return service.initiate_period_close(period_id, current_user.id)
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


@router.get(
    "/closes",
    response_model=List[PeriodCloseResponse],
    summary="List period closes",
    description="List period close processes.",
    tags=["Period Close"]
)
async def list_period_closes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> List[PeriodCloseResponse]:
    """List period closes."""
    service = get_period_close_service(db)
    
    return service.list_period_closes(skip=skip, limit=limit)


@router.post(
    "/tasks/{task_id}/execute",
    response_model=PeriodCloseTaskResponse,
    summary="Execute close task",
    description="Execute a period close task.",
    tags=["Period Close"]
)
async def execute_close_task(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> PeriodCloseTaskResponse:
    """Execute a close task."""
    service = get_period_close_service(db)
    
    try:
        return service.execute_close_task(task_id, current_user.id)
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


@router.post(
    "/closes/{close_id}/complete",
    response_model=PeriodCloseResponse,
    summary="Complete period close",
    description="Complete a period close process.",
    tags=["Period Close"]
)
async def complete_period_close(
    close_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> PeriodCloseResponse:
    """Complete period close process."""
    service = get_period_close_service(db)
    
    try:
        return service.complete_period_close(close_id, current_user.id)
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