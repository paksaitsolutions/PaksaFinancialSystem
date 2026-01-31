"""
Reconciliation Service

This module provides the main service implementation for account reconciliation functionality.
"""
from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any, Union

from ...models.account import Account
from ...models.journal import JournalEntry, JournalEntryLine, JournalEntryStatus
from ...models.reconciliation import (
from ...schemas.reconciliation import (
from .base import BaseReconciliationService
from decimal import Decimal
from sqlalchemy import and_, or_, func, select
from sqlalchemy.orm import Session, joinedload
from uuid import UUID, uuid4

from app.core.exceptions import (
from app.core.logging import get_logger



    NotFoundException,
    ValidationException,
    ForbiddenException,
    ConflictException
)

    Reconciliation,
    ReconciliationItem,
    ReconciliationRule,
    ReconciliationAuditLog,
    ReconciliationStatus,
    ReconciliationMatchType
)
    ReconciliationCreate,
    ReconciliationUpdate,
    ReconciliationItemCreate,
    ReconciliationItemUpdate,
    ReconciliationRuleCreate,
    ReconciliationRuleUpdate,
    ReconciliationAuditLogCreate
)


logger = get_logger(__name__)


class ReconciliationService(BaseReconciliationService):
    """Service for handling reconciliation operations."""
    
    # Reconciliation CRUD Operations
    
    def get_reconciliation(self, reconciliation_id: UUID, user_id: UUID) -> Reconciliation:
        """Get Reconciliation."""
        """Get a reconciliation by ID with permission check.
        
        Args:
            reconciliation_id: ID of the reconciliation to retrieve
            user_id: ID of the user making the request
            
        Returns:
            The reconciliation
            
        Raises:
            NotFoundException: If the reconciliation doesn't exist
            ForbiddenException: If the user doesn't have permission to view this reconciliation
        """
        reconciliation = self.db.query(Reconciliation).get(reconciliation_id)
        
        if not reconciliation:
            raise NotFoundException("Reconciliation not found")
            
        # For now, just check if the user created the reconciliation
        if reconciliation.created_by != user_id:
            raise ForbiddenException("You don't have permission to access this reconciliation")
            
        return reconciliation
    
    def list_reconciliations(
        """List Reconciliations."""
        self,
        user_id: UUID,
        account_id: Optional[UUID] = None,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[Reconciliation], int]:
        """List Reconciliations."""
        """List reconciliations with optional filtering.
        
        Args:
            user_id: ID of the user making the request
            account_id: Filter by account ID
            status: Filter by status
            start_date: Filter by start date (greater than or equal)
            end_date: Filter by end date (less than or equal)
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return
            
        Returns:
            Tuple of (list of reconciliations, total count)
        """
        query = self.db.query(Reconciliation)
        
        # Apply filters
        # For now, just filter by created_by
        query = query.filter(Reconciliation.created_by == user_id)
        
        if account_id:
            query = query.filter(Reconciliation.account_id == account_id)
            
        if status:
            query = query.filter(Reconciliation.status == status)
            
        if start_date:
            query = query.filter(Reconciliation.end_date >= start_date)
            
        if end_date:
            query = query.filter(Reconciliation.start_date <= end_date)
        
        # Order by end_date descending (most recent first)
        query = query.order_by(Reconciliation.end_date.desc())
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        reconciliations = query.offset(skip).limit(limit).all()
        
        return reconciliations, total
    
    def create_reconciliation(self, data: ReconciliationCreate, user_id: UUID) -> Reconciliation:
        """Create Reconciliation."""
        """Create a new reconciliation.
        
        Args:
            data: Reconciliation data
            user_id: ID of the user creating the reconciliation
            
        Returns:
            The created reconciliation
            
        Raises:
            NotFoundException: If the account doesn't exist
            ValidationException: If the data is invalid
        """
        # Verify the account exists and is active
        account = self.account_service.get_account(data.account_id)
        if not account.is_active:
            raise ValidationException("Cannot reconcile an inactive account")
        
        # Validate the date range
        if data.end_date <= data.start_date:
            raise ValidationException("End date must be after start date")
        
        # Check for overlapping reconciliations
        existing = self.db.query(Reconciliation).filter(
            Reconciliation.account_id == data.account_id,
            or_(
                and_(
                    Reconciliation.start_date <= data.start_date,
                    Reconciliation.end_date >= data.start_date
                ),
                and_(
                    Reconciliation.start_date <= data.end_date,
                    Reconciliation.end_date >= data.end_date
                ),
                and_(
                    Reconciliation.start_date >= data.start_date,
                    Reconciliation.end_date <= data.end_date
                )
            )
        ).first()
        
        if existing:
            raise ValidationException(
                f"A reconciliation already exists for this account that overlaps with the specified date range: "
                f"{existing.start_date.date()} to {existing.end_date.date()}"
            )
        
        # Calculate the account balance as of the end date
        balance_service = AccountBalanceService(self.db)
        balance_result = balance_service.get_account_balance(
            account_id=data.account_id,
            as_of_date=data.end_date,
            include_children=False
        )
        
        calculated_balance = balance_result['balance']
        difference = data.statement_balance - calculated_balance
        
        # Create the reconciliation
        reconciliation = Reconciliation(
            id=uuid4(),
            account_id=data.account_id,
            reference=data.reference,
            status=ReconciliationStatus.DRAFT,
            start_date=data.start_date,
            end_date=data.end_date,
            statement_balance=data.statement_balance,
            statement_currency=data.statement_currency,
            statement_reference=data.statement_reference,
            statement_date=data.statement_date,
            calculated_balance=calculated_balance,
            difference=difference,
            created_by=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.db.add(reconciliation)
        
        # Add audit log
        self._add_audit_log(
            reconciliation_id=reconciliation.id,
            action="create",
            user_id=user_id,
            details={
                "status": ReconciliationStatus.DRAFT,
                "statement_balance": float(data.statement_balance),
                "calculated_balance": float(calculated_balance),
                "difference": float(difference)
            }
        )
        
        self.db.commit()
        
        return reconciliation
