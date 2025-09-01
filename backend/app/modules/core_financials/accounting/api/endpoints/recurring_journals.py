"""
Recurring Journal Entry API endpoints.
"""
from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.user import User
from app.schemas.gl_recurring_schemas import (
    RecurringJournalCreate,
    RecurringJournalResponse,
    RecurringJournalUpdate,
    RecurringJournalListResponse,
)
from app.services.gl_recurring_service import RecurringJournalService

router = APIRouter(prefix="/recurring-journals", tags=["Recurring Journal Entries"])


@router.post(
    "/",
    response_model=RecurringJournalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new recurring journal entry",
)
def create_recurring_journal(
    journal_data: RecurringJournalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new recurring journal entry template.
    """
    try:
        return RecurringJournalService.create_recurring_journal(
            db=db,
            journal_data=journal_data,
            company_id=current_user.company_id,
            user_id=current_user.id,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/{journal_id}",
    response_model=RecurringJournalResponse,
    summary="Get a recurring journal entry by ID",
)
def get_recurring_journal(
    journal_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get a specific recurring journal entry by ID.
    """
    journal = (
        db.query(RecurringJournalEntry)
        .filter(
            RecurringJournalEntry.id == journal_id,
            RecurringJournalEntry.company_id == current_user.company_id,
        )
        .first()
    )
    
    if not journal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurring journal entry not found",
        )
    
    return journal


@router.get(
    "/",
    response_model=RecurringJournalListResponse,
    summary="List all recurring journal entries",
)
def list_recurring_journals(
    status: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    page: int = 1,
    page_size: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    List all recurring journal entries with optional filtering.
    """
    query = db.query(RecurringJournalEntry).filter(
        RecurringJournalEntry.company_id == current_user.company_id
    )
    
    if status:
        query = query.filter(RecurringJournalEntry.status == status)
    
    if start_date:
        query = query.filter(RecurringJournalEntry.start_date >= start_date)
    
    if end_date:
        query = query.filter(RecurringJournalEntry.next_run_date <= end_date)
    
    total = query.count()
    items = (
        query.order_by(RecurringJournalEntry.next_run_date.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.put(
    "/{journal_id}",
    response_model=RecurringJournalResponse,
    summary="Update a recurring journal entry",
)
def update_recurring_journal(
    journal_id: UUID,
    journal_data: RecurringJournalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update an existing recurring journal entry.
    """
    try:
        return RecurringJournalService.update_recurring_journal(
            db=db,
            journal_id=journal_id,
            journal_data=journal_data,
            company_id=current_user.company_id,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete(
    "/{journal_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a recurring journal entry",
)
def delete_recurring_journal(
    journal_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete a recurring journal entry.
    """
    journal = (
        db.query(RecurringJournalEntry)
        .filter(
            RecurringJournalEntry.id == journal_id,
            RecurringJournalEntry.company_id == current_user.company_id,
        )
        .first()
    )
    
    if not journal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurring journal entry not found",
        )
    
    # Soft delete by updating status
    journal.status = "cancelled"
    db.commit()
    
    return None


@router.post(
    "/{journal_id}/process",
    status_code=status.HTTP_200_OK,
    summary="Process a recurring journal entry manually",
)
def process_recurring_journal(
    journal_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Manually process a recurring journal entry.
    """
    try:
        success_count, error_count = RecurringJournalService.process_due_entries(
            db=db,
            company_id=current_user.company_id,
        )
        
        return {
            "success_count": success_count,
            "error_count": error_count,
            "message": f"Processed {success_count} entries successfully" + (
                f" with {error_count} errors" if error_count > 0 else ""
            ),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
