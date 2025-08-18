"""
Service layer for managing accounting periods and period closing.
"""
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID, uuid4

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, or_, select, update, delete

from app.exceptions import (
    NotFoundException,
    ValidationException,
    BusinessRuleException
)
from app.models.gl_models import (
    AccountingPeriod,
    JournalEntry,
    JournalEntryStatus,
    ChartOfAccounts,
    LedgerBalance,
    TrialBalance,
    TrialBalanceAccount
)
from app.schemas.gl_schemas import (
    AccountingPeriodCreate,
    AccountingPeriodUpdate,
    AccountingPeriodResponse,
    TrialBalanceCreate,
    TrialBalanceResponse
)
from app.services.base import BaseService

class PeriodService(BaseService):
    """Service for managing accounting periods and period closing."""
    
    def __init__(self, db: Session):
        super().__init__(db, AccountingPeriod)
    
    def create_period(
        self, 
        period_data: AccountingPeriodCreate, 
        created_by: UUID
    ) -> AccountingPeriodResponse:
        """Create a new accounting period."""
        # Check for date overlaps
        overlapping = self.db.query(AccountingPeriod).filter(
            AccountingPeriod.company_id == period_data.company_id,
            or_(
                # New period starts or ends within an existing period
                and_(
                    AccountingPeriod.start_date <= period_data.start_date,
                    AccountingPeriod.end_date >= period_data.start_date
                ),
                and_(
                    AccountingPeriod.start_date <= period_data.end_date,
                    AccountingPeriod.end_date >= period_data.end_date
                ),
                # New period completely contains an existing period
                and_(
                    AccountingPeriod.start_date >= period_data.start_date,
                    AccountingPeriod.end_date <= period_data.end_date
                )
            )
        ).first()
        
        if overlapping:
            raise ValidationException(
                f"Period overlaps with existing period: {overlapping.name} "
                f"({overlapping.start_date} to {overlapping.end_date})"
            )
        
        # Create the period
        period_dict = period_data.dict()
        period_dict["created_by"] = created_by
        period_dict["updated_by"] = created_by
        
        period = AccountingPeriod(**period_dict)
        self.db.add(period)
        self.db.commit()
        self.db.refresh(period)
        
        return AccountingPeriodResponse.from_orm(period)
    
    def close_period(
        self, 
        period_id: UUID, 
        closed_by: UUID,
        force: bool = False
    ) -> AccountingPeriodResponse:
        """Close an accounting period."""
        period = self.db.query(AccountingPeriod).get(period_id)
        if not period:
            raise NotFoundException(f"Period {period_id} not found")
        
        if period.is_closed:
            return AccountingPeriodResponse.from_orm(period)
        
        # Check for unposted journal entries in the period
        unposted_entries = self.db.query(JournalEntry).filter(
            JournalEntry.period_id == period_id,
            JournalEntry.status != JournalEntryStatus.POSTED
        ).count()
        
        if unposted_entries > 0 and not force:
            raise BusinessRuleException(
                f"Cannot close period with {unposted_entries} unposted journal entries. "
                "Post or delete these entries before closing the period."
            )
        
        # Update the period
        period.is_closed = True
        period.close_date = datetime.utcnow()
        period.closed_by_id = closed_by
        period.updated_at = datetime.utcnow()
        period.updated_by = closed_by
        
        # Generate trial balance if not exists
        trial_balance = self.db.query(TrialBalance).filter(
            TrialBalance.company_id == period.company_id,
            TrialBalance.as_of_date == period.end_date
        ).first()
        
        if not trial_balance:
            trial_balance = self._generate_trial_balance(
                company_id=period.company_id,
                as_of_date=period.end_date,
                period_id=period.id,
                created_by=closed_by
            )
        
        self.db.commit()
        self.db.refresh(period)
        
        return AccountingPeriodResponse.from_orm(period)
    
    def reopen_period(
        self, 
        period_id: UUID, 
        updated_by: UUID
    ) -> AccountingPeriodResponse:
        """Reopen a closed accounting period."""
        period = self.db.query(AccountingPeriod).get(period_id)
        if not period:
            raise NotFoundException(f"Period {period_id} not found")
        
        if not period.is_closed:
            return AccountingPeriodResponse.from_orm(period)
        
        # Check if there are any subsequent closed periods
        subsequent_period = self.db.query(AccountingPeriod).filter(
            AccountingPeriod.company_id == period.company_id,
            AccountingPeriod.start_date > period.end_date,
            AccountingPeriod.is_closed == True
        ).first()
        
        if subsequent_period and not force:
            raise BusinessRuleException(
                "Cannot reopen a period when subsequent periods are already closed. "
                "Reopen periods in chronological order."
            )
        
        # Update the period
        period.is_closed = False
        period.close_date = None
        period.closed_by_id = None
        period.updated_at = datetime.utcnow()
        period.updated_by = updated_by
        
        self.db.commit()
        self.db.refresh(period)
        
        return AccountingPeriodResponse.from_orm(period)
    
    def _generate_trial_balance(
        self,
        company_id: UUID,
        as_of_date: date,
        period_id: UUID,
        created_by: UUID
    ) -> TrialBalance:
        """Generate a trial balance for a specific date."""
        # Get all accounts with their balances
        account_balances = self.db.query(
            ChartOfAccounts.id,
            func.coalesce(func.sum(JournalEntryLine.debit), 0).label("total_debit"),
            func.coalesce(func.sum(JournalEntryLine.credit), 0).label("total_credit")
        ).join(
            JournalEntryLine,
            ChartOfAccounts.id == JournalEntryLine.account_id
        ).join(
            JournalEntry,
            JournalEntryLine.journal_entry_id == JournalEntry.id
        ).filter(
            ChartOfAccounts.company_id == company_id,
            ChartOfAccounts.is_active == True,
            JournalEntry.status == JournalEntryStatus.POSTED,
            JournalEntry.entry_date <= as_of_date
        ).group_by(ChartOfAccounts.id).all()
        
        # Create the trial balance
        trial_balance = TrialBalance(
            name=f"Trial Balance as of {as_of_date}",
            as_of_date=as_of_date,
            period_id=period_id,
            company_id=company_id,
            is_posted=True,
            posted_at=datetime.utcnow(),
            posted_by_id=created_by,
            created_by=created_by,
            updated_by=created_by
        )
        
        self.db.add(trial_balance)
        self.db.flush()  # Get the trial_balance.id
        
        # Add account balances
        for account_id, total_debit, total_credit in account_balances:
            if total_debit > 0 or total_credit > 0:
                tb_account = TrialBalanceAccount(
                    trial_balance_id=trial_balance.id,
                    account_id=account_id,
                    debit_balance=total_debit,
                    credit_balance=total_credit,
                    created_by=created_by,
                    updated_by=created_by
                )
                self.db.add(tb_account)
        
        # Update ledger balances for the period
        self._update_ledger_balances(company_id, as_of_date, created_by)
        
        return trial_balance
    
    def _update_ledger_balances(
        self,
        company_id: UUID,
        as_of_date: date,
        updated_by: UUID
    ) -> None:
        """Update ledger balances for all accounts up to the given date."""
        # Get all active accounts
        accounts = self.db.query(ChartOfAccounts).filter(
            ChartOfAccounts.company_id == company_id,
            ChartOfAccounts.is_active == True
        ).all()
        
        for account in accounts:
            # Calculate period totals
            period_totals = self.db.query(
                func.coalesce(func.sum(JournalEntryLine.debit), 0).label("total_debit"),
                func.coalesce(func.sum(JournalEntryLine.credit), 0).label("total_credit")
            ).join(
                JournalEntry,
                JournalEntryLine.journal_entry_id == JournalEntry.id
            ).filter(
                JournalEntryLine.account_id == account.id,
                JournalEntry.status == JournalEntryStatus.POSTED,
                JournalEntry.entry_date <= as_of_date
            ).first()
            
            if not period_totals:
                continue
                
            total_debit, total_credit = period_totals
            
            # Get or create ledger balance
            ledger_balance = self.db.query(LedgerBalance).filter(
                LedgerBalance.account_id == account.id,
                LedgerBalance.period_id == None,  # Current period
                LedgerBalance.company_id == company_id
            ).first()
            
            if not ledger_balance:
                ledger_balance = LedgerBalance(
                    account_id=account.id,
                    company_id=company_id,
                    period_id=None,  # Current period
                    opening_balance=0,  # Will be set from previous period
                    period_debit=0,
                    period_credit=0,
                    closing_balance=0,
                    created_by=updated_by,
                    updated_by=updated_by
                )
                self.db.add(ledger_balance)
            
            # Update balances
            ledger_balance.period_debit = total_debit
            ledger_balance.period_credit = total_credit
            
            # Calculate closing balance based on account type
            if account.account_type in ["asset", "expense"]:
                ledger_balance.closing_balance = (
                    ledger_balance.opening_balance + 
                    total_debit - 
                    total_credit
                )
            else:  # liability, equity, revenue
                ledger_balance.closing_balance = (
                    ledger_balance.opening_balance - 
                    total_debit + 
                    total_credit
                )
            
            ledger_balance.updated_at = datetime.utcnow()
            ledger_balance.updated_by = updated_by
        
        self.db.commit()

    def get_period_by_date(
        self,
        company_id: UUID,
        target_date: date,
        create_if_missing: bool = False,
        created_by: Optional[UUID] = None
    ) -> Optional[AccountingPeriod]:
        """Get the accounting period for a specific date."""
        period = self.db.query(AccountingPeriod).filter(
            AccountingPeriod.company_id == company_id,
            AccountingPeriod.start_date <= target_date,
            AccountingPeriod.end_date >= target_date
        ).first()
        
        if not period and create_if_missing and created_by:
            # Create a new period (e.g., for the current month)
            period_name = target_date.strftime("%B %Y")
            start_date = date(target_date.year, target_date.month, 1)
            
            if target_date.month == 12:
                end_date = date(target_date.year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = date(
                    target_date.year, 
                    target_date.month + 1, 
                    1
                ) - timedelta(days=1)
            
            period_data = AccountingPeriodCreate(
                name=period_name,
                start_date=start_date,
                end_date=end_date,
                company_id=company_id
            )
            
            return self.create_period(period_data, created_by)
        
        return period
