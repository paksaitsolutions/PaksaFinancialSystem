"""Enhanced General Ledger API endpoints with comprehensive functionality"""
from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.modules.core_financials.general_ledger.services import AccountService, JournalEntryService
from app.modules.core_financials.general_ledger.schemas import (
    AccountCreate, AccountUpdate, AccountResponse,
    JournalEntryCreate, JournalEntryResponse,
    TrialBalanceResponse
)

router = APIRouter(prefix="/gl", tags=["General Ledger"])
account_service = AccountService()
journal_service = JournalEntryService()

# Enhanced Account endpoints
@router.get("/accounts", response_model=List[AccountResponse])
async def get_accounts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    account_type: Optional[str] = Query(None),
    active_only: bool = Query(True),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get accounts with filtering and pagination"""
    return await account_service.get_accounts_filtered(
        db, skip=skip, limit=limit, account_type=account_type, 
        active_only=active_only, search=search
    )

@router.post("/accounts", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    account: AccountCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new GL account"""
    existing = await account_service.get_by_code(db, account.account_code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account code already exists"
        )
    return await account_service.create(db, obj_in=account)

@router.get("/accounts/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get account by ID"""
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
    """Update account"""
    account = await account_service.get(db, account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    return await account_service.update(db, db_obj=account, obj_in=account_update)

@router.delete("/accounts/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    account_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete account (soft delete)"""
    account = await account_service.get(db, account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    await account_service.soft_delete(db, account_id)

# Enhanced Journal Entry endpoints
@router.get("/journal-entries", response_model=List[JournalEntryResponse])
async def get_journal_entries(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_filter: Optional[str] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get journal entries with filtering"""
    return await journal_service.get_journal_entries_filtered(
        db, skip=skip, limit=limit, status_filter=status_filter,
        date_from=date_from, date_to=date_to
    )

@router.post("/journal-entries", response_model=JournalEntryResponse, status_code=status.HTTP_201_CREATED)
async def create_journal_entry(
    journal_entry: JournalEntryCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new journal entry"""
    try:
        return await journal_service.create_journal_entry(db, entry_data=journal_entry)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/journal-entries/{entry_id}", response_model=JournalEntryResponse)
async def get_journal_entry(
    entry_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get journal entry by ID"""
    entry = await journal_service.get_with_lines(db, entry_id)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Journal entry not found"
        )
    return entry

@router.post("/journal-entries/{entry_id}/post", response_model=JournalEntryResponse)
async def post_journal_entry(
    entry_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Post a journal entry"""
    try:
        return await journal_service.post_entry(db, entry_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/journal-entries/{entry_id}/unpost", response_model=JournalEntryResponse)
async def unpost_journal_entry(
    entry_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Unpost a journal entry"""
    try:
        return await journal_service.unpost_entry(db, entry_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/journal-entries/{entry_id}/reverse", response_model=JournalEntryResponse)
async def reverse_journal_entry(
    entry_id: int,
    reversal_date: date,
    reason: str,
    db: AsyncSession = Depends(get_db)
):
    """Reverse a journal entry"""
    try:
        return await journal_service.reverse_entry(db, entry_id, reversal_date, reason)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# Reports endpoints
@router.get("/reports/trial-balance", response_model=TrialBalanceResponse)
async def get_trial_balance(
    as_of_date: date = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """Generate trial balance report"""
    trial_balance_items = await journal_service.get_trial_balance(db, as_of_date)
    total_debits = sum(item.debit_balance for item in trial_balance_items)
    total_credits = sum(item.credit_balance for item in trial_balance_items)
    
    return TrialBalanceResponse(
        as_of_date=as_of_date,
        accounts=trial_balance_items,
        total_debits=total_debits,
        total_credits=total_credits
    )

@router.get("/reports/account-balance/{account_id}")
async def get_account_balance(
    account_id: int,
    as_of_date: date = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """Get account balance as of specific date"""
    balance = await journal_service.get_account_balance(db, account_id, as_of_date)
    return {"account_id": account_id, "balance": balance, "as_of_date": as_of_date}

@router.get("/reports/gl-summary")
async def get_gl_summary(
    date_from: date = Query(...),
    date_to: date = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """Get GL summary report"""
    return await journal_service.get_gl_summary(db, date_from, date_to)

@router.get("/reports/gl-detail")
async def get_gl_detail(
    account_id: Optional[int] = Query(None),
    date_from: date = Query(...),
    date_to: date = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """Get GL detail report"""
    return await journal_service.get_gl_detail(db, account_id, date_from, date_to)