"""
Paksa Financial System 
GL Period Service

This module provides services for managing GL (General Ledger) periods.
"""
from datetime import date, datetime, timedelta
from typing import List, Dict, Optional, Tuple, Union, Any

from ...base.service import BaseService
from ..exceptions import (
from ..models import (
from dateutil.relativedelta import relativedelta
from sqlalchemy import and_, or_, func, case, text, extract
from sqlalchemy.orm import Session, joinedload
from uuid import UUID, uuid4



    PeriodNotFoundException,
    InvalidPeriodException,
    PeriodAlreadyClosedException,
    PeriodNotClosedException,
    PeriodOverlapException,
    PeriodInUseException
)
    GLPeriod,
    GLPeriodStatus,
    JournalEntry,
    AccountBalance
)


class GLPeriodService(BaseService):
    """Service for managing GL periods and related operations."""
    
    def __init__(self, db: Session):
        super().__init__(db)
    
    def create_period(
        self,
        name: str,
        start_date: date,
        end_date: date,
        fiscal_year: str,
        period_number: int,
        created_by: UUID,
        description: Optional[str] = None,
        is_adjusting_period: bool = False,
        parent_period_id: Optional[UUID] = None,
        **kwargs
    ) -> GLPeriod:
        """Create Period."""
        """
        Create a new GL period.
        
        Args:
            name: Name of the period (e.g., 'January 2023')
            start_date: Start date of the period
            end_date: End date of the period
            fiscal_year: Fiscal year (e.g., 'FY2023')
            period_number: Period number within the fiscal year (1-12 for monthly)
            created_by: ID of the user creating the period
            description: Optional description
            is_adjusting_period: Whether this is an adjusting period
            parent_period_id: Optional parent period ID for hierarchy
            **kwargs: Additional fields to set on the period
            
        Returns:
            The created GLPeriod object
            
        Raises:
            InvalidPeriodException: If the period dates are invalid
            PeriodOverlapException: If the period overlaps with an existing period
        """
        # Validate dates
        if start_date >= end_date:
            raise InvalidPeriodException("Start date must be before end date")
        
        # Check for overlapping periods
        overlapping_period = self.db.query(GLPeriod).filter(
            GLPeriod.status != GLPeriodStatus.PERMANENTLY_CLOSED,
            or_(
                and_(
                    GLPeriod.start_date <= start_date,
                    GLPeriod.end_date >= start_date
                ),
                and_(
                    GLPeriod.start_date <= end_date,
                    GLPeriod.end_date >= end_date
                ),
                and_(
                    GLPeriod.start_date >= start_date,
                    GLPeriod.end_date <= end_date
                )
            )
        ).first()
        
        if overlapping_period:
            raise PeriodOverlapException(
                f"Period overlaps with existing period: {overlapping_period.name} "
                f"({overlapping_period.start_date} to {overlapping_period.end_date})"
            )
        
        # Create the period
        period = GLPeriod(
            name=name,
            description=description,
            start_date=start_date,
            end_date=end_date,
            fiscal_year=fiscal_year,
            period_number=period_number,
            is_adjusting_period=is_adjusting_period,
            parent_period_id=parent_period_id,
            status=GLPeriodStatus.OPEN,
            created_by=created_by,
            updated_by=created_by,
            **kwargs
        )
        
        self.db.add(period)
        self.db.commit()
        self.db.refresh(period)
        
        return period
    
    def close_period(
        self, 
        period_id: UUID, 
        closed_by: UUID,
        force: bool = False,
        permanent: bool = False
    ) -> GLPeriod:
        """Close Period."""
        """
        Close a GL period.
        
        Args:
            period_id: The ID of the period to close
            closed_by: ID of the user closing the period
            force: If True, close the period even if there are unposted entries
            permanent: If True, permanently close the period (cannot be reopened)
            
        Returns:
            The updated GLPeriod object
            
        Raises:
            PeriodNotFoundException: If the period doesn't exist
            PeriodAlreadyClosedException: If the period is already closed
            PeriodInUseException: If there are unposted entries and force=False
        """
        period = self._get_period(period_id)
        
        if period.status != GLPeriodStatus.OPEN:
            if permanent and period.status == GLPeriodStatus.CLOSED:
                # Upgrade to permanently closed
                period.status = GLPeriodStatus.PERMANENTLY_CLOSED
                period.closed_at = datetime.utcnow()
                period.closed_by = closed_by
                period.updated_by = closed_by
                period.updated_at = datetime.utcnow()
                
                self.db.commit()
                self.db.refresh(period)
                return period
            
            raise PeriodAlreadyClosedException(f"Period '{period.name}' is already closed")
        
        # Check for unposted entries if not forcing
        if not force:
            unposted_count = self.db.query(JournalEntry).filter(
                JournalEntry.entry_date.between(period.start_date, period.end_date),
                JournalEntry.status != JournalEntryStatus.POSTED
            ).count()
            
            if unposted_count > 0:
                raise PeriodInUseException(
                    f"Cannot close period with {unposted_count} unposted journal entries. "
                    "Post or delete these entries first, or use force=True to close anyway."
                )
        
        # Update the period status
        period.status = GLPeriodStatus.PERMANENTLY_CLOSED if permanent else GLPeriodStatus.CLOSED
        period.closed_at = datetime.utcnow()
        period.closed_by = closed_by
        period.updated_by = closed_by
        period.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(period)
        
        return period
    
    def reopen_period(self, period_id: UUID, reopened_by: UUID) -> GLPeriod:
        """
        Reopen a closed GL period.
        
        Args:
            period_id: The ID of the period to reopen
            reopened_by: ID of the user reopening the period
            
        Returns:
            The updated GLPeriod object
            
        Raises:
            PeriodNotFoundException: If the period doesn't exist
            PeriodNotClosedException: If the period is not closed
            InvalidPeriodException: If the period is permanently closed
        """
        period = self._get_period(period_id)
        
        if period.status == GLPeriodStatus.OPEN:
            raise PeriodNotClosedException("Period is already open")
            
        if period.status == GLPeriodStatus.PERMANENTLY_CLOSED:
            raise InvalidPeriodException("Cannot reopen a permanently closed period")
        
        # Update the period status
        period.status = GLPeriodStatus.OPEN
        period.closed_at = None
        period.closed_by = None
        period.updated_by = reopened_by
        period.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(period)
        
        return period
    
    def get_period(self, period_id: UUID) -> GLPeriod:
        """
        Get a GL period by ID.
        
        Args:
            period_id: The ID of the period to retrieve
            
        Returns:
            The GLPeriod object
            
        Raises:
            PeriodNotFoundException: If the period doesn't exist
        """
        return self._get_period(period_id)
    
    def get_period_for_date(self, target_date: date) -> Optional[GLPeriod]:
        """
        Get the GL period that contains the specified date.
        
        Args:
            target_date: The date to find the period for
            
        Returns:
            The GLPeriod containing the date, or None if not found
        """
        return (
            self.db.query(GLPeriod)
            .filter(
                GLPeriod.start_date <= target_date,
                GLPeriod.end_date >= target_date
            )
            .order_by(GLPeriod.start_date.desc())
            .first()
        )
    
    def get_current_period(self) -> Optional[GLPeriod]:
        """
        Get the current GL period based on the current date.
        
        Returns:
            The current GLPeriod, or None if not found
        """
        today = date.today()
        return self.get_period_for_date(today)
    
    def list_periods(
        self,
        fiscal_year: Optional[str] = None,
        status: Optional[Union[GLPeriodStatus, str]] = None,
        include_adjusting: bool = False,
        page: int = 1,
        page_size: int = 50,
        include_children: bool = False
    ) -> Dict[str, Any]:
        """List Periods."""
        """
        List GL periods with optional filtering and pagination.
        
        Args:
            fiscal_year: Filter by fiscal year (e.g., 'FY2023')
            status: Filter by status (open, closed, permanently_closed)
            include_adjusting: Whether to include adjusting periods
            page: Page number (1-based)
            page_size: Number of items per page
            include_children: Whether to include child periods in the results
            
        Returns:
            Dictionary containing the list of periods and pagination info
        """
        query = self.db.query(GLPeriod)
        
        # Apply filters
        if fiscal_year:
            query = query.filter(GLPeriod.fiscal_year == fiscal_year)
            
        if status is not None:
            if isinstance(status, str):
                status = GLPeriodStatus(status.lower())
            query = query.filter(GLPeriod.status == status)
            
        if not include_adjusting:
            query = query.filter(GLPeriod.is_adjusting_period == False)
        
        # Get total count for pagination
        total = query.count()
        
        # Apply pagination and ordering
        query = query.order_by(GLPeriod.start_date.desc(), GLPeriod.end_date.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        # Execute query
        periods = query.all()
        
        # Include child periods if requested
        if include_children and periods:
            period_ids = [p.id for p in periods]
            child_periods = self.db.query(GLPeriod).filter(
                GLPeriod.parent_period_id.in_(period_ids)
            ).all()
            
            # Group child periods by parent ID
            children_by_parent = {}
            for child in child_periods:
                if child.parent_period_id not in children_by_parent:
                    children_by_parent[child.parent_period_id] = []
                children_by_parent[child.parent_period_id].append(child)
            
            # Attach children to their parents
            for period in periods:
                period.child_periods = children_by_parent.get(period.id, [])
        
        return {
            'items': periods,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }
    
    def is_period_open(self, target_date: date) -> bool:
        """
        Check if the period containing the given date is open.
        
        Args:
            target_date: The date to check
            
        Returns:
            bool: True if the period is open, False otherwise
        """
        period = self.get_period_for_date(target_date)
        return period is not None and period.status == GLPeriodStatus.OPEN
    
    def get_period_balances(
        self,
        period_id: UUID,
        account_ids: Optional[List[UUID]] = None,
        include_children: bool = False
    ) -> List[Dict[str, Any]]:
        """Get Period Balances."""
        """
        Get account balances for a specific period.
        
        Args:
            period_id: The ID of the period
            account_ids: Optional list of account IDs to filter by
            include_children: Whether to include child accounts
            
        Returns:
            List of account balances with period information
            
        Raises:
            PeriodNotFoundException: If the period doesn't exist
        """
        period = self._get_period(period_id)
        
        query = (
            self.db.query(
                AccountBalance,
                Account.code.label('account_code'),
                Account.name.label('account_name'),
                Account.type.label('account_type')
            )
            .join(Account, Account.id == AccountBalance.account_id)
            .filter(AccountBalance.period_id == period_id)
        )
        
        if account_ids:
            if include_children:
                # Get all child accounts for the specified account IDs
                account_codes = (
                    self.db.query(Account.code)
                    .filter(Account.id.in_(account_ids))
                    .subquery()
                )
                
                query = query.filter(
                    or_(
                        Account.id.in_(account_ids),
                        Account.path.like(any_(f"%{code}%" for code in account_codes))
                    )
                )
            else:
                query = query.filter(Account.id.in_(account_ids))
        
        # Execute query and format results
        results = []
        for balance, code, name, acc_type in query.all():
            results.append({
                'account_id': balance.account_id,
                'account_code': code,
                'account_name': name,
                'account_type': acc_type,
                'opening_balance': float(balance.opening_balance) if balance.opening_balance is not None else 0.0,
                'debit': float(balance.debit) if balance.debit is not None else 0.0,
                'credit': float(balance.credit) if balance.credit is not None else 0.0,
                'closing_balance': float(balance.closing_balance) if balance.closing_balance is not None else 0.0,
                'period_id': balance.period_id,
                'period_name': period.name,
                'period_start': period.start_date.isoformat(),
                'period_end': period.end_date.isoformat(),
                'fiscal_year': period.fiscal_year,
                'period_status': period.status.value
            })
        
        return results
    
    def _get_period(self, period_id: UUID) -> GLPeriod:
        """
        Internal method to get a period by ID.
        
        Args:
            period_id: The ID of the period to retrieve
            
        Returns:
            The GLPeriod object
            
        Raises:
            PeriodNotFoundException: If the period doesn't exist
        """
        period = self.db.get(GLPeriod, period_id)
        
        if not period:
            raise PeriodNotFoundException(f"Period with ID {period_id} not found")
        
        return period
