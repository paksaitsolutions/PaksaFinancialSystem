"""
Service layer for Journal Entry management.
"""
from datetime import datetime, date
from typing import List, Optional, Tuple, Dict, Any

from decimal import Decimal
from sqlalchemy import func, and_, or_, select
from sqlalchemy.orm import Session, joinedload
from uuid import UUID, uuid4

from app.core.security import get_password_hash
from app.exceptions import (
from app.models.gl_models import (
from app.schemas.gl_schemas import (
from app.services.base import BaseService



    NotFoundException,
    ValidationException,
    BusinessRuleException
)
    JournalEntry,
    JournalEntryLine,
    JournalEntryStatus,
    ChartOfAccounts,
    AccountingPeriod,
    LedgerBalance
)
    JournalEntryCreate,
    JournalEntryUpdate,
    JournalEntryLineCreate,
    JournalEntryResponse,
    JournalEntryLineResponse,
    JournalEntrySearch
)

class JournalEntryService(BaseService):
    """Service for managing Journal Entries."""
    
    def __init__(self, db: Session):
        """  Init  ."""
        super().__init__(db, JournalEntry)
    
    def create_entry(
        """Create Entry."""
        self, 
        entry_data: JournalEntryCreate, 
        created_by: UUID
    ) -> JournalEntryResponse:
        """Create Entry."""
        """Create a new journal entry."""
        # Validate accounting period
        period = self._validate_accounting_period(entry_data.entry_date, entry_data.company_id)
        
        # Validate accounts and calculate totals
        total_debit, total_credit, lines = self._validate_journal_entry(entry_data.lines, entry_data.company_id)
        
        # Ensure debits equal credits
        if total_debit != total_credit:
            raise ValidationException(
                f"Debits ({total_debit}) do not equal credits ({total_credit})"
            )
        
        # Generate entry number if not provided
        if not entry_data.entry_number:
            entry_data.entry_number = self._generate_entry_number(entry_data.company_id)
        
        # Create the journal entry
        entry_dict = entry_data.dict(exclude={"lines"})
        entry_dict.update({
            "total_debit": total_debit,
            "total_credit": total_credit,
            "period_id": period.id if period else None,
            "created_by": created_by,
            "updated_by": created_by,
            "status": JournalEntryStatus.DRAFT
        })
        
        # Create the entry
        entry = JournalEntry(**entry_dict)
        self.db.add(entry)
        
        # Create the line items
        for line_data in lines:
            line = JournalEntryLine(
                journal_entry=entry,
                **line_data.dict(),
                created_by=created_by,
                updated_by=created_by
            )
            self.db.add(line)
        
        # If status is POSTED, update account balances
        if entry_data.status == JournalEntryStatus.POSTED:
            self._post_entry(entry, created_by)
        
        self.db.commit()
        self.db.refresh(entry)
        
        return self._get_entry_response(entry.id)
    
    def update_entry(
        """Update Entry."""
        self, 
        entry_id: UUID, 
        entry_data: JournalEntryUpdate, 
        updated_by: UUID
    ) -> JournalEntryResponse:
        """Update Entry."""
        """Update an existing journal entry."""
        entry = self.db.query(JournalEntry).get(entry_id)
        if not entry:
            raise NotFoundException(f"Journal entry {entry_id} not found")
        
        # Prevent modification of posted entries unless it's a status change
        if entry.status == JournalEntryStatus.POSTED and not entry_data.status:
            raise BusinessRuleException(
                "Posted entries cannot be modified. Create a reversing entry instead."
            )
        
        # If this is a status update to POSTED, post the entry
        if entry_data.status == JournalEntryStatus.POSTED:
            if entry.status != JournalEntryStatus.POSTED:  # Only if not already posted
                self._post_entry(entry, updated_by)
            # Don't update other fields when just changing status
            self.db.commit()
            return self._get_entry_response(entry_id)
        
        # For draft entries, update the entry
        if entry.status != JournalEntryStatus.DRAFT:
            raise BusinessRuleException("Only draft entries can be modified")
        
        # Validate accounting period if date is being updated
        if entry_data.entry_date:
            period = self._validate_accounting_period(entry_data.entry_date, entry.company_id)
            entry.period_id = period.id if period else None
        
        # Update entry fields
        update_data = entry_data.dict(exclude={"lines", "status"}, exclude_unset=True)
        for field, value in update_data.items():
            setattr(entry, field, value)
        
        # Update lines if provided
        if entry_data.lines is not None:
            # Delete existing lines
            self.db.query(JournalEntryLine).filter(
                JournalEntryLine.journal_entry_id == entry_id
            ).delete()
            
            # Validate and add new lines
            total_debit, total_credit, lines = self._validate_journal_entry(
                entry_data.lines, 
                entry.company_id
            )
            
            if total_debit != total_credit:
                raise ValidationException(
                    f"Debits ({total_debit}) do not equal credits ({total_credit})"
                )
            
            # Update entry totals
            entry.total_debit = total_debit
            entry.total_credit = total_credit
            
            # Add new lines
            for line_data in lines:
                line = JournalEntryLine(
                    journal_entry=entry,
                    **line_data.dict(),
                    created_by=updated_by,
                    updated_by=updated_by
                )
                self.db.add(line)
        
        entry.updated_by = updated_by
        entry.updated_at = datetime.utcnow()
        
        # Update status if provided
        if entry_data.status:
            entry.status = entry_data.status
            
            # If posting the entry, update account balances
            if entry_data.status == JournalEntryStatus.POSTED:
                self._post_entry(entry, updated_by)
        
        self.db.commit()
        self.db.refresh(entry)
        
        return self._get_entry_response(entry_id)
    
    def delete_entry(self, entry_id: UUID, deleted_by: UUID) -> bool:
        """Delete Entry."""
        """Delete a journal entry."""
        entry = self.db.query(JournalEntry).get(entry_id)
        if not entry:
            raise NotFoundException(f"Journal entry {entry_id} not found")
        
        # Only allow deletion of draft entries
        if entry.status != JournalEntryStatus.DRAFT:
            raise BusinessRuleException(
                "Only draft entries can be deleted. Create a reversing entry instead."
            )
        
        # Delete the entry (soft delete)
        entry.is_active = False
        entry.updated_by = deleted_by
        entry.updated_at = datetime.utcnow()
        
        # Soft delete associated lines
        self.db.query(JournalEntryLine).filter(
            JournalEntryLine.journal_entry_id == entry_id
        ).update({
            "is_active": False,
            "updated_by": deleted_by,
            "updated_at": datetime.utcnow()
        })
        
        self.db.commit()
        return True
    
    def get_entry(self, entry_id: UUID) -> JournalEntryResponse:
        """Get Entry."""
        """Get a journal entry by ID."""
        return self._get_entry_response(entry_id)
    
    def search_entries(
        """Search Entries."""
        self, 
        search_params: JournalEntrySearch,
        company_id: UUID
    ) -> Tuple[List[JournalEntryResponse], int]:
        """Search Entries."""
        """Search journal entries with pagination and filtering."""
        query = self.db.query(JournalEntry).filter(
            JournalEntry.company_id == company_id,
            JournalEntry.is_active == True
        )
        
        # Apply filters
        if search_params.status:
            query = query.filter(JournalEntry.status == search_params.status)
            
        if search_params.start_date:
            query = query.filter(JournalEntry.entry_date >= search_params.start_date)
            
        if search_params.end_date:
            query = query.filter(JournalEntry.entry_date <= search_params.end_date)
            
        if search_params.reference:
            query = query.filter(JournalEntry.reference.ilike(f"%{search_params.reference}%"))
            
        if search_params.memo:
            query = query.filter(JournalEntry.memo.ilike(f"%{search_params.memo}%"))
        
        # Get total count for pagination
        total = query.count()
        
        # Apply pagination
        query = query.order_by(JournalEntry.entry_date.desc())
        query = query.offset((search_params.page - 1) * search_params.page_size)
        query = query.limit(search_params.page_size)
        
        # Execute query
        entries = query.all()
        
        # Convert to response models
        entry_responses = [
            self._get_entry_response(entry.id) for entry in entries
        ]
        
        return entry_responses, total
    
    def reverse_entry(
        """Reverse Entry."""
        self, 
        entry_id: UUID, 
        reversal_date: date,
        reversal_reference: Optional[str] = None,
        created_by: UUID = None
    ) -> JournalEntryResponse:
        """Reverse Entry."""
        """Create a reversing journal entry."""
        original_entry = self.db.query(JournalEntry).get(entry_id)
        if not original_entry or not original_entry.is_active:
            raise NotFoundException(f"Journal entry {entry_id} not found")
        
        if original_entry.status != JournalEntryStatus.POSTED:
            raise BusinessRuleException("Only posted entries can be reversed")
        
        # Create reversal entry
        reversal_data = JournalEntryCreate(
            entry_date=reversal_date,
            reference=reversal_reference or f"REV-{original_entry.reference or original_entry.entry_number}",
            memo=f"Reversal of entry {original_entry.entry_number}",
            company_id=original_entry.company_id,
            is_reversing=True,
            status=JournalEntryStatus.POSTED,
            lines=[]
        )
        
        # Create reversed lines
        for line in original_entry.line_items:
            reversal_line = JournalEntryLineCreate(
                account_id=line.account_id,
                debit=line.credit,  # Swap debits and credits
                credit=line.debit,
                description=f"Reversal: {line.description or ''}",
                reference=line.reference,
                tracking_category_id=line.tracking_category_id
            )
            reversal_data.lines.append(reversal_line)
        
        # Create the reversal entry
        reversal_entry = self.create_entry(reversal_data, created_by)
        
        # Link the original and reversal entries
        original_entry.reversed_entry_id = reversal_entry.id
        self.db.commit()
        
        return reversal_entry
    
    def _post_entry(self, entry: JournalEntry, posted_by: UUID) -> None:
        """ Post Entry."""
        """Post a journal entry and update account balances."""
        if entry.status == JournalEntryStatus.POSTED:
            return  # Already posted
        
        # Update entry status
        entry.status = JournalEntryStatus.POSTED
        entry.posting_date = datetime.utcnow().date()
        entry.posted_by = posted_by
        
        # Update account balances
        for line in entry.line_items:
            self._update_account_balance(
                account_id=line.account_id,
                debit=line.debit,
                credit=line.credit,
                period_id=entry.period_id
            )
    
    def _update_account_balance(
        """ Update Account Balance."""
        self, 
        account_id: UUID, 
        debit: Decimal, 
        credit: Decimal,
        period_id: UUID
    ) -> None:
        """ Update Account Balance."""
        """Update the balance of an account for a specific period."""
        if debit == 0 and credit == 0:
            return  # No change
        
        # Find or create the ledger balance record
        balance = self.db.query(LedgerBalance).filter(
            LedgerBalance.account_id == account_id,
            LedgerBalance.period_id == period_id
        ).first()
        
        if not balance:
            # Get the previous period's closing balance
            prev_balance = self._get_previous_period_balance(account_id, period_id)
            
            # Create a new balance record
            balance = LedgerBalance(
                account_id=account_id,
                period_id=period_id,
                opening_balance=prev_balance,
                period_debit=Decimal('0'),
                period_credit=Decimal('0'),
                closing_balance=prev_balance
            )
            self.db.add(balance)
        
        # Update the balance
        balance.period_debit += debit
        balance.period_credit += credit
        balance.closing_balance = balance.opening_balance + balance.period_debit - balance.period_credit
    
    def _get_previous_period_balance(
        """ Get Previous Period Balance."""
        self, 
        account_id: UUID, 
        period_id: UUID
    ) -> Decimal:
        """ Get Previous Period Balance."""
        """Get the closing balance from the previous period."""
        # Get the current period to find the previous one
        current_period = self.db.query(AccountingPeriod).get(period_id)
        if not current_period:
            return Decimal('0')
        
        # Find the previous period
        prev_period = self.db.query(AccountingPeriod).filter(
            AccountingPeriod.company_id == current_period.company_id,
            AccountingPeriod.end_date < current_period.start_date,
            AccountingPeriod.is_closed == True
        ).order_by(AccountingPeriod.end_date.desc()).first()
        
        if not prev_period:
            # No previous period, get the account's opening balance
            account = self.db.query(ChartOfAccounts).get(account_id)
            return account.opening_balance if account else Decimal('0')
        
        # Get the balance from the previous period
        prev_balance = self.db.query(LedgerBalance).filter(
            LedgerBalance.account_id == account_id,
            LedgerBalance.period_id == prev_period.id
        ).first()
        
        return prev_balance.closing_balance if prev_balance else Decimal('0')
    
    def _validate_accounting_period(
        """ Validate Accounting Period."""
        self, 
        entry_date: date, 
        company_id: UUID
    ) -> Optional[AccountingPeriod]:
        """ Validate Accounting Period."""
        """Validate that the entry date falls within an open accounting period."""
        period = self.db.query(AccountingPeriod).filter(
            AccountingPeriod.company_id == company_id,
            AccountingPeriod.start_date <= entry_date,
            AccountingPeriod.end_date >= entry_date,
            AccountingPeriod.is_closed == False
        ).first()
        
        if not period:
            raise BusinessRuleException(
                f"No open accounting period found for date {entry_date}. "
                "Please check your accounting periods or create a new one."
            )
        
        return period
    
    def _validate_journal_entry(
        """ Validate Journal Entry."""
        self, 
        lines: List[JournalEntryLineCreate], 
        company_id: UUID
    ) -> Tuple[Decimal, Decimal, List[JournalEntryLineCreate]]:
        """ Validate Journal Entry."""
        """Validate journal entry lines and calculate totals."""
        if not lines or len(lines) < 2:
            raise ValidationException("Journal entry must have at least two lines")
        
        total_debit = Decimal('0')
        total_credit = Decimal('0')
        account_ids = set()
        
        # Validate each line
        for line in lines:
            # Validate account
            account = self.db.query(ChartOfAccounts).filter(
                ChartOfAccounts.id == line.account_id,
                ChartOfAccounts.company_id == company_id,
                ChartOfAccounts.is_active == True
            ).first()
            
            if not account:
                raise ValidationException(f"Invalid or inactive account ID: {line.account_id}")
            
            # Validate amounts
            if line.debit < 0 or line.credit < 0:
                raise ValidationException("Debit and credit amounts must be non-negative")
            
            if line.debit > 0 and line.credit > 0:
                raise ValidationException("A line cannot have both debit and credit amounts")
            
            if line.debit == 0 and line.credit == 0:
                raise ValidationException("A line must have either a debit or credit amount")
            
            # Update totals
            total_debit += line.debit
            total_credit += line.credit
            
            # Track account IDs for duplicate check
            account_ids.add(str(line.account_id))
        
        # Check for duplicate accounts (not allowed in the same entry)
        if len(account_ids) < len(lines):
            raise ValidationException("Duplicate accounts are not allowed in the same journal entry")
        
        return total_debit, total_credit, lines
    
    def _generate_entry_number(self, company_id: UUID) -> str:
        """ Generate Entry Number."""
        """Generate a unique journal entry number."""
        # Get the highest existing entry number for this company
        max_number = self.db.query(func.max(JournalEntry.entry_number)).filter(
            JournalEntry.company_id == company_id,
            JournalEntry.entry_number.like('JE-%')
        ).scalar()
        
        if max_number:
            try:
                # Extract the numeric part and increment
                number = int(max_number.split('-')[1]) + 1
                return f"JE-{number:06d}"
            except (IndexError, ValueError):
                pass
        
        # Default format if no entries exist yet or parsing failed
        return "JE-000001"
    
    def _get_entry_response(self, entry_id: UUID) -> JournalEntryResponse:
        """ Get Entry Response."""
        """Get a journal entry with its lines as a response model."""
        entry = self.db.query(JournalEntry).options(
            joinedload(JournalEntry.line_items)
        ).get(entry_id)
        
        if not entry or not entry.is_active:
            raise NotFoundException(f"Journal entry {entry_id} not found")
        
        # Convert to response model
        response = JournalEntryResponse.from_orm(entry)
        
        # Add line items
        response.lines = [
            JournalEntryLineResponse.from_orm(line) 
            for line in entry.line_items
            if line.is_active
        ]
        
        return response
