"""
Paksa Financial System - Bank Reconciliations API Endpoints
Version: 1.0.0
Copyright (c) 2025 Paksa IT Solutions. All rights reserved.

This software is the proprietary information of Paksa IT Solutions.
Use is subject to license terms and restrictions.

API endpoints for managing bank reconciliations.
"""

from typing import List, Optional
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.schemas.user import User as UserSchema
from .. import schemas, services, exceptions

router = APIRouter()

@router.post(
    "/",
    response_model=schemas.BankReconciliationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new bank reconciliation"
)
async def create_reconciliation(
    reconciliation: schemas.BankReconciliationCreate,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Create a new bank reconciliation.
    
    Required permissions: cash:reconciliations:create
    """
    try:
        reconciliation_service = services.ReconciliationService(db)
        return reconciliation_service.create_reconciliation(reconciliation, current_user.id)
    except exceptions.BankAccountNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "bank_account_not_found",
                "message": str(e),
                "details": {"account_id": str(reconciliation.account_id)}
            }
        )
    except exceptions.ReconciliationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "reconciliation_error",
                "message": str(e),
                "details": {"reconciliation_id": str(e.reconciliation_id) if hasattr(e, 'reconciliation_id') else None}
            }
        )

@router.get(
    "/{reconciliation_id}",
    response_model=schemas.BankReconciliationResponse,
    summary="Get a reconciliation by ID"
)
async def get_reconciliation(
    reconciliation_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Retrieve a bank reconciliation by its ID.
    
    Required permissions: cash:reconciliations:read
    """
    try:
        reconciliation_service = services.ReconciliationService(db)
        return reconciliation_service.get_reconciliation(reconciliation_id)
    except exceptions.ReconciliationNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "reconciliation_not_found",
                "message": str(e),
                "details": {"reconciliation_id": str(reconciliation_id)}
            }
        )

@router.get(
    "/",
    response_model=schemas.PaginatedBankReconciliations,
    summary="List reconciliations with filtering"
)
async def list_reconciliations(
    account_id: Optional[UUID] = Query(None, description="Filter by account ID"),
    status: Optional[schemas.ReconciliationStatus] = Query(None, description="Filter by reconciliation status"),
    start_date: Optional[date] = Query(None, description="Filter by start date (inclusive)"),
    end_date: Optional[date] = Query(None, description="Filter by end date (inclusive)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    List bank reconciliations with filtering and pagination.
    
    Required permissions: cash:reconciliations:read
    """
    reconciliation_service = services.ReconciliationService(db)
    reconciliations, total = reconciliation_service.list_reconciliations(
        account_id=account_id,
        status=status,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )
    
    return {
        "items": reconciliations,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.post(
    "/{reconciliation_id}/transactions",
    response_model=schemas.BankReconciliationResponse,
    summary="Add transactions to a reconciliation"
)
async def add_transactions_to_reconciliation(
    reconciliation_id: UUID,
    transaction_ids: List[UUID],
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Add transactions to an existing reconciliation.
    
    Required permissions: cash:reconciliations:update
    """
    try:
        reconciliation_service = services.ReconciliationService(db)
        reconciliation_service._add_transactions_to_reconciliation(
            reconciliation_id=reconciliation_id,
            transaction_ids=transaction_ids,
            user_id=current_user.id
        )
        
        # Recalculate reconciliation summary
        reconciliation = reconciliation_service.get_reconciliation(reconciliation_id)
        reconciliation_service._calculate_reconciliation_summary(reconciliation)
        db.commit()
        
        return reconciliation
    except exceptions.ReconciliationNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "reconciliation_not_found",
                "message": str(e),
                "details": {"reconciliation_id": str(reconciliation_id)}
            }
        )
    except exceptions.ReconciliationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "reconciliation_error",
                "message": str(e),
                "details": {"reconciliation_id": str(reconciliation_id)}
            }
        )

@router.post(
    "/{reconciliation_id}/complete",
    response_model=schemas.BankReconciliationResponse,
    summary="Complete a reconciliation"
)
async def complete_reconciliation(
    reconciliation_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Mark a reconciliation as completed.
    
    This will also lock the reconciliation from further changes.
    
    Required permissions: cash:reconciliations:complete
    """
    try:
        reconciliation_service = services.ReconciliationService(db)
        reconciliation = reconciliation_service.get_reconciliation(reconciliation_id)
        
        # Verify reconciliation is in progress
        if reconciliation.status != schemas.ReconciliationStatus.IN_PROGRESS:
            raise exceptions.ReconciliationError(
                reconciliation_id=reconciliation_id,
                message=f"Cannot complete reconciliation with status {reconciliation.status}"
            )
        
        # Verify difference is zero (or within tolerance)
        if abs(reconciliation.difference) > Decimal('0.01'):  # Allow for rounding errors
            raise exceptions.ReconciliationError(
                reconciliation_id=reconciliation_id,
                message=f"Cannot complete reconciliation with non-zero difference: {reconciliation.difference}"
            )
        
        # Update status to completed
        reconciliation.status = schemas.ReconciliationStatus.COMPLETED
        reconciliation.completed_at = datetime.utcnow()
        reconciliation.completed_by_id = current_user.id
        reconciliation.updated_at = datetime.utcnow()
        reconciliation.updated_by_id = current_user.id
        
        db.commit()
        db.refresh(reconciliation)
        
        return reconciliation
        
    except exceptions.ReconciliationNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "reconciliation_not_found",
                "message": str(e),
                "details": {"reconciliation_id": str(reconciliation_id)}
            }
        )
    except exceptions.ReconciliationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "reconciliation_error",
                "message": str(e),
                "details": {"reconciliation_id": str(reconciliation_id)}
            }
        )
