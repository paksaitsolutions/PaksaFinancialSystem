"""
Reconciliation Rule Service

This module provides services for managing reconciliation rules.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any, Union

from ...models.account import Account
from ...models.reconciliation import (
from ...schemas.reconciliation import (
from .base import BaseReconciliationService
from decimal import Decimal
from sqlalchemy import and_, or_, func, select, text
from sqlalchemy.orm import Session, joinedload
from uuid import UUID

from app.core.exceptions import (
from app.core.logging import get_logger



    NotFoundException,
    ValidationException,
    ForbiddenException,
    ConflictException
)

    ReconciliationRule,
    ReconciliationRuleCondition,
    ReconciliationRuleAction,
    ReconciliationRuleStatus,
    ReconciliationRuleConditionType,
    ReconciliationRuleActionType,
    ReconciliationRuleFieldType,
    ReconciliationMatchType
)
    ReconciliationRuleCreate,
    ReconciliationRuleUpdate,
    ReconciliationRuleConditionCreate,
    ReconciliationRuleConditionUpdate,
    ReconciliationRuleActionCreate,
    ReconciliationRuleActionUpdate
)

logger = get_logger(__name__)


class ReconciliationRuleService(BaseReconciliationService):
    """Service for handling reconciliation rule operations."""
    
    # Rule CRUD Operations
    
    def get_rule(self, rule_id: UUID, user_id: UUID) -> ReconciliationRule:
        """Get Rule."""
        """Get a reconciliation rule by ID with permission check.
        
        Args:
            rule_id: ID of the rule to retrieve
            user_id: ID of the user making the request
            
        Returns:
            The reconciliation rule with conditions and actions
            
        Raises:
            NotFoundException: If the rule doesn't exist
            ForbiddenException: If the user doesn't have permission to view this rule
        """
        rule = (
            self.db.query(ReconciliationRule)
            .options(
                joinedload(ReconciliationRule.conditions),
                joinedload(ReconciliationRule.actions)
            )
            .filter(ReconciliationRule.id == rule_id)
            .first()
        )
        
        if not rule:
            raise NotFoundException("Reconciliation rule not found")
            
        # For now, just check if the user created the rule
        if rule.created_by != user_id:
            raise ForbiddenException("You don't have permission to access this rule")
            
        return rule
    
    def list_rules(
        self,
        user_id: UUID,
        account_id: Optional[UUID] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[ReconciliationRule], int]:
        """List Rules."""
        """List reconciliation rules with optional filtering.
        
        Args:
            user_id: ID of the user making the request
            account_id: Filter by account ID
            is_active: Filter by active status
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return
            
        Returns:
            Tuple of (list of rules, total count)
        """
        query = self.db.query(ReconciliationRule)
        
        # Apply filters
        # For now, just filter by created_by
        query = query.filter(ReconciliationRule.created_by == user_id)
        
        if account_id is not None:
            query = query.filter(ReconciliationRule.account_id == account_id)
            
        if is_active is not None:
            query = query.filter(ReconciliationRule.is_active == is_active)
        
        # Order by priority (ascending) and then by name
        query = query.order_by(
            ReconciliationRule.priority.asc(),
            ReconciliationRule.name.asc()
        )
        
        # Get total count
        total = query.count()
        
        # Apply pagination and eager loading
        rules = (
            query.options(
                joinedload(ReconciliationRule.conditions),
                joinedload(ReconciliationRule.actions)
            )
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        return rules, total
    
    def create_rule(self, data: ReconciliationRuleCreate, user_id: UUID) -> ReconciliationRule:
        """Create Rule."""
        """Create a new reconciliation rule.
        
        Args:
            data: Rule data
            user_id: ID of the user creating the rule
            
        Returns:
            The created reconciliation rule
            
        Raises:
            NotFoundException: If the account doesn't exist
            ValidationException: If the data is invalid
        """
        # Verify the account exists and is active if specified
        if data.account_id:
            account = self.account_service.get_account(data.account_id)
            if not account.is_active:
                raise ValidationException("Cannot create a rule for an inactive account")
        
        # Check for duplicate rule name for the same account
        existing = self.db.query(ReconciliationRule).filter(
            ReconciliationRule.name == data.name,
            ReconciliationRule.account_id == data.account_id,
            ReconciliationRule.deleted_at.is_(None)
        ).first()
        
        if existing:
            raise ValidationException(
                f"A rule with the name '{data.name}' already exists for this account"
            )
        
        # Create the rule
        rule = ReconciliationRule(
            id=uuid4(),
            name=data.name,
            description=data.description,
            account_id=data.account_id,
            priority=data.priority or 100,
            match_type=data.match_type or ReconciliationMatchType.AUTO,
            is_active=data.is_active if data.is_active is not None else True,
            created_by=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.db.add(rule)
        self.db.flush()  # Get the rule ID for conditions/actions
        
        # Add conditions
        if data.conditions:
            for cond_data in data.conditions:
                condition = ReconciliationRuleCondition(
                    id=uuid4(),
                    rule_id=rule.id,
                    condition_type=cond_data.condition_type,
                    field_type=cond_data.field_type,
                    field_name=cond_data.field_name,
                    operator=cond_data.operator,
                    value=cond_data.value,
                    value_type=cond_data.value_type,
                    is_case_sensitive=cond_data.is_case_sensitive or False,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                self.db.add(condition)
        
        # Add actions
        if data.actions:
            for action_data in data.actions:
                action = ReconciliationRuleAction(
                    id=uuid4(),
                    rule_id=rule.id,
                    action_type=action_data.action_type,
                    field_name=action_data.field_name,
                    field_value=action_data.field_value,
                    field_value_type=action_data.field_value_type,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                self.db.add(action)
        
        # Add audit log
        self._add_audit_log(
            reconciliation_id=None,
            action="create_rule",
            user_id=user_id,
            details={
                "rule_id": str(rule.id),
                "name": rule.name,
                "account_id": str(rule.account_id) if rule.account_id else None,
                "match_type": rule.match_type,
                "is_active": rule.is_active,
                "condition_count": len(data.conditions or []),
                "action_count": len(data.actions or [])
            }
        )
        
        self.db.commit()
        
        # Refresh to load relationships
        self.db.refresh(rule)
        
        return rule
    
    def update_rule(
        self, 
        rule_id: UUID, 
        data: ReconciliationRuleUpdate, 
        user_id: UUID
    ) -> ReconciliationRule:
        """Update Rule."""
        """Update a reconciliation rule.
        
        Args:
            rule_id: ID of the rule to update
            data: Updated rule data
            user_id: ID of the user updating the rule
            
        Returns:
            The updated reconciliation rule
            
        Raises:
            NotFoundException: If the rule doesn't exist
            ForbiddenException: If the user doesn't have permission to update this rule
            ValidationException: If the update is not allowed
        """
        # Get the rule with a lock to prevent concurrent modifications
        rule = (
            self.db.query(ReconciliationRule)
            .with_for_update()
            .filter(ReconciliationRule.id == rule_id)
            .first()
        )
        
        if not rule:
            raise NotFoundException("Reconciliation rule not found")
            
        # Check if the user has permission to update this rule
        if rule.created_by != user_id:
            raise ForbiddenException("You don't have permission to update this rule")
        
        # Track changes for audit log
        changes = {}
        
        # Update fields if provided
        if data.name is not None and data.name != rule.name:
            # Check for duplicate name
            existing = self.db.query(ReconciliationRule).filter(
                ReconciliationRule.name == data.name,
                ReconciliationRule.account_id == rule.account_id,
                ReconciliationRule.id != rule_id,
                ReconciliationRule.deleted_at.is_(None)
            ).first()
            
            if existing:
                raise ValidationException(
                    f"A rule with the name '{data.name}' already exists for this account"
                )
            
            changes["name"] = {"old": rule.name, "new": data.name}
            rule.name = data.name
        
        if data.description is not None and data.description != rule.description:
            changes["description"] = {"old": rule.description, "new": data.description}
            rule.description = data.description
            
        if data.priority is not None and data.priority != rule.priority:
            changes["priority"] = {"old": rule.priority, "new": data.priority}
            rule.priority = data.priority
            
        if data.match_type is not None and data.match_type != rule.match_type:
            changes["match_type"] = {"old": rule.match_type, "new": data.match_type}
            rule.match_type = data.match_type
            
        if data.is_active is not None and data.is_active != rule.is_active:
            changes["is_active"] = {"old": rule.is_active, "new": data.is_active}
            rule.is_active = data.is_active
        
        # Update timestamps
        rule.updated_at = datetime.utcnow()
        
        # Update conditions if provided
        if data.conditions is not None:
            # Delete existing conditions
            self.db.query(ReconciliationRuleCondition).filter(
                ReconciliationRuleCondition.rule_id == rule_id
            ).delete(synchronize_session=False)
            
            # Add new conditions
            for cond_data in data.conditions:
                condition = ReconciliationRuleCondition(
                    id=uuid4(),
                    rule_id=rule_id,
                    condition_type=cond_data.condition_type,
                    field_type=cond_data.field_type,
                    field_name=cond_data.field_name,
                    operator=cond_data.operator,
                    value=cond_data.value,
                    value_type=cond_data.value_type,
                    is_case_sensitive=cond_data.is_case_sensitive or False,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                self.db.add(condition)
            
            changes["conditions_updated"] = True
        
        # Update actions if provided
        if data.actions is not None:
            # Delete existing actions
            self.db.query(ReconciliationRuleAction).filter(
                ReconciliationRuleAction.rule_id == rule_id
            ).delete(synchronize_session=False)
            
            # Add new actions
            for action_data in data.actions:
                action = ReconciliationRuleAction(
                    id=uuid4(),
                    rule_id=rule_id,
                    action_type=action_data.action_type,
                    field_name=action_data.field_name,
                    field_value=action_data.field_value,
                    field_value_type=action_data.field_value_type,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                self.db.add(action)
            
            changes["actions_updated"] = True
        
        # Add audit log if there were changes
        if changes:
            self._add_audit_log(
                reconciliation_id=None,
                action="update_rule",
                user_id=user_id,
                details={
                    "rule_id": str(rule_id),
                    "changes": changes
                }
            )
        
        self.db.commit()
        
        # Refresh to load relationships
        self.db.refresh(rule)
        
        return rule
    
    def delete_rule(self, rule_id: UUID, user_id: UUID) -> bool:
        """Delete Rule."""
        """Delete a reconciliation rule.
        
        Args:
            rule_id: ID of the rule to delete
            user_id: ID of the user deleting the rule
            
        Returns:
            True if the rule was deleted
            
        Raises:
            NotFoundException: If the rule doesn't exist
            ForbiddenException: If the user doesn't have permission to delete this rule
        """
        # Get the rule with a lock to prevent concurrent modifications
        rule = (
            self.db.query(ReconciliationRule)
            .with_for_update()
            .filter(ReconciliationRule.id == rule_id)
            .first()
        )
        
        if not rule:
            raise NotFoundException("Reconciliation rule not found")
            
        # Check if the user has permission to delete this rule
        if rule.created_by != user_id:
            raise ForbiddenException("You don't have permission to delete this rule")
        
        # Soft delete the rule
        rule.deleted_at = datetime.utcnow()
        rule.updated_at = datetime.utcnow()
        
        # Add audit log
        self._add_audit_log(
            reconciliation_id=None,
            action="delete_rule",
            user_id=user_id,
            details={
                "rule_id": str(rule_id),
                "name": rule.name,
                "account_id": str(rule.account_id) if rule.account_id else None
            }
        )
        
        self.db.commit()
        
        return True
