"""
Paksa Financial System - Bank Accounts API Endpoints
Version: 1.0.0
Copyright (c) 2025 Paksa IT Solutions. All rights reserved.

This software is the proprietary information of Paksa IT Solutions.
Use is subject to license terms and restrictions.

API endpoints for managing bank accounts.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.schemas.user import User as UserSchema
from .. import schemas, services, exceptions

router = APIRouter()

@router.post(
    "/",
    response_model=schemas.BankAccountResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new bank account"
)
async def create_bank_account(
    account: schemas.BankAccountCreate,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Create a new bank account.
    
    Required permissions: cash:bank-accounts:create
    """
    try:
        account_service = services.BankAccountService(db)
        return account_service.create_bank_account(account, current_user.id)
    except exceptions.BankAccountAlreadyExists as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "bank_account_exists",
                "message": str(e),
                "details": {
                    "bank_name": e.bank_name,
                    "account_number": e.account_number
                }
            }
        )

@router.get(
    "/{account_id}",
    response_model=schemas.BankAccountResponse,
    summary="Get a bank account by ID"
)
async def get_bank_account(
    account_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Retrieve a bank account by its ID.
    
    Required permissions: cash:bank-accounts:read
    """
    try:
        account_service = services.BankAccountService(db)
        return account_service.get_bank_account(account_id)
    except exceptions.BankAccountNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "bank_account_not_found",
                "message": str(e),
                "details": {"account_id": str(account_id)}
            }
        )

@router.get(
    "/",
    response_model=schemas.PaginatedBankAccounts,
    summary="List bank accounts"
)
async def list_bank_accounts(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    search: Optional[str] = Query(None, description="Search term for bank name or account number"),
    status: Optional[schemas.BankAccountStatus] = Query(None, description="Filter by account status"),
    account_type: Optional[schemas.BankAccountType] = Query(None, description="Filter by account type"),
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    List bank accounts with optional filtering and pagination.
    
    Required permissions: cash:bank-accounts:read
    """
    account_service = services.BankAccountService(db)
    accounts, total = account_service.list_bank_accounts(
        skip=skip,
        limit=limit,
        search=search,
        status=status,
        account_type=account_type
    )
    
    return {
        "items": accounts,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.put(
    "/{account_id}",
    response_model=schemas.BankAccountResponse,
    summary="Update a bank account"
)
async def update_bank_account(
    account_id: UUID,
    account_update: schemas.BankAccountUpdate,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Update an existing bank account.
    
    Required permissions: cash:bank-accounts:update
    """
    try:
        account_service = services.BankAccountService(db)
        return account_service.update_bank_account(account_id, account_update, current_user.id)
    except exceptions.BankAccountNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "bank_account_not_found",
                "message": str(e),
                "details": {"account_id": str(account_id)}
            }
        )
    except exceptions.BankAccountAlreadyExists as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "bank_account_exists",
                "message": str(e),
                "details": {
                    "bank_name": e.bank_name,
                    "account_number": e.account_number
                }
            }
        )

@router.delete(
    "/{account_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a bank account"
)
async def delete_bank_account(
    account_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Delete a bank account.
    
    Required permissions: cash:bank-accounts:delete
    """
    try:
        account_service = services.BankAccountService(db)
        account_service.delete_bank_account(account_id)
        return None
    except exceptions.BankAccountNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "bank_account_not_found",
                "message": str(e),
                "details": {"account_id": str(account_id)}
            }
        )
    except exceptions.InvalidBankAccountOperation as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "invalid_operation",
                "message": str(e),
                "details": {
                    "account_id": str(account_id),
                    "operation": e.operation,
                    "reason": e.reason
                }
            }
        )

@router.post(
    "/{account_id}/balance",
    response_model=schemas.BankAccountResponse,
    summary="Update bank account balance"
)
async def update_bank_account_balance(
    account_id: UUID,
    balance_update: schemas.BankAccountBalanceUpdate,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Update a bank account's balance.
    
    This creates an adjustment transaction to reconcile the account balance.
    
    Required permissions: cash:bank-accounts:update
    """
    try:
        account_service = services.BankAccountService(db)
        return account_service.update_balance(account_id, balance_update, current_user.id)
    except exceptions.BankAccountNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "bank_account_not_found",
                "message": str(e),
                "details": {"account_id": str(account_id)}
            }
        )
