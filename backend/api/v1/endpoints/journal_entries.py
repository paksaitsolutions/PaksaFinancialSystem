"""
Journal Entries API Endpoints
"""
from typing import List, Optional
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.security import get_current_active_user
from schemas.user import User as UserSchema
from schemas.journal_entry import (
    JournalEntry,
    JournalEntryCreate,
    JournalEntryUpdate,
    JournalEntryStatus,
    JournalEntryFilter
)
from crud.journal_entry import crud_journal_entry
from core.exceptions import (
    NotFoundException,
    BadRequestException,
    ValidationException
)

router = APIRouter()

@router.get(
    "/",
    response_model=List[JournalEntry],
    summary="List Journal Entries"
)
async def read_journal_entries(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    status: Optional[JournalEntryStatus] = None,
    account_code: Optional[str] = None,
    reference: Optional[str] = None,
    is_adjusting: Optional[bool] = None,
    is_recurring: Optional[bool] = None,
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Retrieve journal entries with optional filtering.
    """
    # Build filter
    filters = JournalEntryFilter(
        start_date=start_date,
        end_date=end_date,
        status=status,
        account_code=account_code,
        reference=reference,
        is_adjusting=is_adjusting,
        is_recurring=is_recurring,
        created_by_id=current_user.id if not current_user.is_superuser else None
    )
    
    # Get journal entries
    entries, total = await crud_journal_entry.get_multi(
        db,
        skip=skip,
        limit=limit,
        filters=filters
    )
    
    return entries

@router.post(
    "/",
    response_model=JournalEntry,
    status_code=status.HTTP_201_CREATED,
    summary="Create Journal Entry"
)
async def create_journal_entry(
    *,
    db: AsyncSession = Depends(get_db),
    journal_entry_in: JournalEntryCreate,
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Create a new journal entry.
    """
    try:
        return await crud_journal_entry.create(
            db,
            obj_in=journal_entry_in,
            created_by_id=current_user.id
        )
    except (NotFoundException, ValidationException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the journal entry"
        )

@router.get(
    "/{entry_id}",
    response_model=JournalEntry,
    summary="Get Journal Entry by ID"
)
async def read_journal_entry(
    entry_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Get a specific journal entry by ID.
    """
    journal_entry = await crud_journal_entry.get_by_id(db, id=entry_id)
    
    if not journal_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Journal entry not found"
        )
    
    # Check permissions (only admin or creator can view)
    if not current_user.is_superuser and journal_entry.created_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return journal_entry

@router.put(
    "/{entry_id}",
    response_model=JournalEntry,
    summary="Update Journal Entry"
)
async def update_journal_entry(
    *,
    db: AsyncSession = Depends(get_db),
    entry_id: UUID,
    journal_entry_in: JournalEntryUpdate,
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Update a journal entry.
    """
    # Get the existing journal entry
    journal_entry = await crud_journal_entry.get_by_id(db, id=entry_id)
    
    if not journal_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Journal entry not found"
        )
    
    # Check permissions (only admin or creator can update)
    if not current_user.is_superuser and journal_entry.created_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    try:
        return await crud_journal_entry.update(
            db,
            db_obj=journal_entry,
            obj_in=journal_entry_in,
            updated_by_id=current_user.id
        )
    except (BadRequestException, ValidationException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the journal entry"
        )

@router.delete(
    "/{entry_id}",
    response_model=JournalEntry,
    summary="Delete Journal Entry"
)
async def delete_journal_entry(
    *,
    db: AsyncSession = Depends(get_db),
    entry_id: UUID,
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Delete a journal entry (soft delete).
    """
    # Get the existing journal entry
    journal_entry = await crud_journal_entry.get_by_id(db, id=entry_id)
    
    if not journal_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Journal entry not found"
        )
    
    # Check permissions (only admin or creator can delete)
    if not current_user.is_superuser and journal_entry.created_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    try:
        return await crud_journal_entry.delete(
            db,
            db_obj=journal_entry,
            deleted_by_id=current_user.id
        )
    except BadRequestException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the journal entry"
        )

@router.post(
    "/{entry_id}/post",
    response_model=JournalEntry,
    summary="Post Journal Entry"
)
async def post_journal_entry(
    *,
    db: AsyncSession = Depends(get_db),
    entry_id: UUID,
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Post a journal entry (change status to POSTED).
    """
    # Get the existing journal entry
    journal_entry = await crud_journal_entry.get_by_id(db, id=entry_id)
    
    if not journal_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Journal entry not found"
        )
    
    # Check permissions (only admin or creator can post)
    if not current_user.is_superuser and journal_entry.created_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    try:
        return await crud_journal_entry.post(
            db,
            db_obj=journal_entry,
            posted_by_id=current_user.id
        )
    except BadRequestException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while posting the journal entry"
        )

@router.get(
    "/account/{account_code}",
    response_model=List[JournalEntry],
    summary="Get Journal Entries by Account"
)
async def get_journal_entries_by_account(
    account_code: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Get journal entries for a specific account.
    """
    # Get account ID from code
    from crud.chart_of_accounts import crud_chart_of_accounts
    account = await crud_chart_of_accounts.get_by_code(db, code=account_code)
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account with code {account_code} not found"
        )
    
    # Get journal entries for this account
    entries, total = await crud_journal_entry.get_by_account(
        db,
        account_id=account.id,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )
    
    return entries
