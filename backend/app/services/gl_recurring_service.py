"""
Services for managing recurring journal entries and allocation rules.
"""
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple

from decimal import Decimal, InvalidOperation
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from uuid import UUID, uuid4

from app.core.config import settings
from app.core.logging import logger
from app.models import gl_recurring_models as models
from app.schemas import gl_recurring_schemas as schemas
from app.services import gl_service





class RecurringJournalService:
    """Service for managing recurring journal entries."""
    
    @staticmethod
    def create_recurring_journal(
        """Create Recurring Journal."""
        db: Session, 
        journal_data: schemas.RecurringJournalCreate,
        company_id: UUID,
        user_id: UUID
    ) -> models.RecurringJournalEntry:
        """Create Recurring Journal."""
        """Create a new recurring journal entry template."""
        # Validate the recurrence pattern
        next_run_date = RecurringJournalService._calculate_next_run_date(
            journal_data.frequency,
            journal_data.interval,
            journal_data.start_date,
            datetime.now().date()
        )
        
        if not next_run_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid recurrence pattern"
            )
            
        # Create the recurring journal entry
        db_journal = models.RecurringJournalEntry(
            **journal_data.dict(exclude={"template_data"}),
            company_id=company_id,
            created_by=user_id,
            next_run_date=next_run_date,
            status=models.RecurringJournalStatus.ACTIVE
        )
        
        db.add(db_journal)
        db.flush()  # Get the ID for the template
        
        # Create the template
        template = models.RecurringJournalTemplate(
            recurring_journal_id=db_journal.id,
            template_data=journal_data.template_data
        )
        
        db.add(template)
        db.commit()
        db.refresh(db_journal)
        
        return db_journal
    
    @staticmethod
    def update_recurring_journal(
        """Update Recurring Journal."""
        db: Session,
        journal_id: UUID,
        journal_data: schemas.RecurringJournalUpdate,
        company_id: UUID
    ) -> models.RecurringJournalEntry:
        """Update Recurring Journal."""
        """Update an existing recurring journal entry."""
        db_journal = db.query(models.RecurringJournalEntry).filter(
            models.RecurringJournalEntry.id == journal_id,
            models.RecurringJournalEntry.company_id == company_id
        ).first()
        
        if not db_journal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recurring journal entry not found"
            )
            
        # Update fields
        update_data = journal_data.dict(exclude_unset=True, exclude={"template_data"})
        
        # If frequency or interval changed, recalculate next run date
        if "frequency" in update_data or "interval" in update_data:
            frequency = update_data.get("frequency", db_journal.frequency)
            interval = update_data.get("interval", db_journal.interval)
            start_date = update_data.get("start_date", db_journal.start_date)
            
            next_run_date = RecurringJournalService._calculate_next_run_date(
                frequency,
                interval,
                start_date,
                datetime.now().date()
            )
            
            if next_run_date:
                update_data["next_run_date"] = next_run_date
        
        # Update the journal entry
        for field, value in update_data.items():
            setattr(db_journal, field, value)
            
        # Update the template if needed
        if journal_data.template_data is not None:
            if not db_journal.template:
                template = models.RecurringJournalTemplate(
                    recurring_journal_id=db_journal.id,
                    template_data=journal_data.template_data
                )
                db.add(template)
            else:
                db_journal.template.template_data = journal_data.template_data
        
        db.commit()
        db.refresh(db_journal)
        return db_journal
    
    @staticmethod
    def process_due_entries(db: Session, company_id: UUID = None) -> Tuple[int, int]:
        """Process Due Entries."""
        """Process all recurring journal entries that are due.
        
        Args:
            db: Database session
            company_id: If provided, only process entries for this company
            
        Returns:
            Tuple of (success_count, error_count)
        """
        today = datetime.now().date()
        success_count = 0
        error_count = 0
        
        # Find all active recurring journal entries that are due
        query = db.query(models.RecurringJournalEntry).filter(
            models.RecurringJournalEntry.status == models.RecurringJournalStatus.ACTIVE,
            models.RecurringJournalEntry.next_run_date <= today
        )
        
        if company_id:
            query = query.filter(models.RecurringJournalEntry.company_id == company_id)
            
        due_entries = query.options(joinedload(models.RecurringJournalEntry.template)).all()
        
        for entry in due_entries:
            try:
                # Generate the journal entry
                journal_data = schemas.JournalEntryCreate(
                    **entry.template.template_data,
                    transaction_date=entry.next_run_date,
                    reference=f"Recurring: {entry.name} - {entry.next_run_date}",
                    is_recurring=True
                )
                
                # Create the journal entry
                gl_service.JournalService.create_journal_entry(
                    db=db,
                    journal_data=journal_data,
                    company_id=entry.company_id,
                    user_id=entry.created_by,
                    recurring_journal_id=entry.id
                )
                
                # Update the recurring entry
                entry.last_run_date = entry.next_run_date
                entry.total_occurrences += 1
                
                # Check if we've reached the end
                if entry.end_type == models.RecurrenceEndType.AFTER_OCCURRENCES and \
                   entry.total_occurrences >= (entry.end_after_occurrences or 0):
                    entry.status = models.RecurringJournalStatus.COMPLETED
                elif entry.end_type == models.RecurrenceEndType.ON_DATE and \
                     entry.end_date and entry.next_run_date >= entry.end_date:
                    entry.status = models.RecurringJournalStatus.COMPLETED
                else:
                    # Calculate next run date
                    next_run = entry.calculate_next_run(entry.next_run_date)
                    if next_run:
                        entry.next_run_date = next_run
                    else:
                        entry.status = models.RecurringJournalStatus.COMPLETED
                
                success_count += 1
                
            except Exception as e:
                logger.error(f"Error processing recurring journal {entry.id}: {str(e)}", exc_info=True)
                error_count += 1
                
        db.commit()
        return success_count, error_count
    
    @staticmethod
    def _calculate_next_run_date(
        """ Calculate Next Run Date."""
        frequency: models.RecurrenceFrequency,
        interval: int,
        start_date: date,
        current_date: date
    ) -> Optional[date]:
        """ Calculate Next Run Date."""
        """Calculate the next run date based on frequency and interval."""
        if start_date > current_date:
            return start_date
            
        delta = None
        
        if frequency == models.RecurrenceFrequency.DAILY:
            delta = timedelta(days=1 * interval)
        elif frequency == models.RecurrenceFrequency.WEEKLY:
            delta = timedelta(weeks=1 * interval)
        elif frequency == models.RecurrenceFrequency.BIWEEKLY:
            delta = timedelta(weeks=2 * interval)
        elif frequency == models.RecurrenceFrequency.MONTHLY:
            # Handle month arithmetic
            months = interval
            year = current_date.year + (current_date.month + months - 1) // 12
            month = (current_date.month + months - 1) % 12 + 1
            day = min(start_date.day, 28)  # Handle months with fewer days
            
            try:
                next_date = current_date.replace(year=year, month=month, day=day)
                if next_date <= current_date:
                    # Move to next interval
                    next_date = current_date.replace(day=1)  # First day of current month
                    next_date = next_date.replace(month=next_date.month + months)
                    # Handle year rollover
                    if next_date.month > 12:
                        next_date = next_date.replace(year=next_date.year + 1, month=next_date.month - 12)
                    next_date = next_date.replace(day=min(day, (next_date.replace(month=next_date.month % 12 + 1, day=1) - timedelta(days=1)).day))
                return next_date
            except ValueError:
                # Handle invalid dates (e.g., Feb 30)
                next_date = (current_date.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
                return next_date
        elif frequency == models.RecurrenceFrequency.QUARTERLY:
            months = 3 * interval
            return RecurringJournalService._add_months(start_date, months, current_date)
        elif frequency == models.RecurrenceFrequency.SEMI_ANNUALLY:
            months = 6 * interval
            return RecurringJournalService._add_months(start_date, months, current_date)
        elif frequency == models.RecurrenceFrequency.ANNUALLY:
            months = 12 * interval
            return RecurringJournalService._add_months(start_date, months, current_date)
        
        # For unsupported frequencies, return None
        if not delta:
            return None
            
        # For daily/weekly frequencies, calculate the next occurrence
        next_date = start_date
        while next_date <= current_date:
            next_date += delta
            
        return next_date
    
    @staticmethod
    def _add_months(start_date: date, months: int, current_date: date) -> date:
        """ Add Months."""
        """Add months to a date, handling year rollover and month-end dates."""
        year = start_date.year + (start_date.month + months - 1) // 12
        month = (start_date.month + months - 1) % 12 + 1
        
        # Handle month-end dates
        try:
            next_date = start_date.replace(year=year, month=month)
        except ValueError:
            # Handle invalid dates (e.g., Feb 30)
            next_date = (start_date.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
        # If we haven't reached the next occurrence yet, move to the next interval
        while next_date <= current_date:
            year = next_date.year + (next_date.month + months - 1) // 12
            month = (next_date.month + months - 1) % 12 + 1
            
            try:
                next_date = next_date.replace(year=year, month=month)
            except ValueError:
                # Handle invalid dates (e.g., Feb 30)
                next_date = (next_date.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
                
        return next_date


class AllocationService:
    """Service for managing allocation rules."""
    
    @staticmethod
    def create_allocation_rule(
        """Create Allocation Rule."""
        db: Session,
        rule_data: schemas.AllocationRuleCreate,
        company_id: UUID
    ) -> models.AllocationRule:
        """Create Allocation Rule."""
        """Create a new allocation rule."""
        # Validate the allocation method
        if rule_data.allocation_method == "percentage":
            total_percent = sum(d.percentage or 0 for d in rule_data.destinations)
            if abs(total_percent - 100) > 0.01:  # Allow for floating point errors
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Total percentage must be 100%"
                )
        elif rule_data.allocation_method == "fixed":
            # No validation needed for fixed amounts
            pass
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid allocation method: {rule_data.allocation_method}"
            )
            
        # Create the allocation rule
        db_rule = models.AllocationRule(
            **rule_data.dict(exclude={"destinations"}),
            company_id=company_id
        )
        
        db.add(db_rule)
        db.flush()  # Get the ID for the destinations
        
        # Create the destinations
        for dest_data in rule_data.destinations:
            dest = models.AllocationDestination(
                allocation_rule_id=db_rule.id,
                **dest_data.dict()
            )
            db.add(dest)
            
        db.commit()
        db.refresh(db_rule)
        return db_rule
    
    @staticmethod
    def update_allocation_rule(
        """Update Allocation Rule."""
        db: Session,
        rule_id: UUID,
        rule_data: schemas.AllocationRuleUpdate,
        company_id: UUID
    ) -> models.AllocationRule:
        """Update Allocation Rule."""
        """Update an existing allocation rule."""
        db_rule = db.query(models.AllocationRule).filter(
            models.AllocationRule.id == rule_id,
            models.AllocationRule.company_id == company_id
        ).first()
        
        if not db_rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Allocation rule not found"
            )
            
        # If destinations are being updated, validate them
        if rule_data.destinations is not None:
            if rule_data.allocation_method == "percentage":
                total_percent = sum(d.percentage or 0 for d in rule_data.destinations)
                if abs(total_percent - 100) > 0.01:  # Allow for floating point errors
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Total percentage must be 100%"
                    )
        
        # Update the rule
        update_data = rule_data.dict(exclude_unset=True, exclude={"destinations"})
        for field, value in update_data.items():
            setattr(db_rule, field, value)
            
        # Update destinations if provided
        if rule_data.destinations is not None:
            # Delete existing destinations
            db.query(models.AllocationDestination).filter(
                models.AllocationDestination.allocation_rule_id == db_rule.id
            ).delete()
            
            # Add new destinations
            for dest_data in rule_data.destinations:
                dest = models.AllocationDestination(
                    allocation_rule_id=db_rule.id,
                    **dest_data.dict()
                )
                db.add(dest)
                
        db.commit()
        db.refresh(db_rule)
        return db_rule
    
    @staticmethod
    def apply_allocation_rule(
        """Apply Allocation Rule."""
        db: Session,
        rule_id: UUID,
        amount: Decimal,
        company_id: UUID
    ) -> List[Dict[str, Any]]:
        """Apply Allocation Rule."""
        """Apply an allocation rule to an amount."""
        db_rule = db.query(models.AllocationRule).filter(
            models.AllocationRule.id == rule_id,
            models.AllocationRule.company_id == company_id
        ).options(joinedload(models.AllocationRule.destinations)).first()
        
        if not db_rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Allocation rule not found"
            )
            
        if not db_rule.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Allocation rule is not active"
            )
            
        try:
            return db_rule.allocate_amount(amount)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )


# Add a function to process all due recurring entries (for scheduled tasks)
def process_due_recurring_entries(db: Session, company_id: UUID = None) -> Dict[str, int]:
    """Process Due Recurring Entries."""
    """Process all due recurring journal entries.
    
    This function is designed to be called from a scheduled task.
    
    Args:
        db: Database session
        company_id: If provided, only process entries for this company
        
    Returns:
        Dictionary with success and error counts
    """
    success_count, error_count = RecurringJournalService.process_due_entries(db, company_id)
    
    return {
        "success_count": success_count,
        "error_count": error_count
    }
