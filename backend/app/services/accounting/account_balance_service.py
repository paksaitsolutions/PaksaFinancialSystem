<<<<<<< HEAD:backend/app/modules/core_financials/accounting/services/account_balance_service.py
"""
Paksa Financial System 
Account Balance Service

This module provides services for managing and calculating account balances,
including real-time and historical balance calculations.
"""
from datetime import datetime, timedelta, date
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Tuple, Union, Any
from uuid import UUID

from dateutil.relativedelta import relativedelta
from sqlalchemy import and_, case, func, or_, select, text
from sqlalchemy.orm import Session, aliased

from core.database import SessionLocal
from ..exceptions import (
    AccountNotFoundException,
    InvalidDateRangeException,
    PeriodAlreadyClosedException,
    PeriodNotClosedException,
    InvalidBalancePeriodException,
)
from ..models import (
    Account,
    AccountBalance,
    AccountType,
    JournalEntry,
    JournalEntryLine,
    JournalEntryStatus,
)


class AccountBalanceService:
    """Service for managing account balances and related operations."""
    
    def __init__(self, db: Optional[Session] = None):
        """Initialize the service with an optional database session."""
        self.db = db or SessionLocal()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close the session if we created it."""
        if self.db and not self.db.bind:
            self.db.close()
    
    def get_account(self, account_id: UUID) -> Account:
        """Get an account by ID, raising an exception if not found."""
        account = self.db.get(Account, account_id)
        if not account:
            raise AccountNotFoundException(account_id)
        return account
    
    def get_balance_as_of(self, account_id: UUID, as_of_date: datetime = None) -> Decimal:
        """
        Get the balance of an account as of a specific date.
        
        This method calculates the balance by considering:
        1. The most recent balance snapshot (if any)
        2. All transactions after the snapshot date up to as_of_date
        
        Args:
            account_id: The ID of the account
            as_of_date: The date to calculate the balance for (defaults to now)
            
        Returns:
            Decimal: The account balance as of the specified date
            
        Raises:
            AccountNotFoundException: If the account doesn't exist
            InvalidDateRangeException: If the date range is invalid
        """
        if as_of_date is None:
            as_of_date = datetime.utcnow()
            
        # Get the account to verify it exists and get its type
        account = self.get_account(account_id)
        
        # Find the most recent balance snapshot before or on as_of_date
        latest_snapshot = self.db.query(AccountBalance).filter(
            AccountBalance.account_id == account_id,
            AccountBalance.period_end <= as_of_date
        ).order_by(AccountBalance.period_end.desc()).first()
        
        # Calculate the starting point for transaction aggregation
        if latest_snapshot:
            start_date = latest_snapshot.period_end
            running_balance = latest_snapshot.closing_balance
        else:
            # No snapshot found, start from the beginning of time
            start_date = datetime.min
            running_balance = Decimal('0.00')
        
        # Calculate the net effect of all transactions between start_date and as_of_date
        # This is a simplified version - in a real implementation, you'd want to optimize this
        # for performance, especially for accounts with many transactions
        query = self.db.query(
            func.sum(
                case(
                    [
                        (JournalEntryLine.is_debit == True, JournalEntryLine.amount),  # noqa: E712
                        (JournalEntryLine.is_debit == False, -JournalEntryLine.amount)  # noqa: E712
                    ],
                    else_=0
                )
            ).label('net_effect')
        ).join(
            JournalEntry,
            JournalEntry.id == JournalEntryLine.journal_entry_id
        ).filter(
            JournalEntryLine.account_id == account_id,
            JournalEntry.status == JournalEntryStatus.POSTED,
            JournalEntry.posted_at > start_date,
            JournalEntry.posted_at <= as_of_date
        )
        
        net_effect = query.scalar() or Decimal('0.00')
        balance = running_balance + net_effect
        
        # For contra accounts, we need to flip the sign
        if account.is_contra:
            balance = -balance
            
        return balance.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
    def get_balance_for_period(
        self,
        account_id: UUID,
        start_date: datetime,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get detailed balance information for an account over a specific period.
        
        Args:
            account_id: The ID of the account
            start_date: Start of the period
            end_date: End of the period (defaults to now)
            
        Returns:
            Dict containing:
                - opening_balance: Balance at start_date
                - closing_balance: Balance at end_date
                - period_debit: Total debits during the period
                - period_credit: Total credits during the period
                - transactions: List of transactions in the period
                
        Raises:
            AccountNotFoundException: If the account doesn't exist
            InvalidDateRangeException: If the date range is invalid
        """
        if end_date is None:
            end_date = datetime.utcnow()
            
        if start_date > end_date:
            raise InvalidDateRangeException("Start date must be before end date")
            
        # Get the account to verify it exists and get its type
        account = self.get_account(account_id)
        
        # Get the opening balance (as of start_date)
        opening_balance = self.get_balance_as_of(account_id, start_date)
        
        # Get the closing balance (as of end_date)
        closing_balance = self.get_balance_as_of(account_id, end_date)
        
        # Get the period transactions
        period_transactions = self.db.query(
            JournalEntryLine,
            JournalEntry.reference,
            JournalEntry.entry_date,
            JournalEntry.posted_at
        ).join(
            JournalEntry,
            JournalEntry.id == JournalEntryLine.journal_entry_id
        ).filter(
            JournalEntryLine.account_id == account_id,
            JournalEntry.status == JournalEntryStatus.POSTED,
            JournalEntry.posted_at > start_date,
            JournalEntry.posted_at <= end_date
        ).order_by(JournalEntry.posted_at).all()
        
        # Calculate period totals
        period_debit = Decimal('0.00')
        period_credit = Decimal('0.00')
        
        transactions = []
        for line, ref, entry_date, posted_at in period_transactions:
            if line.is_debit:
                period_debit += line.amount
            else:
                period_credit += line.amount
                
            transactions.append({
                'id': str(line.id),
                'journal_entry_id': str(line.journal_entry_id),
                'reference': ref,
                'entry_date': entry_date.isoformat(),
                'posted_at': posted_at.isoformat(),
                'description': line.description,
                'amount': float(line.amount),
                'is_debit': line.is_debit,
                'entity_type': line.entity_type,
                'entity_id': str(line.entity_id) if line.entity_id else None,
            })
        
        return {
            'account_id': str(account_id),
            'account_code': account.code,
            'account_name': account.name,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'opening_balance': float(opening_balance),
            'closing_balance': float(closing_balance),
            'period_debit': float(period_debit),
            'period_credit': float(period_credit),
            'transactions': transactions
        }
        
    def close_period(self, period_end: datetime) -> List[AccountBalance]:
        """
        Close an accounting period by creating balance records for all accounts.
        
        Args:
            period_end: The end date of the period to close
            
        Returns:
            List of created AccountBalance records
            
        Raises:
            PeriodAlreadyClosedException: If the period is already closed
            InvalidDateRangeException: If the period is invalid
        """
        # Check if the period is already closed
        existing_balance = self.db.query(AccountBalance).filter(
            func.date(AccountBalance.period_end) == period_end.date()
        ).first()
        
        if existing_balance:
            raise PeriodAlreadyClosedException(f"Period ending {period_end.date()} is already closed")
            
        # Find the previous period end date
        prev_period = self.db.query(
            func.max(AccountBalance.period_end)
        ).filter(
            AccountBalance.period_end < period_end
        ).scalar()
        
        # Get all accounts
        accounts = self.db.query(Account).filter(
            Account.status == 'active'
        ).all()
        
        balances = []
        for account in accounts:
            # Get the closing balance of the previous period
            if prev_period:
                prev_balance = self.db.query(AccountBalance).filter(
                    AccountBalance.account_id == account.id,
                    AccountBalance.period_end == prev_period
                ).first()
                
                if prev_balance:
                    opening_balance = prev_balance.closing_balance
                else:
                    # No previous balance, calculate from beginning of time
                    opening_balance = self.get_balance_as_of(account.id, prev_period)
            else:
                # First period, start from 0
                opening_balance = Decimal('0.00')
            
            # Calculate period activity
            period_activity = self.db.query(
                func.sum(
                    case(
                        [
                            (JournalEntryLine.is_debit == True, JournalEntryLine.amount),  # noqa: E712
                            (JournalEntryLine.is_debit == False, -JournalEntryLine.amount)  # noqa: E712
                        ],
                        else_=0
                    )
                )
            ).join(
                JournalEntry,
                JournalEntry.id == JournalEntryLine.journal_entry_id
            ).filter(
                JournalEntryLine.account_id == account.id,
                JournalEntry.status == JournalEntryStatus.POSTED,
                JournalEntry.posted_at > (prev_period or datetime.min),
                JournalEntry.posted_at <= period_end
            ).scalar() or Decimal('0.00')
            
            # For contra accounts, flip the sign of the activity
            if account.is_contra:
                period_activity = -period_activity
                
            closing_balance = opening_balance + period_activity
            
            # Calculate period debit/credit totals
            period_debit, period_credit = self.db.query(
                func.sum(
                    case([(JournalEntryLine.is_debit == True, JournalEntryLine.amount)], else_=0)  # noqa: E712
                ),
                func.sum(
                    case([(JournalEntryLine.is_debit == False, JournalEntryLine.amount)], else_=0)  # noqa: E712
                )
            ).join(
                JournalEntry,
                JournalEntry.id == JournalEntryLine.journal_entry_id
            ).filter(
                JournalEntryLine.account_id == account.id,
                JournalEntry.status == JournalEntryStatus.POSTED,
                JournalEntry.posted_at > (prev_period or datetime.min),
                JournalEntry.posted_at <= period_end
            ).first() or (Decimal('0.00'), Decimal('0.00'))
            
            # Create the balance record
            balance = AccountBalance(
                account_id=account.id,
                period_start=prev_period or datetime.min,
                period_end=period_end,
                opening_balance=opening_balance,
                closing_balance=closing_balance,
                period_debit=period_debit or Decimal('0.00'),
                period_credit=period_credit or Decimal('0.00'),
                is_closed=True
            )
            
            self.db.add(balance)
            balances.append(balance)
        
        # Commit all the new balance records
        self.db.commit()
        
        return balances

        """
        if as_of_date is None:
            as_of_date = datetime.utcnow()
            
        # Get the account
        account = self.get_account(account_id)
        
        # Calculate balance from journal entries
        stmt = select(
            func.coalesce(
                func.sum(
                    case(
                        [(JournalEntryLine.debit > 0, JournalEntryLine.debit)],
                        else_=-JournalEntryLine.credit
                    )
                ),
                0
            )
        ).join(
            JournalEntryLine.journal_entry
        ).where(
            JournalEntryLine.account_id == account_id,
            JournalEntry.status == JournalEntryStatus.POSTED,
            JournalEntry.entry_date <= as_of_date
        )
        
        balance = self.db.scalar(stmt) or Decimal('0.00')
        
        # If this is a contra account, invert the balance
        if account.is_contra:
            balance = -balance
            
        return balance
    
    def get_balance_as_of(self, account_id: UUID, as_of_date: datetime = None) -> Decimal:
        """
        Get the balance of an account as of a specific date, using historical balances if available.
        
        Args:
            account_id: UUID of the account
            as_of_date: The date to get the balance for (defaults to now)
            
        Returns:
            The account balance as of the specified date
        """
        if as_of_date is None:
            as_of_date = datetime.utcnow()
        
        # First try to find a historical balance record
        stmt = select(AccountBalance).where(
            AccountBalance.account_id == account_id,
            AccountBalance.period_start <= as_of_date,
            or_(
                AccountBalance.period_end.is_(None),
                AccountBalance.period_end > as_of_date
            )
        ).order_by(AccountBalance.period_start.desc()).limit(1)
        
        balance_record = self.db.scalar(stmt)
        
        if balance_record:
            return balance_record.closing_balance
            
        # If no historical balance found, calculate from journal entries
        return self.calculate_account_balance(account_id, as_of_date)
    
    def get_balance_for_period(
        self, 
        account_id: UUID, 
        start_date: datetime, 
        end_date: datetime = None
    ) -> Dict[str, Union[Decimal, datetime]]:
        """
        Get the balance details for an account over a specific period.
        
        Args:
            account_id: The ID of the account
            start_date: The start of the period
            end_date: The end of the period (defaults to now)
            
        Returns:
            A dictionary containing balance information for the period
        """
        if end_date is None:
            end_date = datetime.utcnow()
            
        if start_date > end_date:
            raise InvalidDateRangeException("Start date cannot be after end date")
        
        # Get the account
        account = self.get_account(account_id)
        
        # Get opening balance (as of the day before the period starts)
        opening_balance = self.get_balance_as_of(account_id, start_date - timedelta(seconds=1))
        
        # Get period activity
        stmt = select(
            func.coalesce(func.sum(JournalEntryLine.debit), 0).label('total_debit'),
            func.coalesce(func.sum(JournalEntryLine.credit), 0).label('total_credit')
        ).join(
            JournalEntryLine.journal_entry
        ).where(
            JournalEntryLine.account_id == account_id,
            JournalEntry.status == JournalEntryStatus.POSTED,
            JournalEntry.entry_date >= start_date,
            JournalEntry.entry_date <= end_date
        )
        
        result = self.db.execute(stmt).first()
        period_debit = result[0] if result[0] is not None else Decimal('0.00')
        period_credit = result[1] if result[1] is not None else Decimal('0.00')
        
        # Calculate net activity based on normal balance
        if account.normal_balance == 'debit':
            period_net = period_debit - period_credit
        else:
            period_net = period_credit - period_debit
            
        closing_balance = opening_balance + period_net
        
        return {
            'account_id': account_id,
            'account_code': account.code,
            'account_name': account.name,
            'opening_balance': opening_balance,
            'period_debit': period_debit,
            'period_credit': period_credit,
            'period_net': period_net,
            'closing_balance': closing_balance,
            'start_date': start_date,
            'end_date': end_date
        }
    
    def create_periodic_balance(
        self,
        account_id: UUID,
        period_start: datetime,
        period_end: datetime = None,
        commit: bool = True
    ) -> AccountBalance:
        """
        Create a periodic balance record for an account.
        
        Args:
            account_id: The ID of the account
            period_start: The start of the period
            period_end: The end of the period (optional)
            commit: Whether to commit the transaction (default: True)
            
        Returns:
            The created AccountBalance record
        """
        # Get the account
        account = self.get_account(account_id)
        
        # Calculate balances
        balance_data = self.get_balance_for_period(account_id, period_start, period_end)
        
        # Create the balance record
        balance = AccountBalance(
            account_id=account_id,
            period_start=period_start,
            period_end=period_end,
            opening_balance=balance_data['opening_balance'],
            period_debit=balance_data['period_debit'],
            period_credit=balance_data['period_credit'],
            closing_balance=balance_data['closing_balance']
        )
        
        self.db.add(balance)
        
        if commit:
            self.db.commit()
            self.db.refresh(balance)
        
        return balance
    
    def close_period(
        self,
        period_end: datetime,
        commit: bool = True
    ) -> List[AccountBalance]:
        """
        Close a period by creating balance records for all accounts.
        
        Args:
            period_end: The end of the period to close
            commit: Whether to commit the transaction (default: True)
            
        Returns:
            A list of created AccountBalance records
        """
        # Find the previous period end to use as our period start
        stmt = select(func.max(AccountBalance.period_end)).where(
            AccountBalance.period_end < period_end
        )
        
        period_start = self.db.scalar(stmt) or datetime.min.replace(tzinfo=period_end.tzinfo)
        
        # Get all active accounts
        accounts = self.db.query(Account).filter(Account.status == 'active').all()
        
        balances = []
        for account in accounts:
            balance = self.create_periodic_balance(
                account_id=account.id,
                period_start=period_start,
                period_end=period_end,
                commit=False
            )
            balances.append(balance)
        
        if commit and balances:
            self.db.commit()
            for balance in balances:
                self.db.refresh(balance)
        
        return balances
=======
"""
Paksa Financial System 
Account Balance Service

This module provides services for managing and calculating account balances,
including real-time and historical balance calculations.
"""
from datetime import datetime, timedelta, date
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Tuple, Union, Any
from uuid import UUID

from dateutil.relativedelta import relativedelta
from sqlalchemy import and_, case, func, or_, select, text
from sqlalchemy.orm import Session, aliased

from app.core.database import SessionLocal
from ..exceptions import (
    AccountNotFoundException,
    InvalidDateRangeException,
    PeriodAlreadyClosedException,
    PeriodNotClosedException,
    InvalidBalancePeriodException,
)
from ..models import (
    Account,
    AccountBalance,
    AccountType,
    JournalEntry,
    JournalEntryLine,
    JournalEntryStatus,
)


class AccountBalanceService:
    """Service for managing account balances and related operations."""
    
    def __init__(self, db: Optional[Session] = None):
        """Initialize the service with an optional database session."""
        self.db = db or SessionLocal()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close the session if we created it."""
        if self.db and not self.db.bind:
            self.db.close()
    
    def get_account(self, account_id: UUID) -> Account:
        """Get an account by ID, raising an exception if not found."""
        account = self.db.get(Account, account_id)
        if not account:
            raise AccountNotFoundException(account_id)
        return account
    
    def get_balance_as_of(self, account_id: UUID, as_of_date: datetime = None) -> Decimal:
        """
        Get the balance of an account as of a specific date.
        
        This method calculates the balance by considering:
        1. The most recent balance snapshot (if any)
        2. All transactions after the snapshot date up to as_of_date
        
        Args:
            account_id: The ID of the account
            as_of_date: The date to calculate the balance for (defaults to now)
            
        Returns:
            Decimal: The account balance as of the specified date
            
        Raises:
            AccountNotFoundException: If the account doesn't exist
            InvalidDateRangeException: If the date range is invalid
        """
        if as_of_date is None:
            as_of_date = datetime.utcnow()
            
        # Get the account to verify it exists and get its type
        account = self.get_account(account_id)
        
        # Find the most recent balance snapshot before or on as_of_date
        latest_snapshot = self.db.query(AccountBalance).filter(
            AccountBalance.account_id == account_id,
            AccountBalance.period_end <= as_of_date
        ).order_by(AccountBalance.period_end.desc()).first()
        
        # Calculate the starting point for transaction aggregation
        if latest_snapshot:
            start_date = latest_snapshot.period_end
            running_balance = latest_snapshot.closing_balance
        else:
            # No snapshot found, start from the beginning of time
            start_date = datetime.min
            running_balance = Decimal('0.00')
        
        # Calculate the net effect of all transactions between start_date and as_of_date
        # This is a simplified version - in a real implementation, you'd want to optimize this
        # for performance, especially for accounts with many transactions
        query = self.db.query(
            func.sum(
                case(
                    [
                        (JournalEntryLine.is_debit == True, JournalEntryLine.amount),  # noqa: E712
                        (JournalEntryLine.is_debit == False, -JournalEntryLine.amount)  # noqa: E712
                    ],
                    else_=0
                )
            ).label('net_effect')
        ).join(
            JournalEntry,
            JournalEntry.id == JournalEntryLine.journal_entry_id
        ).filter(
            JournalEntryLine.account_id == account_id,
            JournalEntry.status == JournalEntryStatus.POSTED,
            JournalEntry.posted_at > start_date,
            JournalEntry.posted_at <= as_of_date
        )
        
        net_effect = query.scalar() or Decimal('0.00')
        balance = running_balance + net_effect
        
        # For contra accounts, we need to flip the sign
        if account.is_contra:
            balance = -balance
            
        return balance.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
    def get_balance_for_period(
        self,
        account_id: UUID,
        start_date: datetime,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get detailed balance information for an account over a specific period.
        
        Args:
            account_id: The ID of the account
            start_date: Start of the period
            end_date: End of the period (defaults to now)
            
        Returns:
            Dict containing:
                - opening_balance: Balance at start_date
                - closing_balance: Balance at end_date
                - period_debit: Total debits during the period
                - period_credit: Total credits during the period
                - transactions: List of transactions in the period
                
        Raises:
            AccountNotFoundException: If the account doesn't exist
            InvalidDateRangeException: If the date range is invalid
        """
        if end_date is None:
            end_date = datetime.utcnow()
            
        if start_date > end_date:
            raise InvalidDateRangeException("Start date must be before end date")
            
        # Get the account to verify it exists and get its type
        account = self.get_account(account_id)
        
        # Get the opening balance (as of start_date)
        opening_balance = self.get_balance_as_of(account_id, start_date)
        
        # Get the closing balance (as of end_date)
        closing_balance = self.get_balance_as_of(account_id, end_date)
        
        # Get the period transactions
        period_transactions = self.db.query(
            JournalEntryLine,
            JournalEntry.reference,
            JournalEntry.entry_date,
            JournalEntry.posted_at
        ).join(
            JournalEntry,
            JournalEntry.id == JournalEntryLine.journal_entry_id
        ).filter(
            JournalEntryLine.account_id == account_id,
            JournalEntry.status == JournalEntryStatus.POSTED,
            JournalEntry.posted_at > start_date,
            JournalEntry.posted_at <= end_date
        ).order_by(JournalEntry.posted_at).all()
        
        # Calculate period totals
        period_debit = Decimal('0.00')
        period_credit = Decimal('0.00')
        
        transactions = []
        for line, ref, entry_date, posted_at in period_transactions:
            if line.is_debit:
                period_debit += line.amount
            else:
                period_credit += line.amount
                
            transactions.append({
                'id': str(line.id),
                'journal_entry_id': str(line.journal_entry_id),
                'reference': ref,
                'entry_date': entry_date.isoformat(),
                'posted_at': posted_at.isoformat(),
                'description': line.description,
                'amount': float(line.amount),
                'is_debit': line.is_debit,
                'entity_type': line.entity_type,
                'entity_id': str(line.entity_id) if line.entity_id else None,
            })
        
        return {
            'account_id': str(account_id),
            'account_code': account.code,
            'account_name': account.name,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'opening_balance': float(opening_balance),
            'closing_balance': float(closing_balance),
            'period_debit': float(period_debit),
            'period_credit': float(period_credit),
            'transactions': transactions
        }
        
    def close_period(self, period_end: datetime) -> List[AccountBalance]:
        """
        Close an accounting period by creating balance records for all accounts.
        
        Args:
            period_end: The end date of the period to close
            
        Returns:
            List of created AccountBalance records
            
        Raises:
            PeriodAlreadyClosedException: If the period is already closed
            InvalidDateRangeException: If the period is invalid
        """
        # Check if the period is already closed
        existing_balance = self.db.query(AccountBalance).filter(
            func.date(AccountBalance.period_end) == period_end.date()
        ).first()
        
        if existing_balance:
            raise PeriodAlreadyClosedException(f"Period ending {period_end.date()} is already closed")
            
        # Find the previous period end date
        prev_period = self.db.query(
            func.max(AccountBalance.period_end)
        ).filter(
            AccountBalance.period_end < period_end
        ).scalar()
        
        # Get all accounts
        accounts = self.db.query(Account).filter(
            Account.status == 'active'
        ).all()
        
        balances = []
        for account in accounts:
            # Get the closing balance of the previous period
            if prev_period:
                prev_balance = self.db.query(AccountBalance).filter(
                    AccountBalance.account_id == account.id,
                    AccountBalance.period_end == prev_period
                ).first()
                
                if prev_balance:
                    opening_balance = prev_balance.closing_balance
                else:
                    # No previous balance, calculate from beginning of time
                    opening_balance = self.get_balance_as_of(account.id, prev_period)
            else:
                # First period, start from 0
                opening_balance = Decimal('0.00')
            
            # Calculate period activity
            period_activity = self.db.query(
                func.sum(
                    case(
                        [
                            (JournalEntryLine.is_debit == True, JournalEntryLine.amount),  # noqa: E712
                            (JournalEntryLine.is_debit == False, -JournalEntryLine.amount)  # noqa: E712
                        ],
                        else_=0
                    )
                )
            ).join(
                JournalEntry,
                JournalEntry.id == JournalEntryLine.journal_entry_id
            ).filter(
                JournalEntryLine.account_id == account.id,
                JournalEntry.status == JournalEntryStatus.POSTED,
                JournalEntry.posted_at > (prev_period or datetime.min),
                JournalEntry.posted_at <= period_end
            ).scalar() or Decimal('0.00')
            
            # For contra accounts, flip the sign of the activity
            if account.is_contra:
                period_activity = -period_activity
                
            closing_balance = opening_balance + period_activity
            
            # Calculate period debit/credit totals
            period_debit, period_credit = self.db.query(
                func.sum(
                    case([(JournalEntryLine.is_debit == True, JournalEntryLine.amount)], else_=0)  # noqa: E712
                ),
                func.sum(
                    case([(JournalEntryLine.is_debit == False, JournalEntryLine.amount)], else_=0)  # noqa: E712
                )
            ).join(
                JournalEntry,
                JournalEntry.id == JournalEntryLine.journal_entry_id
            ).filter(
                JournalEntryLine.account_id == account.id,
                JournalEntry.status == JournalEntryStatus.POSTED,
                JournalEntry.posted_at > (prev_period or datetime.min),
                JournalEntry.posted_at <= period_end
            ).first() or (Decimal('0.00'), Decimal('0.00'))
            
            # Create the balance record
            balance = AccountBalance(
                account_id=account.id,
                period_start=prev_period or datetime.min,
                period_end=period_end,
                opening_balance=opening_balance,
                closing_balance=closing_balance,
                period_debit=period_debit or Decimal('0.00'),
                period_credit=period_credit or Decimal('0.00'),
                is_closed=True
            )
            
            self.db.add(balance)
            balances.append(balance)
        
        # Commit all the new balance records
        self.db.commit()
        
        return balances

        """
        if as_of_date is None:
            as_of_date = datetime.utcnow()
            
        # Get the account
        account = self.get_account(account_id)
        
        # Calculate balance from journal entries
        stmt = select(
            func.coalesce(
                func.sum(
                    case(
                        [(JournalEntryLine.debit > 0, JournalEntryLine.debit)],
                        else_=-JournalEntryLine.credit
                    )
                ),
                0
            )
        ).join(
            JournalEntryLine.journal_entry
        ).where(
            JournalEntryLine.account_id == account_id,
            JournalEntry.status == JournalEntryStatus.POSTED,
            JournalEntry.entry_date <= as_of_date
        )
        
        balance = self.db.scalar(stmt) or Decimal('0.00')
        
        # If this is a contra account, invert the balance
        if account.is_contra:
            balance = -balance
            
        return balance
    
    def get_balance_as_of(self, account_id: UUID, as_of_date: datetime = None) -> Decimal:
        """
        Get the balance of an account as of a specific date, using historical balances if available.
        
        Args:
            account_id: UUID of the account
            as_of_date: The date to get the balance for (defaults to now)
            
        Returns:
            The account balance as of the specified date
        """
        if as_of_date is None:
            as_of_date = datetime.utcnow()
        
        # First try to find a historical balance record
        stmt = select(AccountBalance).where(
            AccountBalance.account_id == account_id,
            AccountBalance.period_start <= as_of_date,
            or_(
                AccountBalance.period_end.is_(None),
                AccountBalance.period_end > as_of_date
            )
        ).order_by(AccountBalance.period_start.desc()).limit(1)
        
        balance_record = self.db.scalar(stmt)
        
        if balance_record:
            return balance_record.closing_balance
            
        # If no historical balance found, calculate from journal entries
        return self.calculate_account_balance(account_id, as_of_date)
    
    def get_balance_for_period(
        self, 
        account_id: UUID, 
        start_date: datetime, 
        end_date: datetime = None
    ) -> Dict[str, Union[Decimal, datetime]]:
        """
        Get the balance details for an account over a specific period.
        
        Args:
            account_id: The ID of the account
            start_date: The start of the period
            end_date: The end of the period (defaults to now)
            
        Returns:
            A dictionary containing balance information for the period
        """
        if end_date is None:
            end_date = datetime.utcnow()
            
        if start_date > end_date:
            raise InvalidDateRangeException("Start date cannot be after end date")
        
        # Get the account
        account = self.get_account(account_id)
        
        # Get opening balance (as of the day before the period starts)
        opening_balance = self.get_balance_as_of(account_id, start_date - timedelta(seconds=1))
        
        # Get period activity
        stmt = select(
            func.coalesce(func.sum(JournalEntryLine.debit), 0).label('total_debit'),
            func.coalesce(func.sum(JournalEntryLine.credit), 0).label('total_credit')
        ).join(
            JournalEntryLine.journal_entry
        ).where(
            JournalEntryLine.account_id == account_id,
            JournalEntry.status == JournalEntryStatus.POSTED,
            JournalEntry.entry_date >= start_date,
            JournalEntry.entry_date <= end_date
        )
        
        result = self.db.execute(stmt).first()
        period_debit = result[0] if result[0] is not None else Decimal('0.00')
        period_credit = result[1] if result[1] is not None else Decimal('0.00')
        
        # Calculate net activity based on normal balance
        if account.normal_balance == 'debit':
            period_net = period_debit - period_credit
        else:
            period_net = period_credit - period_debit
            
        closing_balance = opening_balance + period_net
        
        return {
            'account_id': account_id,
            'account_code': account.code,
            'account_name': account.name,
            'opening_balance': opening_balance,
            'period_debit': period_debit,
            'period_credit': period_credit,
            'period_net': period_net,
            'closing_balance': closing_balance,
            'start_date': start_date,
            'end_date': end_date
        }
    
    def create_periodic_balance(
        self,
        account_id: UUID,
        period_start: datetime,
        period_end: datetime = None,
        commit: bool = True
    ) -> AccountBalance:
        """
        Create a periodic balance record for an account.
        
        Args:
            account_id: The ID of the account
            period_start: The start of the period
            period_end: The end of the period (optional)
            commit: Whether to commit the transaction (default: True)
            
        Returns:
            The created AccountBalance record
        """
        # Get the account
        account = self.get_account(account_id)
        
        # Calculate balances
        balance_data = self.get_balance_for_period(account_id, period_start, period_end)
        
        # Create the balance record
        balance = AccountBalance(
            account_id=account_id,
            period_start=period_start,
            period_end=period_end,
            opening_balance=balance_data['opening_balance'],
            period_debit=balance_data['period_debit'],
            period_credit=balance_data['period_credit'],
            closing_balance=balance_data['closing_balance']
        )
        
        self.db.add(balance)
        
        if commit:
            self.db.commit()
            self.db.refresh(balance)
        
        return balance
    
    def close_period(
        self,
        period_end: datetime,
        commit: bool = True
    ) -> List[AccountBalance]:
        """
        Close a period by creating balance records for all accounts.
        
        Args:
            period_end: The end of the period to close
            commit: Whether to commit the transaction (default: True)
            
        Returns:
            A list of created AccountBalance records
        """
        # Find the previous period end to use as our period start
        stmt = select(func.max(AccountBalance.period_end)).where(
            AccountBalance.period_end < period_end
        )
        
        period_start = self.db.scalar(stmt) or datetime.min.replace(tzinfo=period_end.tzinfo)
        
        # Get all active accounts
        accounts = self.db.query(Account).filter(Account.status == 'active').all()
        
        balances = []
        for account in accounts:
            balance = self.create_periodic_balance(
                account_id=account.id,
                period_start=period_start,
                period_end=period_end,
                commit=False
            )
            balances.append(balance)
        
        if commit and balances:
            self.db.commit()
            for balance in balances:
                self.db.refresh(balance)
        
        return balances
>>>>>>> e96df7278ce4216131b6c65d411c0723f4de7f91:backend/app/services/accounting/account_balance_service.py
