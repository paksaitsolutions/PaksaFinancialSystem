"""
API endpoints for managing recurring journal entries and allocation rules.
"""
from datetime import date, datetime
from typing import Any, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.services.gl_recurring_service import (
    RecurringJournalService, 
    AllocationService
)

router = APIRouter()

# Recurring Journal Entries
@router.post("/recurring-journals/", response_model=schemas.RecurringJournal, status_code=status.HTTP_201_CREATED)
def create_recurring_journal(
    *,
    db: Session = Depends(deps.get_db),
    journal_in: schemas.RecurringJournalCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create a new recurring journal entry.
    """
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with a company",
        )
        
    try:
        journal = RecurringJournalService.create_recurring_journal(
            db=db,
            journal_data=journal_in,
            company_id=current_user.company_id,
            user_id=current_user.id
        )
        return journal
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/recurring-journals/", response_model=List[schemas.RecurringJournal])
def list_recurring_journals(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[schemas.RecurringJournalStatus] = None,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve recurring journal entries.
    """
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with a company",
        )
    
    query = db.query(models.RecurringJournalEntry).filter(
        models.RecurringJournalEntry.company_id == current_user.company_id
    )
    
    if status:
        query = query.filter(models.RecurringJournalEntry.status == status)
    
    journals = query.offset(skip).limit(limit).all()
    return journals


@router.get("/recurring-journals/{journal_id}", response_model=schemas.RecurringJournal)
def get_recurring_journal(
    *,
    db: Session = Depends(deps.get_db),
    journal_id: UUID,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get a specific recurring journal entry by ID.
    """
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with a company",
        )
    
    journal = db.query(models.RecurringJournalEntry).filter(
        models.RecurringJournalEntry.id == journal_id,
        models.RecurringJournalEntry.company_id == current_user.company_id
    ).first()
    
    if not journal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurring journal entry not found",
        )
    
    return journal


@router.put("/recurring-journals/{journal_id}", response_model=schemas.RecurringJournal)
def update_recurring_journal(
    *,
    db: Session = Depends(deps.get_db),
    journal_id: UUID,
    journal_in: schemas.RecurringJournalUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a recurring journal entry.
    """
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with a company",
        )
    
    try:
        journal = RecurringJournalService.update_recurring_journal(
            db=db,
            journal_id=journal_id,
            journal_data=journal_in,
            company_id=current_user.company_id
        )
        return journal
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/recurring-journals/{journal_id}", response_model=schemas.RecurringJournal)
def delete_recurring_journal(
    *,
    db: Session = Depends(deps.get_db),
    journal_id: UUID,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a recurring journal entry.
    """
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with a company",
        )
    
    journal = db.query(models.RecurringJournalEntry).filter(
        models.RecurringJournalEntry.id == journal_id,
        models.RecurringJournalEntry.company_id == current_user.company_id
    ).first()
    
    if not journal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurring journal entry not found",
        )
    
    # Soft delete by marking as cancelled
    journal.status = schemas.RecurringJournalStatus.CANCELLED
    
    db.add(journal)
    db.commit()
    db.refresh(journal)
    
    return journal


@router.post("/recurring-journals/{journal_id}/process", response_model=schemas.JournalEntry)
def process_recurring_journal(
    *,
    db: Session = Depends(deps.get_db),
    journal_id: UUID,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Manually process a recurring journal entry to create a new journal entry.
    """
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with a company",
        )
    
    journal = db.query(models.RecurringJournalEntry).filter(
        models.RecurringJournalEntry.id == journal_id,
        models.RecurringJournalEntry.company_id == current_user.company_id
    ).first()
    
    if not journal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurring journal entry not found",
        )
    
    if journal.status != schemas.RecurringJournalStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only active recurring journal entries can be processed",
        )
    
    # Process the recurring entry
    success_count, error_count = RecurringJournalService.process_due_entries(
        db=db,
        company_id=current_user.company_id
    )
    
    if error_count > 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process recurring journal entry: {error_count} errors occurred",
        )
    
    # Get the most recent journal entry created by this recurring entry
    journal_entry = db.query(models.JournalEntry).filter(
        models.JournalEntry.recurring_journal_id == journal_id
    ).order_by(models.JournalEntry.created_at.desc()).first()
    
    if not journal_entry:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create journal entry",
        )
    
    return journal_entry


# Allocation Rules
@router.post("/allocation-rules/", response_model=schemas.AllocationRule, status_code=status.HTTP_201_CREATED)
def create_allocation_rule(
    *,
    db: Session = Depends(deps.get_db),
    rule_in: schemas.AllocationRuleCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create a new allocation rule.
    """
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with a company",
        )
    
    try:
        rule = AllocationService.create_allocation_rule(
            db=db,
            rule_data=rule_in,
            company_id=current_user.company_id
        )
        return rule
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/allocation-rules/", response_model=List[schemas.AllocationRule])
def list_allocation_rules(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve allocation rules.
    """
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with a company",
        )
    
    query = db.query(models.AllocationRule).filter(
        models.AllocationRule.company_id == current_user.company_id
    ).options(
        # Eager load the destinations
        db.joinedload(models.AllocationRule.destinations)
    )
    
    if is_active is not None:
        query = query.filter(models.AllocationRule.is_active == is_active)
    
    rules = query.offset(skip).limit(limit).all()
    return rules


@router.get("/allocation-rules/{rule_id}", response_model=schemas.AllocationRule)
def get_allocation_rule(
    *,
    db: Session = Depends(deps.get_db),
    rule_id: UUID,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get a specific allocation rule by ID.
    """
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with a company",
        )
    
    rule = db.query(models.AllocationRule).filter(
        models.AllocationRule.id == rule_id,
        models.AllocationRule.company_id == current_user.company_id
    ).options(
        db.joinedload(models.AllocationRule.destinations)
    ).first()
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Allocation rule not found",
        )
    
    return rule


@router.put("/allocation-rules/{rule_id}", response_model=schemas.AllocationRule)
def update_allocation_rule(
    *,
    db: Session = Depends(deps.get_db),
    rule_id: UUID,
    rule_in: schemas.AllocationRuleUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an allocation rule.
    """
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with a company",
        )
    
    try:
        rule = AllocationService.update_allocation_rule(
            db=db,
            rule_id=rule_id,
            rule_data=rule_in,
            company_id=current_user.company_id
        )
        return rule
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/allocation-rules/{rule_id}", response_model=schemas.AllocationRule)
def delete_allocation_rule(
    *,
    db: Session = Depends(deps.get_db),
    rule_id: UUID,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an allocation rule.
    """
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with a company",
        )
    
    rule = db.query(models.AllocationRule).filter(
        models.AllocationRule.id == rule_id,
        models.AllocationRule.company_id == current_user.company_id
    ).first()
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Allocation rule not found",
        )
    
    # Delete the rule
    db.delete(rule)
    db.commit()
    
    return rule


@router.post("/allocation-rules/{rule_id}/apply", response_model=List[schemas.AllocationResult])
def apply_allocation_rule(
    *,
    db: Session = Depends(deps.get_db),
    rule_id: UUID,
    allocation_in: schemas.ApplyAllocationRule,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Apply an allocation rule to an amount.
    """
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with a company",
        )
    
    try:
        results = AllocationService.apply_allocation_rule(
            db=db,
            rule_id=rule_id,
            amount=allocation_in.amount,
            company_id=current_user.company_id
        )
        
        # Format the results
        formatted_results = []
        for result in results:
            formatted_results.append({
                "account_id": result["account_id"],
                "amount": result["amount"],
                "description": allocation_in.description or result.get("description"),
                "reference": allocation_in.reference or result.get("reference"),
            })
            
        return formatted_results
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# Scheduled Tasks
@router.post("/process-due-recurring-entries/", include_in_schema=False)
def process_due_recurring_entries(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Process all due recurring journal entries.
    
    This endpoint is intended to be called by a scheduled task and requires superuser privileges.
    """
    from app.services.gl_recurring_service import process_due_recurring_entries as process_entries
    
    try:
        result = process_entries(db=db)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process recurring entries: {str(e)}",
        )
