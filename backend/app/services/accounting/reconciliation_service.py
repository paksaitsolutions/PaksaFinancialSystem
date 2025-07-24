"""
Reconciliation Service

This module provides services for managing account reconciliations.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4

from sqlalchemy import and_, or_, func, select
from sqlalchemy.orm import Session, joinedload

from .. import models, schemas
from ..exceptions import (
    ReconciliationNotFoundException,
    ReconciliationItemNotFoundException,
    InvalidReconciliationStateException,
    AccountNotFoundException,
    JournalEntryNotFoundException
)
from .account_balance_service import AccountBalanceService


class ReconciliationService:
    """Service for managing account reconciliations."""
    
    def __init__(self, db: Optional[Session] = None):
        """Initialize the service with an optional database session."""
        self.db = db
        self.balance_service = AccountBalanceService(db)
    
    def _get_db(self) -> Session:
        """Get a database session."""
        if not self.db:
            from core.database import SessionLocal
            return SessionLocal()
        return self.db
    
    def create_reconciliation(
        self,
        db: Session,
        reconciliation: schemas.ReconciliationCreate,
        user_id: UUID
    ) -> models.Reconciliation:
        """
        Create a new reconciliation.
        """
        db_reconciliation = models.Reconciliation(
            **reconciliation.dict(exclude={"id", "created_by", "updated_by"}),
            id=uuid4(),
            status=models.ReconciliationStatus.DRAFT,
            created_by=user_id,
            updated_by=user_id
        )
        
        db.add(db_reconciliation)
        db.commit()
        db.refresh(db_reconciliation)
        
        # Create an audit log
        self._create_audit_log(
            db=db,
            reconciliation_id=db_reconciliation.id,
            user_id=user_id,
            action="create",
            details={"status": db_reconciliation.status}
        )
        
        return db_reconciliation
    
    def get_reconciliation(
        self,
        db: Session,
        reconciliation_id: UUID,
        user_id: UUID
    ) -> Optional[models.Reconciliation]:
        """
        Get a reconciliation by ID.
        """
        return db.query(models.Reconciliation).filter(
            models.Reconciliation.id == reconciliation_id
        ).options(
            joinedload(models.Reconciliation.account),
            joinedload(models.Reconciliation.items)
        ).first()
    
    def get_reconciliations(
        self,
        db: Session,
        status: Optional[models.ReconciliationStatus] = None,
        account_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[UUID] = None
    ) -> List[models.Reconciliation]:
        """
        Get a list of reconciliations with optional filters.
        """
        query = db.query(models.Reconciliation).options(
            joinedload(models.Reconciliation.account)
        )
        
        # Apply filters
        if status:
            query = query.filter(models.Reconciliation.status == status)
        if account_id:
            query = query.filter(models.Reconciliation.account_id == account_id)
        if start_date:
            query = query.filter(models.Reconciliation.start_date >= start_date)
        if end_date:
            query = query.filter(models.Reconciliation.end_date <= end_date)
        
        return query.offset(skip).limit(limit).all()
    
    def update_reconciliation(
        self,
        db: Session,
        reconciliation_id: UUID,
        reconciliation_update: schemas.ReconciliationUpdate,
        user_id: UUID
    ) -> Optional[models.Reconciliation]:
        """
        Update a reconciliation.
        ""
        db_reconciliation = self.get_reconciliation(db, reconciliation_id, user_id)
        if not db_reconciliation:
            return None
            
        # Store old values for audit log
        old_values = {
            k: v for k, v in db_reconciliation.__dict__.items()
            if k in reconciliation_update.dict(exclude_unset=True)
        }
        
        # Update fields
        update_data = reconciliation_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_reconciliation, field, value)
        
        db_reconciliation.updated_by = user_id
        db_reconciliation.updated_at = datetime.utcnow()
        
        db.add(db_reconciliation)
        db.commit()
        db.refresh(db_reconciliation)
        
        # Create audit log
        self._create_audit_log(
            db=db,
            reconciliation_id=db_reconciliation.id,
            user_id=user_id,
            action="update",
            details={
                "field": list(update_data.keys()),
                "old_values": old_values,
                "new_values": update_data
            }
        )
        
        return db_reconciliation
    
    def delete_reconciliation(
        self,
        db: Session,
        reconciliation_id: UUID,
        user_id: UUID
    ) -> bool:
        """
        Delete a reconciliation.
        """
        db_reconciliation = self.get_reconciliation(db, reconciliation_id, user_id)
        if not db_reconciliation:
            return False
            
        # Only allow deletion of draft reconciliations
        if db_reconciliation.status != models.ReconciliationStatus.DRAFT:
            raise InvalidReconciliationStateException(
                "Only draft reconciliations can be deleted"
            )
        
        # Create audit log before deletion
        self._create_audit_log(
            db=db,
            reconciliation_id=db_reconciliation.id,
            user_id=user_id,
            action="delete",
            details={"status": db_reconciliation.status}
        )
        
        db.delete(db_reconciliation)
        db.commit()
        return True
    
    def add_reconciliation_item(
        self,
        db: Session,
        reconciliation_id: UUID,
        item: schemas.ReconciliationItemCreate,
        user_id: UUID
    ) -> models.ReconciliationItem:
        """
        Add an item to a reconciliation.
        ""
        # Verify reconciliation exists and is in a valid state
        reconciliation = self.get_reconciliation(db, reconciliation_id, user_id)
        if not reconciliation:
            raise ReconciliationNotFoundException(reconciliation_id)
            
        if reconciliation.status != models.ReconciliationStatus.DRAFT:
            raise InvalidReconciliationStateException(
                "Items can only be added to draft reconciliations"
            )
        
        # Create the item
        db_item = models.ReconciliationItem(
            **item.dict(exclude={"id"}),
            id=uuid4(),
            reconciliation_id=reconciliation_id,
            created_by=user_id,
            updated_by=user_id
        )
        
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        
        # Create audit log
        self._create_audit_log(
            db=db,
            reconciliation_id=reconciliation_id,
            user_id=user_id,
            action="add_item",
            details={"item_id": str(db_item.id)}
        )
        
        return db_item
    
    def update_reconciliation_item(
        self,
        db: Session,
        item_id: UUID,
        item_update: schemas.ReconciliationItemUpdate,
        user_id: UUID
    ) -> Optional[models.ReconciliationItem]:
        """
        Update a reconciliation item.
        ""
        db_item = db.query(models.ReconciliationItem).filter(
            models.ReconciliationItem.id == item_id
        ).first()
        
        if not db_item:
            return None
            
        # Verify reconciliation is in a valid state
        reconciliation = self.get_reconciliation(db, db_item.reconciliation_id, user_id)
        if reconciliation.status != models.ReconciliationStatus.DRAFT:
            raise InvalidReconciliationStateException(
                "Items can only be updated in draft reconciliations"
            )
        
        # Store old values for audit log
        old_values = {
            k: v for k, v in db_item.__dict__.items()
            if k in item_update.dict(exclude_unset=True)
        }
        
        # Update fields
        update_data = item_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_item, field, value)
        
        db_item.updated_by = user_id
        db_item.updated_at = datetime.utcnow()
        
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        
        # Create audit log
        self._create_audit_log(
            db=db,
            reconciliation_id=db_item.reconciliation_id,
            user_id=user_id,
            action="update_item",
            details={
                "item_id": str(item_id),
                "field": list(update_data.keys()),
                "old_values": old_values,
                "new_values": update_data
            }
        )
        
        return db_item
    
    def delete_reconciliation_item(
        self,
        db: Session,
        item_id: UUID,
        user_id: UUID
    ) -> bool:
        """
        Delete a reconciliation item.
        ""
        db_item = db.query(models.ReconciliationItem).filter(
            models.ReconciliationItem.id == item_id
        ).first()
        
        if not db_item:
            return False
            
        # Verify reconciliation is in a valid state
        reconciliation = self.get_reconciliation(db, db_item.reconciliation_id, user_id)
        if reconciliation.status != models.ReconciliationStatus.DRAFT:
            raise InvalidReconciliationStateException(
                "Items can only be deleted from draft reconciliations"
            )
        
        # Create audit log before deletion
        self._create_audit_log(
            db=db,
            reconciliation_id=db_item.reconciliation_id,
            user_id=user_id,
            action="delete_item",
            details={"item_id": str(item_id)}
        )
        
        db.delete(db_item)
        db.commit()
        return True
    
    def complete_reconciliation(
        self,
        db: Session,
        reconciliation_id: UUID,
        user_id: UUID
    ) -> Optional[models.Reconciliation]:
        """
        Complete a reconciliation.
        """
        db_reconciliation = self.get_reconciliation(db, reconciliation_id, user_id)
        if not db_reconciliation:
            return None
            
        if db_reconciliation.status != models.ReconciliationStatus.DRAFT:
            raise InvalidReconciliationStateException(
                "Only draft reconciliations can be completed"
            )
        
        # Verify all items are matched
        unmatched_items = db.query(models.ReconciliationItem).filter(
            models.ReconciliationItem.reconciliation_id == reconciliation_id,
            models.ReconciliationItem.is_matched == False  # noqa: E712
        ).count()
        
        if unmatched_items > 0:
            raise InvalidReconciliationStateException(
                f"Cannot complete reconciliation with {unmatched_items} unmatched items"
            )
        
        # Update status
        db_reconciliation.status = models.ReconciliationStatus.COMPLETED
        db_reconciliation.completed_at = datetime.utcnow()
        db_reconciliation.completed_by = user_id
        db_reconciliation.updated_by = user_id
        db_reconciliation.updated_at = datetime.utcnow()
        
        db.add(db_reconciliation)
        db.commit()
        db.refresh(db_reconciliation)
        
        # Create audit log
        self._create_audit_log(
            db=db,
            reconciliation_id=reconciliation_id,
            user_id=user_id,
            action="complete",
            details={"status": "completed"}
        )
        
        return db_reconciliation
    
    def get_unreconciled_transactions(
        self,
        db: Session,
        account_id: UUID,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Get unreconciled transactions for an account within a date range.
        """
        # Get all journal entries for the account in the date range
        # that are not already included in a reconciliation
        subquery = db.query(
            models.ReconciliationItem.journal_entry_id
        ).filter(
            models.ReconciliationItem.journal_entry_id.isnot(None)
        ).subquery()
        
        # Get unreconciled journal entries
        entries = db.query(
            models.JournalEntryLine
        ).join(
            models.JournalEntry,
            models.JournalEntry.id == models.JournalEntryLine.journal_entry_id
        ).filter(
            models.JournalEntryLine.account_id == account_id,
            models.JournalEntry.entry_date >= start_date,
            models.JournalEntry.entry_date <= end_date,
            models.JournalEntry.status == models.JournalEntryStatus.POSTED,
            ~models.JournalEntryLine.id.in_(subquery)
        ).all()
        
        # Format the results
        result = []
        for entry in entries:
            result.append({
                "id": entry.id,
                "transaction_date": entry.journal_entry.entry_date,
                "reference": entry.journal_entry.reference_number,
                "description": entry.description or entry.journal_entry.description,
                "amount": float(entry.debit - entry.credit) if entry.debit > 0 else float(entry.credit - entry.debit),
                "type": "debit" if entry.debit > 0 else "credit",
                "source_type": "journal_entry",
                "source_id": entry.journal_entry_id
            })
        
        return result
    
    def _create_audit_log(
        self,
        db: Session,
        reconciliation_id: UUID,
        user_id: UUID,
        action: str,
        details: Dict[str, Any]
    ) -> models.ReconciliationAuditLog:
        """
        Create an audit log entry for a reconciliation.
        """
        log = models.ReconciliationAuditLog(
            id=uuid4(),
            reconciliation_id=reconciliation_id,
            user_id=user_id,
            action=action,
            details=details
        )
        
        db.add(log)
        db.commit()
        db.refresh(log)
        return log


# Create a singleton instance
reconciliation_service = ReconciliationService()
