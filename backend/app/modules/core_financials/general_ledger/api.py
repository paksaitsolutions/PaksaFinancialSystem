"""
General Ledger API endpoints.
"""
from datetime import date
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from app.modules.core_financials.general_ledger.services import AccountService, JournalEntryService
from app.modules.core_financials.general_ledger.schemas import (
    AccountCreate, AccountUpdate, AccountResponse,
    JournalEntryCreate, JournalEntryResponse,
    TrialBalanceResponse, TrialBalanceItem
)

router = APIRouter()
account_service = AccountService()
journal_service = JournalEntryService()

# Account endpoints
@router.post("/accounts/", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    account: AccountCreate,
    db: AsyncSession = Depends(get_db)
):
    # Check if account code already exists
    existing = await account_service.get_by_code(db, account.account_code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account code already exists"
        )
    return await account_service.create(db, obj_in=account)

@router.get("/accounts/", response_model=List[AccountResponse])
async def get_accounts(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    return await account_service.get_multi(db, skip=skip, limit=limit)

@router.get("/accounts/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: int,
    db: AsyncSession = Depends(get_db)
):
    account = await account_service.get(db, account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    return account

@router.put("/accounts/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: int,
    account_update: AccountUpdate,
    db: AsyncSession = Depends(get_db)
):
    account = await account_service.get(db, account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    return await account_service.update(db, db_obj=account, obj_in=account_update)

@router.get("/chart-of-accounts/", response_model=List[AccountResponse])
async def get_chart_of_accounts(db: AsyncSession = Depends(get_db)):
    return await account_service.get_chart_of_accounts(db)

# Journal Entry endpoints
@router.post("/journal-entries/", response_model=JournalEntryResponse, status_code=status.HTTP_201_CREATED)
async def create_journal_entry(
    journal_entry: JournalEntryCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        return await journal_service.create_journal_entry(db, entry_data=journal_entry)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/journal-entries/", response_model=List[JournalEntryResponse])
async def get_journal_entries(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    return await journal_service.get_multi(db, skip=skip, limit=limit)

@router.get("/journal-entries/{entry_id}", response_model=JournalEntryResponse)
async def get_journal_entry(
    entry_id: int,
    db: AsyncSession = Depends(get_db)
):
    entry = await journal_service.get(db, entry_id)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Journal entry not found"
        )
    return entry

# Reports
@router.get("/reports/trial-balance", response_model=TrialBalanceResponse)
async def get_trial_balance(
    as_of_date: date,
    db: AsyncSession = Depends(get_db)
):
    trial_balance_items = await journal_service.get_trial_balance(db, as_of_date)
    total_debits = sum(item.debit_balance for item in trial_balance_items)
    total_credits = sum(item.credit_balance for item in trial_balance_items)
    
    return TrialBalanceResponse(
        as_of_date=as_of_date,
        accounts=trial_balance_items,
        total_debits=total_debits,
        total_credits=total_credits
    )