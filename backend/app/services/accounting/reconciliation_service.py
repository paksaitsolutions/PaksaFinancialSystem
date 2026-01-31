"""
Reconciliation Service

This module provides services for managing account reconciliations.
"""
from typing import Any, Dict, List, Optional, Type, TypeVar

from .. import models, schemas
from ..exceptions import (
from .account_balance_service import AccountBalanceService
from sqlalchemy import and_, or_, func, select
from sqlalchemy.orm import Session, joinedload
from uuid import UUID

from app.services.audit.audit_service import AuditService
from app.services.base import BaseService



    AccountNotFoundException,
    InvalidReconciliationStateException,
    JournalEntryNotFoundException,
    ReconciliationItemNotFoundException,
    ReconciliationNotFoundException,
)


class ReconciliationService(BaseService[models.Reconciliation, schemas.ReconciliationCreate, schemas.ReconciliationUpdate]):
    """Service for managing account reconciliations."""
    
    def __init__(self, db: Optional[Session] = None):
        """  Init  ."""
        """
        Initialize the service with an optional database session.
        
        Args:
            db: Optional database session. If not provided, a new one will be created.
        """
        super().__init__(models.Reconciliation)
        self.db = db
        self.audit_service = AuditService(db or self._get_db())
        self.balance_service = AccountBalanceService(db)
    
    def _get_db(self) -> Session:
        """ Get Db."""
        """Get a database session."""
        if self.db is None:
            from app.core.database import SessionLocal
            self.db = SessionLocal()
        return self.db
    
    def _get_reconciliation_or_404(self, reconciliation_id: UUID) -> models.Reconciliation:
        """ Get Reconciliation Or 404."""
        """Get a reconciliation by ID or raise appropriate exception."""
        return self._get_or_404(
            self._get_db(), 
            models.Reconciliation, 
            reconciliation_id,
            ReconciliationNotFoundException(reconciliation_id)
        )
    
    def _get_reconciliation_item_or_404(self, item_id: UUID) -> models.ReconciliationItem:
        """ Get Reconciliation Item Or 404."""
        """Get a reconciliation item by ID or raise appropriate exception."""
        return self._get_or_404(
            self._get_db(),
            models.ReconciliationItem,
            item_id,
            ReconciliationItemNotFoundException(item_id)
        )
    
    def _get_account_or_404(self, account_id: UUID) -> models.Account:
        """ Get Account Or 404."""
        """Get an account by ID or raise appropriate exception."""
        return self._get_or_404(
            self._get_db(),
            models.Account,
            account_id,
            AccountNotFoundException(account_id)
        )
        
    def _validate_reconciliation_state(
        """ Validate Reconciliation State."""
        self, 
        reconciliation: models.Reconciliation, 
        required_status: Optional[models.ReconciliationStatus] = None,
        check_items: bool = False
    ) -> None:
        """ Validate Reconciliation State."""
        """
        Validate reconciliation state.
        
        Args:
            reconciliation: The reconciliation to validate
            required_status: If provided, the reconciliation must be in this state
            check_items: If True, check for unmatched items when status is COMPLETED
            
        Raises:
            InvalidReconciliationStateException: If validation fails
        """
        if required_status and reconciliation.status != required_status:
            raise InvalidReconciliationStateException(
                f"Reconciliation must be in {required_status} state"
            )
            
        if check_items and reconciliation.status == models.ReconciliationStatus.COMPLETED:
            # Check for unmatched items only if reconciliation is being completed
            unmatched_items = self._count_unmatched_items(reconciliation.id)
            if unmatched_items > 0:
                raise InvalidReconciliationStateException(
                    f"Cannot complete reconciliation with {unmatched_items} unmatched items"
                )
    
    def _count_unmatched_items(self, reconciliation_id: UUID) -> int:
        """ Count Unmatched Items."""
        """
        Count unmatched items for a reconciliation.
        
        Args:
            reconciliation_id: ID of the reconciliation
            
        Returns:
            int: Number of unmatched items
        """
        db = self._get_db()
        return db.query(models.ReconciliationItem).filter(
            models.ReconciliationItem.reconciliation_id == reconciliation_id,
            models.ReconciliationItem.is_matched == False  # noqa: E712
        ).count()
        
    def _create_audit_log(
        """ Create Audit Log."""
        self,
        reconciliation_id: UUID,
        user_id: UUID,
        action: str,
        details: Dict[str, Any]
    ) -> None:
        """ Create Audit Log."""
        """
        Create an audit log entry for a reconciliation.
        
        Args:
            reconciliation_id: ID of the reconciliation
            user_id: ID of the user performing the action
            action: Action being performed
            details: Additional details about the action
            
        Returns:
            The created audit log entry
        """
        db = self._get_db()
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
    def create_reconciliation(
        """Create Reconciliation."""
        self,
        reconciliation: schemas.ReconciliationCreate,
        user_id: UUID
    ) -> models.Reconciliation:
        """Create Reconciliation."""
        """
        Create a new reconciliation.
        
        Args:
            reconciliation: Reconciliation data to create
            user_id: ID of the user creating the reconciliation
            
        Returns:
            The created reconciliation
        """
        db = self._get_db()
        
        # Create the reconciliation record
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
        
        # Log the creation using the audit service
        self.audit_service.log_action(
            action="reconciliation.create",
            resource_type="reconciliation",
            user_id=user_id,
            resource_id=str(db_reconciliation.id),
            new_values={"status": db_reconciliation.status.value}
        )
        
        return db_reconciliation
    
    def get_reconciliation(
        """Get Reconciliation."""
        self,
        reconciliation_id: UUID,
        user_id: UUID
    ) -> Optional[models.Reconciliation]:
        """Get Reconciliation."""
        """
        Get a reconciliation by ID with related data.
        
        Args:
            reconciliation_id: ID of the reconciliation to retrieve
            user_id: ID of the user making the request
            
        Returns:
            The reconciliation with account and items loaded, or None if not found
        """
        db = self._get_db()
        return db.query(models.Reconciliation).filter(
            models.Reconciliation.id == reconciliation_id
        ).options(
            joinedload(models.Reconciliation.account),
            joinedload(models.Reconciliation.items)
        ).first()
    
    def get_reconciliations(
        """Get Reconciliations."""
        self,
        user_id: UUID,
        account_id: Optional[UUID] = None,
        status: Optional[models.ReconciliationStatus] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[models.Reconciliation]:
        """Get Reconciliations."""
        """
        Get a list of reconciliations with optional filtering.
        
        Args:
            user_id: ID of the user making the request
            account_id: Optional account ID to filter by
            status: Optional status to filter by
            start_date: Optional start date to filter reconciliations
            end_date: Optional end date to filter reconciliations
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return (for pagination)
            
        Returns:
            List of reconciliation records with account information
        """
        db = self._get_db()
        query = db.query(models.Reconciliation)
        
        # Apply filters
        if account_id:
            query = query.filter(models.Reconciliation.account_id == account_id)
            
        if status:
            query = query.filter(models.Reconciliation.status == status)
            
        if start_date:
            query = query.filter(models.Reconciliation.statement_date >= start_date)
            
        if end_date:
            # Include the entire end date
            end_date = end_date.replace(hour=23, minute=59, second=59)
            query = query.filter(models.Reconciliation.statement_date <= end_date)
            
        return query.options(
            joinedload(models.Reconciliation.account)
        ).order_by(
            models.Reconciliation.statement_date.desc()
        ).offset(skip).limit(limit).all()
    
    def update_reconciliation(
        """Update Reconciliation."""
        self,
        reconciliation_id: UUID,
        reconciliation_update: schemas.ReconciliationUpdate,
        user_id: UUID
    ) -> models.Reconciliation:
        """Update Reconciliation."""
        """
        Update a reconciliation.
        
        Args:
            reconciliation_id: ID of the reconciliation to update
            reconciliation_update: Data to update the reconciliation with
            user_id: ID of the user performing the update
            
        Returns:
            The updated reconciliation record
            
        Raises:
            HTTPException: If reconciliation is not found or not in a valid state for update
        """
        db = self._get_db()
        db_reconciliation = self._get_or_404(db, models.Reconciliation, reconciliation_id)
        
        # Store old values for audit log
        update_data = reconciliation_update.dict(exclude_unset=True)
        old_values = {
            k: getattr(db_reconciliation, k) 
            for k in update_data.keys()
            if hasattr(db_reconciliation, k)
        }
        
        # Validate reconciliation state before update
        self._validate_reconciliation_state(
            db_reconciliation,
            check_items=False
        )
        
        # Update the record
        db_reconciliation.updated_by = user_id
        db_reconciliation.updated_at = datetime.utcnow()
        
        for field, value in update_data.items():
            if hasattr(db_reconciliation, field):
                setattr(db_reconciliation, field, value)
        
        db.add(db_reconciliation)
        db.commit()
        db.refresh(db_reconciliation)
        
        # Log the update action
        self.audit_service.log_action(
            action="reconciliation.update",
            resource_type="reconciliation",
            user_id=user_id,
            resource_id=str(reconciliation_id),
            old_values=old_values,
            new_values=update_data
        )
        
        return db_reconciliation
    
    def delete_reconciliation(
        """Delete Reconciliation."""
        self,
        reconciliation_id: UUID,
        user_id: UUID
    ) -> bool:
        """Delete Reconciliation."""
        """
        Delete a reconciliation.
        
        Args:
            reconciliation_id: ID of the reconciliation to delete
            user_id: ID of the user performing the deletion
            
        Returns:
            bool: True if deletion was successful
            
        Raises:
            HTTPException: If reconciliation is not found or not in a valid state for deletion
        """
        db = self._get_db()
        db_reconciliation = self._get_or_404(db, models.Reconciliation, reconciliation_id)
        
        # Validate state before deletion
        self._validate_reconciliation_state(db_reconciliation)
        
        # Store data for audit log before deletion
        reconciliation_data = {
            'account_id': str(db_reconciliation.account_id),
            'statement_date': db_reconciliation.statement_date.isoformat(),
            'status': db_reconciliation.status.value
        }
        
        # Log the deletion action
        self.audit_service.log_action(
            action="reconciliation.delete",
            resource_type="reconciliation",
            user_id=user_id,
            resource_id=str(reconciliation_id),
            old_values=reconciliation_data
        )
        
        # Delete the reconciliation
        db.delete(db_reconciliation)
        db.commit()
        
        return True
    
    def add_reconciliation_item(
        """Add Reconciliation Item."""
        self,
        reconciliation_id: UUID,
        item: schemas.ReconciliationItemCreate,
        user_id: UUID
    ) -> models.ReconciliationItem:
        """Add Reconciliation Item."""
        """
        Add an item to a reconciliation.
        
        Args:
            reconciliation_id: ID of the reconciliation to add the item to
            item: Data for the new reconciliation item
            user_id: ID of the user adding the item
            
        Returns:
            The created reconciliation item
            
        Raises:
            HTTPException: If reconciliation is not found or not in a valid state for modification
        """
        db = self._get_db()
        
        # Get the reconciliation
        reconciliation = self._get_reconciliation_or_404(reconciliation_id)
        
        # Validate reconciliation state
        self._validate_reconciliation_state(reconciliation)
        
        # Create the item
        db_item = models.ReconciliationItem(
            **item.dict(),
            id=uuid4(),
            reconciliation_id=reconciliation_id,
            created_by=user_id,
            updated_by=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        
        # Log the item addition
        self.audit_service.log_action(
            action="reconciliation.item.add",
            resource_type="reconciliation_item",
            user_id=user_id,
            resource_id=str(db_item.id),
            parent_resource_type="reconciliation",
            parent_resource_id=str(reconciliation_id),
            new_values={
                "item_type": db_item.item_type.value,
                "amount": float(db_item.amount),
                "transaction_date": db_item.transaction_date.isoformat() if db_item.transaction_date else None,
                "description": db_item.description
            }
        )
        
        return db_item
    
    def update_reconciliation_item(
        """Update Reconciliation Item."""
        self,
        item_id: UUID,
        item_update: schemas.ReconciliationItemUpdate,
        user_id: UUID
    ) -> models.ReconciliationItem:
        """Update Reconciliation Item."""
        """
        Update a reconciliation item.
        
        Args:
            item_id: ID of the item to update
            item_update: Data to update the item with
            user_id: ID of the user performing the update
            
        Returns:
            The updated reconciliation item
            
        Raises:
            HTTPException: If item or its reconciliation is not found or not in a valid state for modification
        """
        db = self._get_db()
        
        # Get the item and its reconciliation
        db_item = self._get_reconciliation_item_or_404(item_id)
        reconciliation = self._get_reconciliation_or_404(db_item.reconciliation_id)
        
        # Validate reconciliation state
        self._validate_reconciliation_state(reconciliation)
        
        # Store old values for audit log
        update_data = item_update.dict(exclude_unset=True)
        old_values = {
            k: getattr(db_item, k) 
            for k in update_data.keys()
            if hasattr(db_item, k)
        }
        
        # Update the item
        for field, value in update_data.items():
            if hasattr(db_item, field):
                setattr(db_item, field, value)
        
        db_item.updated_by = user_id
        db_item.updated_at = datetime.utcnow()
        
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        
        # Log the item update
        self.audit_service.log_action(
            action="reconciliation.item.update",
            resource_type="reconciliation_item",
            user_id=user_id,
            resource_id=str(item_id),
            parent_resource_type="reconciliation",
            parent_resource_id=str(db_item.reconciliation_id),
            old_values=old_values,
            new_values={
                k: v.isoformat() if hasattr(v, 'isoformat') and callable(v.isoformat) 
                else v for k, v in update_data.items()
            }
        )
        
        # Delete the item
        db.delete(db_item)
        db.commit()

    def complete_reconciliation(
        """Complete Reconciliation."""
        self,
        reconciliation_id: UUID,
        user_id: UUID
    ) -> models.Reconciliation:
        """Complete Reconciliation."""
        """
        Mark a reconciliation as completed.
        
        Args:
            reconciliation_id: ID of the reconciliation to complete
            user_id: ID of the user completing the reconciliation
            
        Returns:
            The completed reconciliation record
            
        Raises:
            HTTPException: If reconciliation is not found, not in DRAFT status, or has unmatched items
        """
        db = self._get_db()
        db_reconciliation = self._get_or_404(db, models.Reconciliation, reconciliation_id)
        
        # Validate reconciliation can be completed
        self._validate_reconciliation_state(
            db_reconciliation,
            required_status=models.ReconciliationStatus.DRAFT,
            check_items=True  # This will check for unmatched items
        )
        
        # Store old values for audit log
        old_status = db_reconciliation.status
        
        # Update reconciliation status
        db_reconciliation.status = models.ReconciliationStatus.COMPLETED
        db_reconciliation.completed_by = user_id
        db_reconciliation.completed_at = datetime.utcnow()
        db_reconciliation.updated_by = user_id
        db_reconciliation.updated_at = datetime.utcnow()
        
        db.add(db_reconciliation)
        db.commit()
        db.refresh(db_reconciliation)
        
        # Log the completion
        self.audit_service.log_action(
            action="reconciliation.complete",
            resource_type="reconciliation",
            user_id=user_id,
            resource_id=str(reconciliation_id),
            old_values={"status": old_status.value},
            new_values={
                "status": db_reconciliation.status.value,
                "completed_at": db_reconciliation.completed_at.isoformat(),
                "completed_by": str(user_id)
            }
        )
        
        return db_reconciliation
    
    def get_unreconciled_transactions(
        """Get Unreconciled Transactions."""
        self,
        account_id: UUID,
        start_date: datetime,
        end_date: datetime,
        user_id: UUID
    ) -> List[Dict[str, Any]]:
        """Get Unreconciled Transactions."""
        """
        Get unreconciled transactions for an account within a date range.
        
        Args:
            account_id: ID of the account to get transactions for
            start_date: Start of the date range (inclusive)
            end_date: End of the date range (inclusive)
            user_id: ID of the user making the request (for audit purposes)
            
        Returns:
            List of dictionaries containing transaction details
            
        Raises:
            HTTPException: If account is not found
        """
        db = self._get_db()
        
        # Verify account exists
        self._get_account_or_404(account_id)
        
        # Log the query for audit purposes
        self.audit_service.log_action(
            action="reconciliation.transactions.query",
            resource_type="account",
            resource_id=str(account_id),
            user_id=user_id,
            details={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "status": "unreconciled"
            }
        )
        
        # Get all transactions for the account in the date range
        transactions = db.query(models.Transaction).filter(
            models.Transaction.account_id == account_id,
            models.Transaction.transaction_date.between(start_date, end_date),
            models.Transaction.reconciled == False  # noqa: E712
        ).order_by(
            models.Transaction.transaction_date.asc()
        ).all()
        
        return [
            {
                "id": str(txn.id),
                "transaction_date": txn.transaction_date.isoformat(),
                "amount": float(txn.amount),
                "description": txn.description,
                "reference": txn.reference,
                "transaction_type": txn.transaction_type.value,
                "created_at": txn.created_at.isoformat() if txn.created_at else None,
                "updated_at": txn.updated_at.isoformat() if txn.updated_at else None
            }
            for txn in transactions
        ]


# Create a singleton instance
reconciliation_service = ReconciliationService()
