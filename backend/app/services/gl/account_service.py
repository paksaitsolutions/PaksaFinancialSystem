"""
Service layer for Chart of Accounts management.
"""
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID, uuid4

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.core.security import get_password_hash
from app.exceptions import (
    NotFoundException,
    ValidationException,
    BusinessRuleException
)
from app.models.gl_models import (
    ChartOfAccounts,
    AccountType,
    AccountSubType,
    AccountStatus,
    JournalEntryLine,
    LedgerBalance
)
from app.schemas.gl_schemas import (
    AccountCreate,
    AccountUpdate,
    AccountResponse,
    AccountTreeResponse,
    AccountBalanceResponse
)
from app.services.base import BaseService

class AccountService(BaseService):
    """Service for managing Chart of Accounts."""
    
    def __init__(self, db: Session):
        super().__init__(db, ChartOfAccounts)
    
    def create_account(self, account_data: AccountCreate, created_by: UUID) -> AccountResponse:
        """Create a new account in the chart of accounts."""
        # Validate parent account
        if account_data.parent_id:
            parent = self.db.query(ChartOfAccounts).get(account_data.parent_id)
            if not parent:
                raise ValidationException(f"Parent account {account_data.parent_id} not found")
            
            # Ensure parent is not a leaf account
            if parent.account_type in [AccountType.REVENUE, AccountType.EXPENSE, AccountType.GAIN, AccountType.LOSS]:
                raise BusinessRuleException("Cannot create child accounts under a leaf account type")
        
        # Validate account code uniqueness within company
        existing = self.db.query(ChartOfAccounts).filter(
            ChartOfAccounts.code == account_data.code,
            ChartOfAccounts.company_id == account_data.company_id,
            ChartOfAccounts.is_active == True
        ).first()
        
        if existing:
            raise BusinessRuleException(f"Account code {account_data.code} already exists")
        
        # Create the account
        account_dict = account_data.dict(exclude_unset=True)
        account_dict["created_by"] = created_by
        account_dict["updated_by"] = created_by
        
        # Set default values
        if "status" not in account_dict:
            account_dict["status"] = AccountStatus.ACTIVE
        
        # Create the account
        account = ChartOfAccounts(**account_dict)
        self.db.add(account)
        self.db.commit()
        self.db.refresh(account)
        
        return AccountResponse.from_orm(account)
    
    def update_account(
        self, 
        account_id: UUID, 
        account_data: AccountUpdate, 
        updated_by: UUID
    ) -> AccountResponse:
        """Update an existing account."""
        account = self.db.query(ChartOfAccounts).get(account_id)
        if not account or not account.is_active:
            raise NotFoundException(f"Account {account_id} not found")
        
        # Prevent modification of system accounts
        if account.is_system_account:
            raise BusinessRuleException("System accounts cannot be modified")
        
        # Check if account has transactions (restrict certain changes)
        has_transactions = self.db.query(JournalEntryLine.id).filter(
            JournalEntryLine.account_id == account_id
        ).first() is not None
        
        # Validate parent assignment
        if account_data.parent_id is not None:
            if account_data.parent_id == account_id:
                raise ValidationException("Account cannot be its own parent")
                
            parent = self.db.query(ChartOfAccounts).get(account_data.parent_id)
            if not parent:
                raise ValidationException(f"Parent account {account_data.parent_id} not found")
            
            # Prevent circular references
            if self._is_descendant(account_id, account_data.parent_id):
                raise BusinessRuleException("Circular reference detected in account hierarchy")
            
            # Validate account type hierarchy
            if parent.account_type != account_data.account_type:
                raise BusinessRuleException("Parent and child accounts must be of the same type")
        
        # Validate account code uniqueness if being changed
        if account_data.code and account_data.code != account.code:
            existing = self.db.query(ChartOfAccounts).filter(
                ChartOfAccounts.code == account_data.code,
                ChartOfAccounts.company_id == account.company_id,
                ChartOfAccounts.id != account_id,
                ChartOfAccounts.is_active == True
            ).first()
            
            if existing:
                raise BusinessRuleException(f"Account code {account_data.code} already exists")
        
        # Update account fields
        update_data = account_data.dict(exclude_unset=True)
        
        # Protect certain fields from being updated after creation
        if has_transactions:
            protected_fields = ["account_type", "account_subtype", "is_reconcilable"]
            for field in protected_fields:
                if field in update_data and getattr(account, field) != update_data[field]:
                    raise BusinessRuleException(
                        f"Cannot modify {field} for accounts with existing transactions"
                    )
        
        # Apply updates
        for field, value in update_data.items():
            setattr(account, field, value)
        
        account.updated_by = updated_by
        account.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(account)
        
        return AccountResponse.from_orm(account)
    
    def delete_account(self, account_id: UUID, deleted_by: UUID) -> bool:
        """Soft delete an account."""
        account = self.db.query(ChartOfAccounts).get(account_id)
        if not account or not account.is_active:
            raise NotFoundException(f"Account {account_id} not found")
        
        # Prevent deletion of system accounts
        if account.is_system_account:
            raise BusinessRuleException("System accounts cannot be deleted")
        
        # Check for child accounts
        child_count = self.db.query(ChartOfAccounts).filter(
            ChartOfAccounts.parent_id == account_id,
            ChartOfAccounts.is_active == True
        ).count()
        
        if child_count > 0:
            raise BusinessRuleException("Cannot delete an account with active child accounts")
        
        # Check for transactions
        transaction_count = self.db.query(JournalEntryLine.id).filter(
            JournalEntryLine.account_id == account_id
        ).count()
        
        if transaction_count > 0:
            raise BusinessRuleException(
                "Cannot delete an account with existing transactions. "
                "Consider marking it as inactive instead."
            )
        
        # Soft delete the account
        account.is_active = False
        account.updated_by = deleted_by
        account.updated_at = datetime.utcnow()
        
        self.db.commit()
        return True
    
    def get_account_tree(self, company_id: UUID) -> List[AccountTreeResponse]:
        """Get the complete account hierarchy as a tree."""
        # Get all active accounts for the company
        accounts = self.db.query(ChartOfAccounts).filter(
            ChartOfAccounts.company_id == company_id,
            ChartOfAccounts.is_active == True
        ).order_by(ChartOfAccounts.code).all()
        
        # Build a dictionary of accounts by ID
        account_map = {str(account.id): AccountTreeResponse.from_orm(account) for account in accounts}
        
        # Build the tree structure
        root_nodes = []
        
        for account in accounts:
            account_node = account_map[str(account.id)]
            
            if account.parent_id is None:
                # This is a root node
                root_nodes.append(account_node)
            else:
                # Add as a child of the parent
                parent_node = account_map.get(str(account.parent_id))
                if parent_node:
                    if not hasattr(parent_node, 'children'):
                        parent_node.children = []
                    parent_node.children.append(account_node)
        
        return root_nodes
    
    def get_account_balance(
        self, 
        account_id: UUID, 
        as_of_date: Optional[datetime] = None,
        include_children: bool = False
    ) -> AccountBalanceResponse:
        """Get the current balance of an account."""
        account = self.db.query(ChartOfAccounts).get(account_id)
        if not account or not account.is_active:
            raise NotFoundException(f"Account {account_id} not found")
        
        # Build query to get balance
        query = self.db.query(
            func.sum(JournalEntryLine.debit).label("total_debit"),
            func.sum(JournalEntryLine.credit).label("total_credit")
        ).join(
            JournalEntryLine.journal_entry
        ).filter(
            JournalEntryLine.account_id == account_id,
            JournalEntryLine.is_active == True
        )
        
        # Apply date filter if provided
        if as_of_date:
            query = query.filter(JournalEntry.entry_date <= as_of_date)
        
        # Execute query
        result = query.first()
        
        # Calculate balance based on account type
        total_debit = result[0] or Decimal('0')
        total_credit = result[1] or Decimal('0')
        
        if account.account_type in [AccountType.ASSET, AccountType.EXPENSE, AccountType.LOSS]:
            balance = total_debit - total_credit
        else:
            balance = total_credit - total_debit
        
        # Include child accounts if requested
        child_balances = []
        if include_children:
            child_accounts = self.db.query(ChartOfAccounts).filter(
                ChartOfAccounts.parent_id == account_id,
                ChartOfAccounts.is_active == True
            ).all()
            
            for child in child_accounts:
                child_balance = self.get_account_balance(child.id, as_of_date, False)
                child_balances.append(child_balance)
        
        return AccountBalanceResponse(
            account_id=account_id,
            account_code=account.code,
            account_name=account.name,
            account_type=account.account_type,
            currency_code=account.currency_code,
            balance=balance,
            total_debit=total_debit,
            total_credit=total_credit,
            as_of_date=as_of_date or datetime.utcnow().date(),
            children=child_balances or None
        )
    
    def _is_descendant(self, parent_id: UUID, child_id: UUID) -> bool:
        """Check if an account is a descendant of another account."""
        if parent_id == child_id:
            return True
        
        # Get all ancestors of the child
        parent_ids = set()
        current_id = child_id
        
        while current_id:
            account = self.db.query(ChartOfAccounts).get(current_id)
            if not account or not account.parent_id:
                break
                
            if account.parent_id in parent_ids:
                # Circular reference detected
                return False
                
            parent_ids.add(account.parent_id)
            current_id = account.parent_id
        
        return parent_id in parent_ids
