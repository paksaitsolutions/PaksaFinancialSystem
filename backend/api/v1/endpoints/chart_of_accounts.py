"""
Chart of Accounts API Endpoints
"""
from typing import List, Optional
from uuid import UUID
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.security import get_current_active_user
from schemas.user import User as UserSchema
from schemas.chart_of_accounts import (
    ChartOfAccounts,
    ChartOfAccountsCreate,
    ChartOfAccountsUpdate,
    ChartOfAccountsTree,
    ChartOfAccountsWithBalance
)
from crud.chart_of_accounts import crud_chart_of_accounts
from core.exceptions import (
    NotFoundException,
    BadRequestException,
    ValidationException
)

router = APIRouter()

@router.get(
    "/",
    response_model=List[ChartOfAccounts],
    summary="List Chart of Accounts"
)
async def read_chart_of_accounts(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    account_type: Optional[str] = None,
    parent_id: Optional[UUID] = None,
    include_inactive: bool = False,
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Retrieve chart of accounts with optional filtering.
    """
    accounts, total = await crud_chart_of_accounts.get_multi(
        db,
        skip=skip,
        limit=limit,
        category=category,
        account_type=account_type,
        parent_id=parent_id,
        include_inactive=include_inactive
    )
    
    return accounts

@router.get(
    "/tree",
    response_model=List[ChartOfAccountsTree],
    summary="Get Chart of Accounts as Tree"
)
async def read_chart_of_accounts_tree(
    db: AsyncSession = Depends(get_db),
    parent_id: Optional[UUID] = None,
    include_inactive: bool = False,
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Retrieve chart of accounts as a hierarchical tree.
    """
    return await crud_chart_of_accounts.get_tree(
        db,
        parent_id=parent_id,
        include_inactive=include_inactive
    )

@router.post(
    "/",
    response_model=ChartOfAccounts,
    status_code=status.HTTP_201_CREATED,
    summary="Create Chart of Accounts Entry"
)
async def create_chart_of_accounts(
    *,
    db: AsyncSession = Depends(get_db),
    chart_of_accounts_in: ChartOfAccountsCreate,
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Create a new chart of accounts entry.
    """
    try:
        return await crud_chart_of_accounts.create(
            db,
            obj_in=chart_of_accounts_in,
            created_by_id=current_user.id
        )
    except (NotFoundException, ValidationException, BadRequestException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the chart of accounts entry"
        )

@router.get(
    "/{account_id}",
    response_model=ChartOfAccountsWithBalance,
    summary="Get Chart of Accounts by ID"
)
async def read_chart_of_accounts_by_id(
    account_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Get a specific chart of accounts entry by ID.
    """
    account = await crud_chart_of_accounts.get_by_id(db, id=account_id)
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chart of accounts entry not found"
        )
    
    # Calculate current balance
    balance_info = await crud_chart_of_accounts.calculate_account_balance(db, account_id)
    
    # Convert to dict and add balance info
    account_data = account.to_dict()
    account_data.update({
        'balance': float(balance_info['balance']),
        'balance_debit': float(balance_info['debit']),
        'balance_credit': float(balance_info['credit'])
    })
    
    return ChartOfAccountsWithBalance(**account_data)

@router.put(
    "/{account_id}",
    response_model=ChartOfAccounts,
    summary="Update Chart of Accounts Entry"
)
async def update_chart_of_accounts(
    *,
    db: AsyncSession = Depends(get_db),
    account_id: UUID,
    chart_of_accounts_in: ChartOfAccountsUpdate,
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Update a chart of accounts entry.
    """
    # Get the existing account
    account = await crud_chart_of_accounts.get_by_id(db, id=account_id, include_inactive=True)
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chart of accounts entry not found"
        )
    
    try:
        return await crud_chart_of_accounts.update(
            db,
            db_obj=account,
            obj_in=chart_of_accounts_in,
            updated_by_id=current_user.id
        )
    except (BadRequestException, ValidationException, NotFoundException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the chart of accounts entry"
        )

@router.delete(
    "/{account_id}",
    response_model=ChartOfAccounts,
    summary="Delete Chart of Accounts Entry"
)
async def delete_chart_of_accounts(
    *,
    db: AsyncSession = Depends(get_db),
    account_id: UUID,
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Delete a chart of accounts entry (soft delete).
    """
    # Get the existing account
    account = await crud_chart_of_accounts.get_by_id(db, id=account_id, include_inactive=True)
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chart of accounts entry not found"
        )
    
    try:
        return await crud_chart_of_accounts.delete(
            db,
            db_obj=account,
            deleted_by_id=current_user.id
        )
    except (BadRequestException, ValidationException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the chart of accounts entry"
        )

@router.get(
    "/{account_id}/balance",
    response_model=dict,
    summary="Get Account Balance"
)
async def get_account_balance(
    account_id: UUID,
    as_of_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Get the current balance of an account.
    """
    # Check if account exists
    account = await crud_chart_of_accounts.get_by_id(db, id=account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chart of accounts entry not found"
        )
    
    # Calculate balance
    balance_info = await crud_chart_of_accounts.calculate_account_balance(
        db, 
        account_id,
        as_of_date=as_of_date
    )
    
    return {
        "account_id": account_id,
        "account_code": account.code,
        "account_name": account.name,
        "as_of_date": as_of_date or date.today().isoformat(),
        "balance": float(balance_info['balance']),
        "debit": float(balance_info['debit']),
        "credit": float(balance_info['credit'])
    }
