"""
Recurring Journal Entry API endpoints.
"""
from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.schemas.gl_recurring_schemas import (
    RecurringJournalCreate,
    RecurringJournalResponse,
    RecurringJournalUpdate,
    RecurringJournalListResponse,
    RecurringJournalStatusEnum,
)
from app.services.gl_recurring_service import RecurringJournalService, process_due_recurring_entries

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
    
    This endpoint creates a template for journal entries that will be automatically
    generated according to the specified recurrence pattern.
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
    
    Returns the details of a recurring journal entry including its template data.
    """
    journal = RecurringJournalService.get_recurring_journal(
        db=db,
        journal_id=journal_id,
        company_id=current_user.company_id,
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
    status: Optional[RecurringJournalStatusEnum] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    List all recurring journal entries with optional filtering.
    
    Returns a paginated list of recurring journal entries that match the specified filters.
    """
    return RecurringJournalService.list_recurring_journals(
        db=db,
        company_id=current_user.company_id,
        status=status,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
    )


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
    
    Updates the recurrence pattern, status, or template data of a recurring journal entry.
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
    
    This performs a soft delete by marking the entry as cancelled.
    """
    RecurringJournalService.delete_recurring_journal(
        db=db,
        journal_id=journal_id,
        company_id=current_user.company_id,
    )
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
    
    This will generate the journal entry for the next occurrence immediately,
    regardless of the schedule.
    """
    try:
        success, error = RecurringJournalService.process_recurring_journal(
            db=db,
            journal_id=journal_id,
            company_id=current_user.company_id,
            user_id=current_user.id,
        )
        
        if error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error,
            )
            
        return {"message": "Recurring journal processed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/process-due-entries",
    status_code=status.HTTP_200_OK,
    summary="Process all due recurring journal entries",
    include_in_schema=False,  # Primarily for internal/scheduled use
)
def process_due_entries(
    company_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Process all recurring journal entries that are due.
    
    This endpoint is typically called by a scheduled task, but can also be
    triggered manually if needed.
    """
    # If no company_id provided, use the current user's company
    if company_id is None:
        company_id = current_user.company_id
    
    success_count, error_count = process_due_recurring_entries(db, company_id)
    
    return {
        "success_count": success_count,
        "error_count": error_count,
        "message": f"Processed {success_count} entries successfully" + 
                  (f" with {error_count} errors" if error_count > 0 else ""),
    }
