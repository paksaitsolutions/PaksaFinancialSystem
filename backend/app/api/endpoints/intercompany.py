"""
Intercompany API endpoints.
"""
from datetime import date
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import models
from app.api import deps
from app.core.db.session import get_db
from app.schemas.intercompany_schemas import (
    IntercompanyTransactionCreate,
    IntercompanyTransactionUpdate,
    IntercompanyTransactionResponse,
    IntercompanyReconciliationResponse,
    IntercompanyTransactionStatus
)
from app.services.intercompany.intercompany_service import IntercompanyService

router = APIRouter()


def get_intercompany_service(db: Session = Depends(get_db)) -> IntercompanyService:
    """Get an instance of the intercompany service."""
    return IntercompanyService(db)


@router.post(
    "/transactions",
    response_model=IntercompanyTransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create intercompany transaction",
    description="Create a new intercompany transaction between two companies.",
    tags=["Intercompany Transactions"]
)
async def create_transaction(
    transaction: IntercompanyTransactionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> IntercompanyTransactionResponse:
    """Create a new intercompany transaction."""
    service = get_intercompany_service(db)
    
    try:
        return service.create_transaction(transaction.dict(), current_user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/transactions/{transaction_id}",
    response_model=IntercompanyTransactionResponse,
    summary="Get intercompany transaction",
    description="Get an intercompany transaction by ID.",
    tags=["Intercompany Transactions"]
)
async def get_transaction(
    transaction_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> IntercompanyTransactionResponse:
    """Get an intercompany transaction by ID."""
    service = get_intercompany_service(db)
    
    transaction = service.get_transaction(transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction {transaction_id} not found"
        )
    
    return transaction


@router.get(
    "/transactions",
    response_model=List[IntercompanyTransactionResponse],
    summary="List intercompany transactions",
    description="List intercompany transactions with optional filters.",
    tags=["Intercompany Transactions"]
)
async def list_transactions(
    company_id: Optional[UUID] = None,
    status_filter: Optional[IntercompanyTransactionStatus] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> List[IntercompanyTransactionResponse]:
    """List intercompany transactions with optional filters."""
    service = get_intercompany_service(db)
    
    return service.list_transactions(
        company_id=company_id,
        status=status_filter,
        skip=skip,
        limit=limit
    )


@router.post(
    "/transactions/{transaction_id}/approve",
    response_model=IntercompanyTransactionResponse,
    summary="Approve intercompany transaction",
    description="Approve a pending intercompany transaction.",
    tags=["Intercompany Transactions"]
)
async def approve_transaction(
    transaction_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> IntercompanyTransactionResponse:
    """Approve a pending intercompany transaction."""
    service = get_intercompany_service(db)
    
    try:
        return service.approve_transaction(transaction_id, current_user.id)
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
    "/transactions/{transaction_id}/post",
    response_model=IntercompanyTransactionResponse,
    summary="Post intercompany transaction",
    description="Post an approved intercompany transaction to create journal entries.",
    tags=["Intercompany Transactions"]
)
async def post_transaction(
    transaction_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> IntercompanyTransactionResponse:
    """Post an approved intercompany transaction."""
    service = get_intercompany_service(db)
    
    try:
        return service.post_transaction(transaction_id, current_user.id)
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