"""
Paksa Financial System
Journal Entry Service

This module provides services for managing journal entries in the general ledger.
"""
from datetime import datetime, date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Optional, Tuple, Union, Any
from uuid import UUID, uuid4

from dateutil.relativedelta import relativedelta
from sqlalchemy import and_, or_, func, case, text
from sqlalchemy.orm import Session, joinedload

from ...base.service import BaseService
from ..exceptions import (
    JournalEntryNotFoundException,
    InvalidJournalEntryException,
    PeriodClosedException,
    InvalidAccountException,
    InvalidAmountException,
    UnbalancedJournalEntryException,
    JournalEntryAlreadyPostedException,
    JournalEntryNotPostedException,
    JournalEntryAlreadyReversedException,
    InvalidRecurringEntryException
)
from ..models import (
    JournalEntry,
    JournalEntryLine,
    JournalEntryStatus,
    JournalEntryType,
    GLPeriod,
    Account,
    AccountType
)
from .gl_period_service import GLPeriodService


class JournalEntryService(BaseService):
    """Service for managing journal entries and related operations."""
    
    def __init__(self, db: Session):
        """Initialize the service with a database session."""
        super().__init__(db)
        self.period_service = GLPeriodService(db)
    
    def create_journal_entry(
        self,
        entry_date: date,
        lines: List[Dict[str, Any]],
        entry_type: Union[JournalEntryType, str] = JournalEntryType.STANDARD,
        reference: Optional[str] = None,
        description: Optional[str] = None,
        is_recurring: bool = False,
        recurring_frequency: Optional[str] = None,
        recurring_end_date: Optional[date] = None,
        created_by: Optional[UUID] = None,
        **kwargs
    ) -> JournalEntry:
        """
        Create a new journal entry.
        
        Args:
            entry_date: The effective date of the journal entry
            lines: List of journal entry lines
            entry_type: Type of journal entry (default: STANDARD)
            reference: Optional reference number or code
            description: Optional description of the journal entry
            is_recurring: Whether this is a recurring journal entry
            recurring_frequency: Frequency of recurrence (e.g., 'monthly', 'quarterly')
            recurring_end_date: End date for recurring entries
            created_by: ID of the user creating the journal entry
            **kwargs: Additional fields to set on the journal entry
            
        Returns:
            The created JournalEntry object
            
        Raises:
            InvalidJournalEntryException: If the journal entry is invalid
            UnbalancedJournalEntryException: If debits don't equal credits
            PeriodClosedException: If the period for the entry date is closed
            InvalidAccountException: If any account is invalid
        """
        # Convert string enum values if needed
        if isinstance(entry_type, str):
            try:
                entry_type = JournalEntryType(entry_type.lower())
            except ValueError as e:
                raise InvalidJournalEntryException(f"Invalid journal entry type: {entry_type}") from e
        
        # Validate entry date
        if entry_date > date.today() and entry_type != JournalEntryType.ADJUSTING:
            raise InvalidJournalEntryException("Cannot post to future dates except for adjusting entries")
        
        # Check if period is open for the entry date
        if not self.period_service.is_period_open(entry_date):
            raise PeriodClosedException(f"The period for {entry_date} is closed")
        
        # Create the journal entry
        journal_entry = JournalEntry(
            entry_number=self._generate_entry_number(),
            reference=reference,
            description=description,
            type=entry_type,
            status=JournalEntryStatus.DRAFT,
            entry_date=entry_date,
            is_recurring=is_recurring,
            recurring_frequency=recurring_frequency if is_recurring else None,
            recurring_end_date=recurring_end_date if is_recurring else None,
            next_recurring_date=self._calculate_next_recurring_date(
                entry_date, 
                recurring_frequency
            ) if is_recurring and recurring_frequency else None,
            created_by=created_by,
            updated_by=created_by,
            **kwargs
        )
        
        # Add lines to the journal entry
        total_debit = Decimal('0.00')
        total_credit = Decimal('0.00')
        
        for i, line in enumerate(lines, 1):
            amount = Decimal(str(line['amount'])).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            is_debit = line.get('is_debit', False)
            
            # Validate account
            account = self._validate_account(line.get('account_id'))
            
            # Create journal entry line
            entry_line = JournalEntryLine(
                line_number=i,
                account_id=account.id,
                description=line.get('description'),
                amount=amount,
                is_debit=is_debit,
                allocation_id=line.get('allocation_id'),
                allocation_type=line.get('allocation_type'),
                currency_code=line.get('currency_code'),
                exchange_rate=line.get('exchange_rate', Decimal('1.0')),
                foreign_amount=line.get('foreign_amount'),
                tax_code=line.get('tax_code'),
                tax_amount=line.get('tax_amount'),
                metadata_=line.get('metadata', {})
            )
            
            # Update totals
            if is_debit:
                total_debit += amount
            else:
                total_credit += amount
            
            journal_entry.lines.append(entry_line)
        
        # Validate that debits equal credits
        if total_debit != total_credit:
            raise UnbalancedJournalEntryException(
                f"Debits ({total_debit}) do not equal credits ({total_credit})"
            )
        
        # Set totals
        journal_entry.total_debit = total_debit
        journal_entry.total_credit = total_credit
        
        # Save to database
        self.db.add(journal_entry)
        self.db.commit()
        self.db.refresh(journal_entry)
        
        return journal_entry
    
    def post_journal_entry(self, entry_id: UUID, posted_by: UUID) -> JournalEntry:
        """
        Post a draft journal entry.
        
        Args:
            entry_id: The ID of the journal entry to post
            posted_by: ID of the user posting the entry
            
        Returns:
            The updated JournalEntry object
            
        Raises:
            JournalEntryNotFoundException: If the journal entry doesn't exist
            JournalEntryAlreadyPostedException: If the entry is already posted
            PeriodClosedException: If the period is closed
        """
        journal_entry = self._get_journal_entry(entry_id)
        
        if journal_entry.status == JournalEntryStatus.POSTED:
            raise JournalEntryAlreadyPostedException("Journal entry is already posted")
        
        if journal_entry.status == JournalEntryStatus.VOIDED:
            raise InvalidJournalEntryException("Cannot post a voided journal entry")
        
        # Check if period is open for the entry date
        if not self.period_service.is_period_open(journal_entry.entry_date):
            raise PeriodClosedException(
                f"The period for {journal_entry.entry_date} is closed"
            )
        
        # Update journal entry
        journal_entry.status = JournalEntryStatus.POSTED
        journal_entry.posted_at = datetime.utcnow()
        journal_entry.updated_by = posted_by
        
        # Set the period if not already set
        if not journal_entry.period_id:
            period = self.period_service.get_period_for_date(journal_entry.entry_date)
            if period:
                journal_entry.period_id = period.id
        
        self.db.commit()
        self.db.refresh(journal_entry)
        
        return journal_entry
    
    def reverse_journal_entry(
        self, 
        entry_id: UUID, 
        reversal_date: Optional[date] = None,
        reversal_description: Optional[str] = None,
        reversed_by: Optional[UUID] = None
    ) -> JournalEntry:
        """
        Reverse a posted journal entry.
        
        Args:
            entry_id: The ID of the journal entry to reverse
            reversal_date: The date for the reversal entry (defaults to today)
            reversal_description: Optional description for the reversal entry
            reversed_by: ID of the user performing the reversal
            
        Returns:
            The reversal JournalEntry object
            
        Raises:
            JournalEntryNotFoundException: If the journal entry doesn't exist
            JournalEntryNotPostedException: If the entry is not posted
            JournalEntryAlreadyReversedException: If the entry is already reversed
            PeriodClosedException: If the period is closed
        """
        if reversal_date is None:
            reversal_date = date.today()
        
        # Get the original journal entry
        original_entry = self._get_journal_entry(entry_id)
        
        if original_entry.status != JournalEntryStatus.POSTED:
            raise JournalEntryNotPostedException("Only posted journal entries can be reversed")
        
        if original_entry.reversed_entry_id:
            raise JournalEntryAlreadyReversedException("This entry has already been reversed")
        
        # Check if period is open for the reversal date
        if not self.period_service.is_period_open(reversal_date):
            raise PeriodClosedException(f"The period for {reversal_date} is closed")
        
        # Create reversal lines (flip debits and credits)
        reversal_lines = []
        for line in original_entry.lines:
            reversal_lines.append({
                'account_id': line.account_id,
                'description': line.description,
                'amount': line.amount,
                'is_debit': not line.is_debit,  # Flip debit/credit
                'allocation_id': line.allocation_id,
                'allocation_type': line.allocation_type,
                'currency_code': line.currency_code,
                'exchange_rate': line.exchange_rate,
                'foreign_amount': line.foreign_amount,
                'tax_code': line.tax_code,
                'tax_amount': line.tax_amount,
                'metadata': line.metadata_
            })
        
        # Create the reversal entry
        reversal_entry = self.create_journal_entry(
            entry_date=reversal_date,
            lines=reversal_lines,
            entry_type=JournalEntryType.REVERSING,
            reference=f"REV-{original_entry.entry_number}",
            description=reversal_description or f"Reversal of {original_entry.entry_number}",
            created_by=reversed_by,
            reversed_entry_id=original_entry.id
        )
        
        # Post the reversal entry
        self.post_journal_entry(reversal_entry.id, reversed_by)
        
        # Update the original entry
        original_entry.reversed_at = datetime.utcnow()
        original_entry.updated_by = reversed_by
        original_entry.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(original_entry)
        
        return reversal_entry
    
    def get_journal_entry(self, entry_id: UUID) -> JournalEntry:
        """
        Get a journal entry by ID.
        
        Args:
            entry_id: The ID of the journal entry to retrieve
            
        Returns:
            The JournalEntry object
            
        Raises:
            JournalEntryNotFoundException: If the journal entry doesn't exist
        """
        return self._get_journal_entry(entry_id)
    
    def list_journal_entries(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status: Optional[Union[JournalEntryStatus, str]] = None,
        entry_type: Optional[Union[JournalEntryType, str]] = None,
        account_id: Optional[UUID] = None,
        reference: Optional[str] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """
        List journal entries with optional filtering and pagination.
        
        Args:
            start_date: Filter entries on or after this date
            end_date: Filter entries on or before this date
            status: Filter by entry status
            entry_type: Filter by entry type
            account_id: Filter by account ID
            reference: Filter by reference (partial match)
            page: Page number (1-based)
            page_size: Number of items per page
            
        Returns:
            Dictionary containing the list of journal entries and pagination info
        """
        query = self.db.query(JournalEntry).options(joinedload(JournalEntry.lines))
        
        # Apply filters
        if start_date:
            query = query.filter(JournalEntry.entry_date >= start_date)
        
        if end_date:
            query = query.filter(JournalEntry.entry_date <= end_date)
        
        if status:
            if isinstance(status, str):
                status = JournalEntryStatus(status.lower())
            query = query.filter(JournalEntry.status == status)
        
        if entry_type:
            if isinstance(entry_type, str):
                entry_type = JournalEntryType(entry_type.lower())
            query = query.filter(JournalEntry.type == entry_type)
        
        if account_id:
            query = query.join(JournalEntry.lines).filter(JournalEntryLine.account_id == account_id)
        
        if reference:
            query = query.filter(JournalEntry.reference.ilike(f"%{reference}%"))
        
        # Get total count for pagination
        total = query.count()
        
        # Apply pagination
        query = query.order_by(JournalEntry.entry_date.desc(), JournalEntry.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        # Execute query
        entries = query.all()
        
        return {
            'items': entries,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }
    
    def _get_journal_entry(self, entry_id: UUID) -> JournalEntry:
        """
        Internal method to get a journal entry by ID.
        
        Args:
            entry_id: The ID of the journal entry to retrieve
            
        Returns:
            The JournalEntry object
            
        Raises:
            JournalEntryNotFoundException: If the journal entry doesn't exist
        """
        journal_entry = (
            self.db.query(JournalEntry)
            .options(joinedload(JournalEntry.lines))
            .filter(JournalEntry.id == entry_id)
            .first()
        )
        
        if not journal_entry:
            raise JournalEntryNotFoundException(f"Journal entry with ID {entry_id} not found")
        
        return journal_entry
    
    def _generate_entry_number(self) -> str:
        """
        Generate a unique journal entry number.
        
        Returns:
            A unique journal entry number
        """
        # Format: JE-YYYYMMDD-XXXXX
        prefix = f"JE-{datetime.utcnow().strftime('%Y%m%d')}"
        
        # Get the highest sequence number for today
        last_entry = (
            self.db.query(JournalEntry)
            .filter(JournalEntry.entry_number.startswith(prefix))
            .order_by(JournalEntry.entry_number.desc())
            .first()
        )
        
        if last_entry:
            # Extract the sequence number and increment
            try:
                seq = int(last_entry.entry_number.split('-')[-1])
                seq += 1
            except (IndexError, ValueError):
                seq = 1
        else:
            seq = 1
        
        return f"{prefix}-{seq:05d}"
    
    def _calculate_next_recurring_date(
        self, 
        last_date: date, 
        frequency: str
    ) -> Optional[date]:
        """
        Calculate the next recurring date based on frequency.
        
        Args:
            last_date: The last occurrence date
            frequency: The frequency of recurrence (daily, weekly, monthly, quarterly, yearly)
            
        Returns:
            The next occurrence date, or None if frequency is invalid
        """
        if not frequency:
            return None
            
        frequency = frequency.lower()
        
        if frequency == 'daily':
            return last_date + timedelta(days=1)
        elif frequency == 'weekly':
            return last_date + timedelta(weeks=1)
        elif frequency == 'monthly':
            return last_date + relativedelta(months=1)
        elif frequency == 'quarterly':
            return last_date + relativedelta(months=3)
        elif frequency == 'yearly':
            return last_date + relativedelta(years=1)
        else:
            return None
    
    def _validate_account(self, account_id: Optional[UUID]) -> Account:
        """
        Validate that an account exists and is active.
        
        Args:
            account_id: The ID of the account to validate
            
        Returns:
            The Account object if valid
            
        Raises:
            InvalidAccountException: If the account is invalid or inactive
        """
        if not account_id:
            raise InvalidAccountException("Account ID is required")
        
        account = self.db.get(Account, account_id)
        
        if not account:
            raise InvalidAccountException(f"Account with ID {account_id} not found")
        
        if account.status != 'active':
            raise InvalidAccountException(f"Account {account.code} is not active")
        
        return account
