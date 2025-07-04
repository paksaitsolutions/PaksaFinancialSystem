"""
Paksa Financial System - Bank Transactions API Endpoints
Version: 1.0.0
Copyright (c) 2025 Paksa IT Solutions. All rights reserved.

This software is the proprietary information of Paksa IT Solutions.
Use is subject to license terms and restrictions.

API endpoints for managing bank transactions.
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
    response_model=schemas.BankTransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new bank transaction"
)
async def create_transaction(
    transaction: schemas.BankTransactionCreate,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Create a new bank transaction.
    
    Required permissions: cash:transactions:create
    """
    try:
        transaction_service = services.TransactionService(db)
        return transaction_service.create_transaction(transaction, current_user.id)
    except exceptions.BankAccountNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "bank_account_not_found",
                "message": str(e),
                "details": {"account_id": str(transaction.account_id)}
            }
        )
    except exceptions.InsufficientFundsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "insufficient_funds",
                "message": str(e),
                "details": {
                    "account_id": str(e.account_id),
                    "available_balance": float(e.available_balance),
                    "requested_amount": float(e.requested_amount)
                }
            }
        )

@router.get(
    "/{transaction_id}",
    response_model=schemas.BankTransactionResponse,
    summary="Get a transaction by ID"
)
async def get_transaction(
    transaction_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Retrieve a bank transaction by its ID.
    
    Required permissions: cash:transactions:read
    """
    try:
        transaction_service = services.TransactionService(db)
        return transaction_service.get_transaction(transaction_id)
    except exceptions.TransactionNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "transaction_not_found",
                "message": str(e),
                "details": {"transaction_id": str(transaction_id)}
            }
        )

@router.get(
    "/",
    response_model=schemas.PaginatedBankTransactions,
    summary="List transactions with filtering"
)
async def list_transactions(
    account_id: Optional[UUID] = Query(None, description="Filter by account ID"),
    start_date: Optional[date] = Query(None, description="Filter by start date (inclusive)"),
    end_date: Optional[date] = Query(None, description="Filter by end date (inclusive)"),
    transaction_type: Optional[schemas.TransactionType] = Query(None, description="Filter by transaction type"),
    status: Optional[schemas.TransactionStatus] = Query(None, description="Filter by transaction status"),
    category_id: Optional[UUID] = Query(None, description="Filter by category ID"),
    search: Optional[str] = Query(None, description="Search in reference, memo, notes, or payee"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    List bank transactions with filtering and pagination.
    
    Required permissions: cash:transactions:read
    """
    transaction_service = services.TransactionService(db)
    transactions, total = transaction_service.list_transactions(
        account_id=account_id,
        start_date=start_date,
        end_date=end_date,
        transaction_type=transaction_type,
        status=status,
        category_id=category_id,
        search=search,
        skip=skip,
        limit=limit
    )
    
    return {
        "items": transactions,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.put(
    "/{transaction_id}",
    response_model=schemas.BankTransactionResponse,
    summary="Update a transaction"
)
async def update_transaction(
    transaction_id: UUID,
    transaction_update: schemas.BankTransactionUpdate,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Update an existing bank transaction.
    
    Required permissions: cash:transactions:update
    """
    try:
        transaction_service = services.TransactionService(db)
        # Implementation would go here
        raise HTTPException(status_code=501, detail="Not implemented")
    except exceptions.TransactionNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "transaction_not_found",
                "message": str(e),
                "details": {"transaction_id": str(transaction_id)}
            }
        )

@router.delete(
    "/{transaction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Void a transaction"
)
async def void_transaction(
    transaction_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Void a bank transaction.
    
    This creates a reversal transaction rather than deleting the original.
    
    Required permissions: cash:transactions:void
    """
    try:
        transaction_service = services.TransactionService(db)
        # Implementation would go here
        return None
    except exceptions.TransactionNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "transaction_not_found",
                "message": str(e),
                "details": {"transaction_id": str(transaction_id)}
            }
        )
    except exceptions.InvalidTransactionOperation as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "invalid_operation",
                "message": str(e),
                "details": {
                    "transaction_id": str(transaction_id),
                    "operation": e.operation,
                    "reason": e.reason
                }
            }
        )
