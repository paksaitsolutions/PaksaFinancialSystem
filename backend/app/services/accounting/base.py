"""
Paksa Financial System 
Base Reconciliation Service

This module contains the base service class for reconciliation operations.
"""
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Tuple, Dict, Any, Union
from uuid import UUID

from sqlalchemy import and_, or_, func, select
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import (
    NotFoundException,
    ValidationException,
    ForbiddenException,
    ConflictException
)
from app.core.logging import get_logger

from ...models.reconciliation import (
    Reconciliation,
    ReconciliationItem,
    ReconciliationRule,
    ReconciliationAuditLog,
    ReconciliationStatus,
    ReconciliationMatchType
)
from ...models.account import Account
from ...models.journal import JournalEntry, JournalEntryLine, JournalEntryStatus
from ...schemas.reconciliation import (
    ReconciliationCreate,
    ReconciliationUpdate,
    ReconciliationItemCreate,
    ReconciliationItemUpdate,
    ReconciliationRuleCreate,
    ReconciliationRuleUpdate,
    ReconciliationAuditLogCreate
)
from ..account_service import AccountService
from ..journal_service import JournalEntryService

logger = get_logger(__name__)


class BaseReconciliationService:
    """Base service class for reconciliation operations."""
    
    def __init__(self, db: Session):
        """Initialize the base reconciliation service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.account_service = AccountService(db)
        self.journal_service = JournalEntryService(db)
    
    # Helper Methods
    
    def _add_audit_log(
        self, 
        reconciliation_id: UUID, 
        action: str, 
        user_id: UUID, 
        details: Optional[Dict[str, Any]] = None
    ) -> ReconciliationAuditLog:
        """Add an audit log entry for a reconciliation.
        
        Args:
            reconciliation_id: ID of the reconciliation
            action: Action that was performed
            user_id: ID of the user who performed the action
            details: Additional details about the action
            
        Returns:
            The created audit log entry
        """
        log = ReconciliationAuditLog(
            id=uuid4(),
            reconciliation_id=reconciliation_id,
            action=action,
            details=details or {},
            user_id=user_id,
            created_at=datetime.utcnow()
        )
        
        self.db.add(log)
        return log
    
    def _recalculate_reconciliation(self, reconciliation_id: UUID, user_id: UUID) -> None:
        """Recalculate the reconciliation totals and update the status.
        
        Args:
            reconciliation_id: ID of the reconciliation to recalculate
            user_id: ID of the user initiating the recalculation
        """
        reconciliation = self.db.query(Reconciliation).get(reconciliation_id)
        if not reconciliation:
            raise NotFoundException("Reconciliation not found")
        
        # Get all matched items
        items = self.db.query(ReconciliationItem).filter(
            ReconciliationItem.reconciliation_id == reconciliation_id,
            ReconciliationItem.is_matched == True
        ).all()
        
        # Calculate the total of matched items
        matched_total = Decimal('0')
        for item in items:
            if item.statement_line_amount is not None:
                matched_total += Decimal(str(item.statement_line_amount))
        
        # Update the reconciliation
        reconciliation.calculated_balance = matched_total
        reconciliation.difference = reconciliation.statement_balance - matched_total
        reconciliation.updated_at = datetime.utcnow()
        
        # Update status based on the difference
        if reconciliation.difference == 0 and reconciliation.status == ReconciliationStatus.IN_PROGRESS:
            reconciliation.status = ReconciliationStatus.COMPLETED
            reconciliation.completed_at = datetime.utcnow()
            reconciliation.completed_by = user_id
        
        # Add audit log
        self._add_audit_log(
            reconciliation_id=reconciliation_id,
            action="recalculate",
            user_id=user_id,
            details={
                "calculated_balance": float(matched_total),
                "difference": float(reconciliation.difference),
                "new_status": reconciliation.status
            }
        )
