"""
Account API Endpoints

This module provides API endpoints for managing chart of accounts.
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from core.database import get_db
from core.security import get_current_active_user
from modules.core_financials.accounting import (
    AccountService,
    Account,
    AccountType,
    AccountStatus,
    AccountNotFoundException,
    DuplicateAccountCodeException,
    InvalidAccountTypeException,
)
from modules.users.models import User

router = APIRouter()


@router.get("/", response_model=List[dict], summary="List all accounts")
async def list_accounts(
    skip: int = 0,
    limit: int = 100,
    type: Optional[AccountType] = None,
    status: Optional[AccountStatus] = None,
    parent_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve a list of accounts with optional filtering.
    """
    with AccountService(db) as service:
        accounts = service.list_accounts(skip=skip, limit=limit, type=type, status=status, parent_id=parent_id)
        return [
            {
                "id": str(account.id),
                "code": account.code,
                "name": account.name,
                "type": account.type,
                "status": account.status,
                "parent_id": str(account.parent_id) if account.parent_id else None,
                "is_contra": account.is_contra,
                "normal_balance": account.normal_balance,
                "current_balance": float(account.current_balance) if hasattr(account, 'current_balance') else 0.0,
            }
            for account in accounts
        ]


@router.get("/{account_id}", response_model=dict, summary="Get account by ID")
async def get_account(
    account_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get a specific account by ID.
    """
    with AccountService(db) as service:
        try:
            account = service.get_account(account_id)
            return {
                "id": str(account.id),
                "code": account.code,
                "name": account.name,
                "description": account.description,
                "type": account.type,
                "subtype": account.subtype,
                "status": account.status,
                "currency": account.currency,
                "is_contra": account.is_contra,
                "is_system_account": account.is_system_account,
                "parent_id": str(account.parent_id) if account.parent_id else None,
                "normal_balance": account.normal_balance,
                "current_balance": float(account.current_balance) if hasattr(account, 'current_balance') else 0.0,
                "created_at": account.created_at.isoformat(),
                "updated_at": account.updated_at.isoformat(),
            }
        except AccountNotFoundException as e:
            raise HTTPException(status_code=404, detail=str(e))


@router.post("/", response_model=dict, status_code=201, summary="Create a new account")
async def create_account(
    account_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new account in the chart of accounts.
    """
    with AccountService(db) as service:
        try:
            # TODO: Add validation for required fields
            account = service.create_account(
                code=account_data["code"],
                name=account_data["name"],
                type=account_data["type"],
                parent_id=account_data.get("parent_id"),
                description=account_data.get("description"),
                subtype=account_data.get("subtype"),
                currency=account_data.get("currency", "USD"),
                is_contra=account_data.get("is_contra", False),
                status=account_data.get("status", "active"),
            )
            
            return {
                "id": str(account.id),
                "code": account.code,
                "name": account.name,
                "type": account.type,
                "status": account.status,
                "message": "Account created successfully"
            }
            
        except (DuplicateAccountCodeException, InvalidAccountTypeException) as e:
            raise HTTPException(status_code=400, detail=str(e))
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(status_code=400, detail="Database integrity error")


@router.put("/{account_id}", response_model=dict, summary="Update an existing account")
async def update_account(
    account_id: UUID,
    account_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update an existing account.
    """
    with AccountService(db) as service:
        try:
            # TODO: Add validation for allowed fields
            account = service.update_account(
                account_id=account_id,
                **account_data
            )
            
            return {
                "id": str(account.id),
                "code": account.code,
                "name": account.name,
                "type": account.type,
                "status": account.status,
                "message": "Account updated successfully"
            }
            
        except AccountNotFoundException as e:
            raise HTTPException(status_code=404, detail=str(e))
        except (DuplicateAccountCodeException, InvalidAccountTypeException) as e:
            raise HTTPException(status_code=400, detail=str(e))
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(status_code=400, detail="Database integrity error")


@router.delete("/{account_id}", status_code=204, summary="Delete an account")
async def delete_account(
    account_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete an account from the chart of accounts.
    """
    with AccountService(db) as service:
        try:
            service.delete_account(account_id)
            return None
            
        except AccountNotFoundException as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e))
