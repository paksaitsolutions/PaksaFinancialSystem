"""
Journal Entry API Endpoints

This module provides API endpoints for managing journal entries.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from core.database import get_db
from core.deps import get_current_active_user
from modules.core_financials.accounting import (
    JournalEntryService,
    JournalEntry,
    JournalEntryLine,
    JournalEntryStatus,
    JournalEntryNotFoundException,
    InvalidJournalEntryException,
    InvalidAccountException,
    UnbalancedJournalEntryException,
    PeriodClosedException,
    InvalidPeriodException,
)
from modules.users.models import User

router = APIRouter()


@router.get("/", response_model=List[dict], summary="List journal entries")
async def list_journal_entries(
    skip: int = 0,
    limit: int = 100,
    status: Optional[JournalEntryStatus] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    reference: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve a list of journal entries with optional filtering.
    """
    with JournalEntryService(db) as service:
        entries = service.list_entries(
            skip=skip,
            limit=limit,
            status=status,
            start_date=start_date,
            end_date=end_date,
            reference=reference,
        )
        
        return [
            {
                "id": str(entry.id),
                "entry_date": entry.entry_date.isoformat(),
                "reference": entry.reference,
                "description": entry.description,
                "status": entry.status,
                "created_by": str(entry.created_by),
                "created_at": entry.created_at.isoformat(),
                "approved_by": str(entry.approved_by) if entry.approved_by else None,
                "approved_at": entry.approved_at.isoformat() if entry.approved_at else None,
                "total_debit": float(entry.total_debit) if hasattr(entry, 'total_debit') else 0.0,
                "total_credit": float(entry.total_credit) if hasattr(entry, 'total_credit') else 0.0,
                "line_count": len(entry.lines) if hasattr(entry, 'lines') else 0,
            }
            for entry in entries
        ]


@router.get("/{entry_id}", response_model=dict, summary="Get journal entry by ID")
async def get_journal_entry(
    entry_id: UUID,
    include_lines: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get a specific journal entry by ID.
    """
    with JournalEntryService(db) as service:
        try:
            entry = service.get_entry(entry_id, include_lines=include_lines)
            
            result = {
                "id": str(entry.id),
                "entry_date": entry.entry_date.isoformat(),
                "reference": entry.reference,
                "description": entry.description,
                "status": entry.status,
                "currency": entry.currency,
                "created_by": str(entry.created_by),
                "created_at": entry.created_at.isoformat(),
                "updated_at": entry.updated_at.isoformat(),
                "approved_by": str(entry.approved_by) if entry.approved_by else None,
                "approved_at": entry.approved_at.isoformat() if entry.approved_at else None,
                "posted_by": str(entry.posted_by) if entry.posted_by else None,
                "posted_at": entry.posted_at.isoformat() if entry.posted_at else None,
                "total_debit": float(entry.total_debit) if hasattr(entry, 'total_debit') else 0.0,
                "total_credit": float(entry.total_credit) if hasattr(entry, 'total_credit') else 0.0,
            }
            
            if include_lines and hasattr(entry, 'lines'):
                result["lines"] = [
                    {
                        "id": str(line.id),
                        "account_id": str(line.account_id),
                        "account_code": line.account_code if hasattr(line, 'account_code') else None,
                        "account_name": line.account_name if hasattr(line, 'account_name') else None,
                        "description": line.description,
                        "debit": float(line.debit) if line.debit else 0.0,
                        "credit": float(line.credit) if line.credit else 0.0,
                        "tax_code": line.tax_code,
                        "tax_amount": float(line.tax_amount) if line.tax_amount else 0.0,
                        "entity_type": line.entity_type,
                        "entity_id": str(line.entity_id) if line.entity_id else None,
                    }
                    for line in entry.lines
                ]
                
            return result
            
        except JournalEntryNotFoundException as e:
            raise HTTPException(status_code=404, detail=str(e))


@router.post("/", status_code=status.HTTP_201_CREATED, summary="Create a new journal entry")
async def create_journal_entry(
    entry_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new journal entry.
    
    Request body should include:
    - entry_date: Date of the entry (ISO format)
    - reference: Reference number/string
    - description: Description of the entry
    - currency: Currency code (default: USD)
    - lines: List of journal entry lines
      - account_id: UUID of the account
      - description: Line description
      - debit: Debit amount (must be 0 or positive)
      - credit: Credit amount (must be 0 or positive)
      - tax_code: Optional tax code
      - tax_amount: Optional tax amount
      - entity_type: Optional entity type (e.g., 'customer', 'vendor')
      - entity_id: Optional entity ID
    """
    with JournalEntryService(db) as service:
        try:
            # Create the journal entry
            entry = service.create_entry(
                entry_date=entry_data["entry_date"],
                reference=entry_data["reference"],
                description=entry_data["description"],
                currency=entry_data.get("currency", "USD"),
                created_by=current_user.id,
                lines=entry_data["lines"],
            )
            
            return {
                "id": str(entry.id),
                "entry_date": entry.entry_date.isoformat(),
                "reference": entry.reference,
                "status": entry.status,
                "message": "Journal entry created successfully"
            }
            
        except (InvalidJournalEntryException, UnbalancedJournalEntryException, 
                InvalidAccountException, PeriodClosedException) as e:
            raise HTTPException(status_code=400, detail=str(e))
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(status_code=400, detail="Database integrity error")


@router.post("/{entry_id}/post", status_code=200, summary="Post a journal entry")
async def post_journal_entry(
    entry_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Post a journal entry to update account balances.
    """
    with JournalEntryService(db) as service:
        try:
            entry = service.post_entry(entry_id, current_user.id)
            return {
                "id": str(entry.id),
                "status": entry.status,
                "posted_at": entry.posted_at.isoformat() if entry.posted_at else None,
                "message": "Journal entry posted successfully"
            }
            
        except JournalEntryNotFoundException as e:
            raise HTTPException(status_code=404, detail=str(e))
        except (InvalidJournalEntryException, PeriodClosedException) as e:
            raise HTTPException(status_code=400, detail=str(e))


@router.post("/{entry_id}/approve", status_code=200, summary="Approve a journal entry")
async def approve_journal_entry(
    entry_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Approve a journal entry (requires appropriate permissions).
    """
    # Check if user has permission to approve entries
    if not current_user.has_permission("approve_journal_entries"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to approve journal entries"
        )
    
    with JournalEntryService(db) as service:
        try:
            entry = service.approve_entry(entry_id, current_user.id)
            return {
                "id": str(entry.id),
                "status": entry.status,
                "approved_at": entry.approved_at.isoformat() if entry.approved_at else None,
                "message": "Journal entry approved successfully"
            }
            
        except JournalEntryNotFoundException as e:
            raise HTTPException(status_code=404, detail=str(e))
        except InvalidJournalEntryException as e:
            raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a journal entry")
async def delete_journal_entry(
    entry_id: UUID,
    force: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete a journal entry.
    
    Only draft or rejected entries can be deleted unless force=True.
    """
    with JournalEntryService(db) as service:
        try:
            service.delete_entry(entry_id, force=force)
            return None
            
        except JournalEntryNotFoundException as e:
            raise HTTPException(status_code=404, detail=str(e))
        except InvalidJournalEntryException as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e))
