"""
Account Balance API Endpoints

This module provides API endpoints for managing and retrieving account balances.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.deps import get_current_active_user
from modules.core_financials.accounting import (
    AccountBalanceService,
    AccountBalanceNotFoundException,
    InvalidDateRangeException,
    PeriodAlreadyClosedException,
    PeriodNotClosedException,
    InvalidBalancePeriodException,
)
from modules.users.models import User

router = APIRouter()


@router.get("/{account_id}", summary="Get account balance as of a specific date")
async def get_account_balance(
    account_id: UUID,
    as_of: Optional[datetime] = Query(
        None,
        description="Date to get the balance as of. Defaults to current date/time if not provided.",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get the current balance of an account.
    
    Args:
        account_id: The ID of the account
        as_of: Optional date to get the balance as of
        
    Returns:
        The account balance information
    """
    with AccountBalanceService(db) as service:
        try:
            balance = service.get_balance_as_of(account_id, as_of)
            return {
                "account_id": account_id,
                "as_of": as_of or datetime.utcnow(),
                "balance": float(balance),
                "currency": "USD",  # TODO: Get from account
            }
        except AccountBalanceNotFoundException as e:
            raise HTTPException(status_code=404, detail=str(e))
        except (InvalidDateRangeException, InvalidBalancePeriodException) as e:
            raise HTTPException(status_code=400, detail=str(e))


@router.get("/{account_id}/period", summary="Get account balance for a specific period")
async def get_account_balance_for_period(
    account_id: UUID,
    start_date: datetime = Query(..., description="Start of the period"),
    end_date: Optional[datetime] = Query(
        None, description="End of the period. Defaults to now if not provided."
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get the balance details for an account over a specific period.
    
    Args:
        account_id: The ID of the account
        start_date: Start of the period
        end_date: End of the period (defaults to now)
        
    Returns:
        Detailed balance information for the period
    """
    with AccountBalanceService(db) as service:
        try:
            balance_info = service.get_balance_for_period(account_id, start_date, end_date)
            # Convert Decimal to float for JSON serialization
            for key, value in balance_info.items():
                if hasattr(value, 'isoformat'):  # For datetime objects
                    balance_info[key] = value.isoformat()
                elif isinstance(value, Decimal):
                    balance_info[key] = float(value)
            return balance_info
        except (AccountBalanceNotFoundException, InvalidDateRangeException) as e:
            raise HTTPException(status_code=400, detail=str(e))


@router.post("/periods/close", summary="Close an accounting period")
async def close_accounting_period(
    period_end: datetime = Query(..., description="End date of the period to close"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Close an accounting period by creating balance records for all accounts.
    
    Args:
        period_end: End date of the period to close
        
    Returns:
        List of created account balance records
    """
    # Check if user has permission to close periods
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to close accounting periods"
        )
    
    with AccountBalanceService(db) as service:
        try:
            balances = service.close_period(period_end)
            return [
                {
                    "account_id": str(balance.account_id),
                    "period_start": balance.period_start.isoformat(),
                    "period_end": balance.period_end.isoformat() if balance.period_end else None,
                    "opening_balance": float(balance.opening_balance),
                    "period_debit": float(balance.period_debit),
                    "period_credit": float(balance.period_credit),
                    "closing_balance": float(balance.closing_balance),
                }
                for balance in balances
            ]
        except (PeriodAlreadyClosedException, InvalidDateRangeException) as e:
            raise HTTPException(status_code=400, detail=str(e))
