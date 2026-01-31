"""
Reconciliation Item Service

This module provides services for managing reconciliation items.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any, Union

from ...models.journal import JournalEntry, JournalEntryLine, JournalEntryStatus
from ...models.reconciliation import (
from ...schemas.reconciliation import (
from .base import BaseReconciliationService
from decimal import Decimal
from sqlalchemy import and_, or_, func, select
from sqlalchemy.orm import Session, joinedload
from uuid import UUID

from app.core.exceptions import (
from app.core.logging import get_logger



    NotFoundException,
    ValidationException,
    ForbiddenException,
    ConflictException
)

    ReconciliationItem,
    ReconciliationMatchType,
    ReconciliationStatus
)
    ReconciliationItemCreate,
    ReconciliationItemUpdate
)

logger = get_logger(__name__)


class ReconciliationItemService(BaseReconciliationService):
    """Service for handling reconciliation item operations."""
    
    def add_reconciliation_item(
        """Add Reconciliation Item."""
        self, 
        reconciliation_id: UUID, 
        data: ReconciliationItemCreate, 
        user_id: UUID
    ) -> ReconciliationItem:
        """Add Reconciliation Item."""
        """Add an item to a reconciliation.
        
        Args:
            reconciliation_id: ID of the reconciliation
            data: Item data
            user_id: ID of the user adding the item
            
        Returns:
            The created reconciliation item
            
        Raises:
            NotFoundException: If the reconciliation or journal entry doesn't exist
            ForbiddenException: If the user doesn't have permission to modify this reconciliation
            ValidationException: If the item is invalid or the reconciliation is not in a modifiable state
        """
        # Get the reconciliation with a lock to prevent concurrent modifications
        reconciliation = self.db.query(Reconciliation).with_for_update().get(reconciliation_id)
        if not reconciliation:
            raise NotFoundException("Reconciliation not found")
        
        # Check if the user has permission to modify this reconciliation
        if reconciliation.created_by != user_id:
            raise ForbiddenException("You don't have permission to modify this reconciliation")
        
        # Check if the reconciliation can be modified
        if reconciliation.status not in (ReconciliationStatus.DRAFT, ReconciliationStatus.IN_PROGRESS):
            raise ValidationException(
                f"Cannot add items to a reconciliation with status {reconciliation.status}"
            )
        
        # Validate the item
        if data.journal_entry_id and data.journal_entry_line_id:
            # Validate the journal entry line belongs to the journal entry
            je_line = self.db.query(JournalEntryLine).get(data.journal_entry_line_id)
            if not je_line or je_line.journal_entry_id != data.journal_entry_id:
                raise ValidationException("Journal entry line does not belong to the specified journal entry")
            
            # Check if this line is already reconciled
            existing = self.db.query(ReconciliationItem).filter(
                ReconciliationItem.journal_entry_line_id == data.journal_entry_line_id,
                ReconciliationItem.reconciliation_id != reconciliation_id,  # Allow updating existing
                ReconciliationItem.is_matched == True
            ).first()
            
            if existing:
                raise ValidationException(
                    f"This journal entry line is already reconciled in reconciliation {existing.reconciliation.reference}"
                )
            
            # Get the journal entry
            journal_entry = self.db.query(JournalEntry).get(data.journal_entry_id)
            if not journal_entry:
                raise NotFoundException("Journal entry not found")
            
            # Check if the journal entry is in the reconciliation date range
            if journal_entry.entry_date < reconciliation.start_date or journal_entry.entry_date > reconciliation.end_date:
                raise ValidationException(
                    f"Journal entry date {journal_entry.entry_date.date()} is outside the reconciliation period "
                    f"({reconciliation.start_date.date()} to {reconciliation.end_date.date()})"
                )
            
            # Check if the journal entry is posted
            if journal_entry.status != JournalEntryStatus.POSTED:
                raise ValidationException("Cannot reconcile an unposted journal entry")
            
            # Check if the journal entry line is for the reconciliation account
            if je_line.account_id != reconciliation.account_id:
                raise ValidationException(
                    f"Journal entry line account {je_line.account_id} does not match reconciliation account {reconciliation.account_id}"
                )
            
            # Set the amount from the journal entry line
            amount = abs(je_line.amount)
            if je_line.is_debit:
                amount = -amount
            
            # Use the journal entry date as the statement date if not provided
            statement_date = data.statement_line_date or journal_entry.entry_date
            description = data.statement_line_description or journal_entry.description or ""
            
            # Create the reconciliation item
            item = ReconciliationItem(
                id=uuid4(),
                reconciliation_id=reconciliation_id,
                journal_entry_id=data.journal_entry_id,
                journal_entry_line_id=data.journal_entry_line_id,
                statement_line_ref=data.statement_line_ref or f"JE-{journal_entry.reference_number}",
                statement_line_date=statement_date,
                statement_line_description=description,
                statement_line_amount=amount,
                match_type=ReconciliationMatchType.MANUAL,
                is_matched=True,  # Auto-match since we're adding a journal entry line
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        else:
            # This is a statement line without a journal entry (needs to be matched)
            if not data.statement_line_ref or not data.statement_line_date or data.statement_line_amount is None:
                raise ValidationException(
                    "For statement lines, reference, date, and amount are required"
                )
            
            # Create the reconciliation item
            item = ReconciliationItem(
                id=uuid4(),
                reconciliation_id=reconciliation_id,
                statement_line_ref=data.statement_line_ref,
                statement_line_date=data.statement_line_date,
                statement_line_description=data.statement_line_description or "",
                statement_line_amount=data.statement_line_amount,
                match_type=ReconciliationMatchType.MANUAL,
                is_matched=False,  # Needs to be matched with a journal entry
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        
        self.db.add(item)
        
        # Add audit log
        self._add_audit_log(
            reconciliation_id=reconciliation_id,
            action="add_item",
            user_id=user_id,
            details={
                "item_id": str(item.id),
                "journal_entry_id": str(item.journal_entry_id) if item.journal_entry_id else None,
                "journal_entry_line_id": str(item.journal_entry_line_id) if item.journal_entry_line_id else None,
                "statement_line_ref": item.statement_line_ref,
                "statement_line_amount": float(item.statement_line_amount) if item.statement_line_amount else None,
                "is_matched": item.is_matched
            }
        )
        
        # Recalculate the reconciliation
        self._recalculate_reconciliation(reconciliation_id, user_id)
        
        self.db.commit()
        
        return item
    
    def update_reconciliation_item(
        """Update Reconciliation Item."""
        self, 
        item_id: UUID, 
        data: ReconciliationItemUpdate, 
        user_id: UUID
    ) -> ReconciliationItem:
        """Update Reconciliation Item."""
        """Update a reconciliation item.
        
        Args:
            item_id: ID of the item to update
            data: Updated item data
            user_id: ID of the user updating the item
            
        Returns:
            The updated reconciliation item
            
        Raises:
            NotFoundException: If the item doesn't exist
            ForbiddenException: If the user doesn't have permission to modify this item
            ValidationException: If the update is not allowed
        """
        # Get the item with a lock to prevent concurrent modifications
        item = self.db.query(ReconciliationItem).with_for_update().get(item_id)
        if not item:
            raise NotFoundException("Reconciliation item not found")
        
        # Get the reconciliation
        reconciliation = self.db.query(Reconciliation).get(item.reconciliation_id)
        if not reconciliation:
            raise NotFoundException("Reconciliation not found")
        
        # Check if the user has permission to modify this reconciliation
        if reconciliation.created_by != user_id:
            raise ForbiddenException("You don't have permission to modify this reconciliation")
        
        # Check if the reconciliation can be modified
        if reconciliation.status not in (ReconciliationStatus.DRAFT, ReconciliationStatus.IN_PROGRESS):
            raise ValidationException(
                f"Cannot update items in a reconciliation with status {reconciliation.status}"
            )
        
        # Track changes for audit log
        changes = {}
        
        # Update fields if provided
        if data.is_matched is not None and data.is_matched != item.is_matched:
            changes["is_matched"] = data.is_matched
            item.is_matched = data.is_matched
        
        if data.matched_with is not None and data.matched_with != item.matched_with:
            # Validate that the matched_with item exists and is in the same reconciliation
            if data.matched_with:
                matched_item = self.db.query(ReconciliationItem).get(data.matched_with)
                if not matched_item or matched_item.reconciliation_id != reconciliation.id:
                    raise ValidationException("Invalid match reference")
                
                # If matching with another item, ensure they have opposite signs
                if item.statement_line_amount and matched_item.statement_line_amount:
                    if (item.statement_line_amount * matched_item.statement_line_amount) > 0:
                        raise ValidationException(
                            "Cannot match items with the same sign (both positive or both negative)"
                        )
                
                changes["matched_with"] = str(data.matched_with)
                item.matched_with = data.matched_with
                
                # Auto-set is_matched to True when matched_with is set
                if not item.is_matched:
                    item.is_matched = True
                    changes["is_matched"] = True
            else:
                changes["matched_with"] = None
                item.matched_with = None
        
        if data.notes is not None and data.notes != item.notes:
            changes["notes"] = data.notes
            item.notes = data.notes
        
        if changes:
            item.updated_at = datetime.utcnow()
            
            # Add audit log
            self._add_audit_log(
                reconciliation_id=reconciliation.id,
                action="update_item",
                user_id=user_id,
                details={
                    "item_id": str(item_id),
                    **changes
                }
            )
            
            # Recalculate the reconciliation
            self._recalculate_reconciliation(reconciliation.id, user_id)
            
            self.db.commit()
        
        return item
    
    def delete_reconciliation_item(self, item_id: UUID, user_id: UUID) -> bool:
        """Delete Reconciliation Item."""
        """Delete a reconciliation item.
        
        Args:
            item_id: ID of the item to delete
            user_id: ID of the user deleting the item
            
        Returns:
            True if the item was deleted
            
        Raises:
            NotFoundException: If the item doesn't exist
            ForbiddenException: If the user doesn't have permission to delete this item
            ValidationException: If the item cannot be deleted in the current state
        """
        # Get the item with a lock to prevent concurrent modifications
        item = self.db.query(ReconciliationItem).with_for_update().get(item_id)
        if not item:
            raise NotFoundException("Reconciliation item not found")
        
        # Get the reconciliation
        reconciliation = self.db.query(Reconciliation).get(item.reconciliation_id)
        if not reconciliation:
            raise NotFoundException("Reconciliation not found")
        
        # Check if the user has permission to modify this reconciliation
        if reconciliation.created_by != user_id:
            raise ForbiddenException("You don't have permission to modify this reconciliation")
        
        # Check if the reconciliation can be modified
        if reconciliation.status not in (ReconciliationStatus.DRAFT, ReconciliationStatus.IN_PROGRESS):
            raise ValidationException(
                f"Cannot delete items from a reconciliation with status {reconciliation.status}"
            )
        
        reconciliation_id = reconciliation.id
        
        # Add audit log before deletion
        self._add_audit_log(
            reconciliation_id=reconciliation_id,
            action="delete_item",
            user_id=user_id,
            details={
                "item_id": str(item_id),
                "journal_entry_id": str(item.journal_entry_id) if item.journal_entry_id else None,
                "journal_entry_line_id": str(item.journal_entry_line_id) if item.journal_entry_line_id else None,
                "statement_line_ref": item.statement_line_ref,
                "statement_line_amount": float(item.statement_line_amount) if item.statement_line_amount else None
            }
        )
        
        # Delete the item
        self.db.delete(item)
        
        # Recalculate the reconciliation
        self._recalculate_reconciliation(reconciliation_id, user_id)
        
        self.db.commit()
        
        return True
