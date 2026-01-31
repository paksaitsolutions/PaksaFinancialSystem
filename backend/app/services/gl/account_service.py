"""
Service layer for Chart of Accounts management.
"""
from datetime import datetime, date
from typing import List, Optional, Tuple, Dict, Any, Set

from decimal import Decimal, ROUND_HALF_UP
from sqlalchemy import func, and_, or_, case, select
from sqlalchemy.orm import Session, joinedload
from uuid import UUID, uuid4

from app.core.security import get_password_hash
from app.exceptions import (
from app.models.gl_models import (
from app.schemas.gl_schemas import (
from app.services.base import BaseService



    NotFoundException,
    ValidationException,
    BusinessRuleException
)
    ChartOfAccounts,
    AccountType,
    AccountSubType,
    AccountStatus,
    JournalEntryLine,
    LedgerBalance
)
    AccountCreate,
    AccountUpdate,
    AccountResponse,
    AccountTreeResponse,
    AccountBalanceResponse
)

class AccountService(BaseService):
    """Service for managing Chart of Accounts."""
    
    def __init__(self, db: Session):
        """  Init  ."""
        super().__init__(db, ChartOfAccounts)
    
    def _validate_account_creation(self, account_data: AccountCreate) -> None:
        """ Validate Account Creation."""
        """Validate account creation data."""
        # Validate account type and sub-type compatibility
        if account_data.account_type == AccountType.ASSET:
            if account_data.sub_type not in [
                AccountSubType.CURRENT_ASSET, 
                AccountSubType.FIXED_ASSET,
                AccountSubType.INVENTORY,
                AccountSubType.RECEIVABLE,
                AccountSubType.BANK,
                AccountSubType.CASH
            ]:
                raise ValidationException(f"Invalid sub-type {account_data.sub_type} for asset account")
        
        # Add more validations for other account types...

    def _validate_account_code(self, code: str, company_id: UUID, account_id: UUID = None) -> None:
        """ Validate Account Code."""
        """Validate account code uniqueness within company."""
        query = self.db.query(ChartOfAccounts).filter(
            ChartOfAccounts.code == code,
            ChartOfAccounts.company_id == company_id,
            ChartOfAccounts.is_active == True
        )
        
        if account_id:
            query = query.filter(ChartOfAccounts.id != account_id)
        
        if query.first():
            raise BusinessRuleException(f"Account code {code} already exists in this company")

    def _get_account_balance_query(self, account_id: UUID, as_of_date: date = None):
        """ Get Account Balance Query."""
        """Build a query to calculate account balance."""
        # Base query for journal entries
        query = self.db.query(
            func.coalesce(
                func.sum(
                    case(
                        [(JournalEntryLine.type == 'debit', JournalEntryLine.amount)],
                        else_=0
                    )
                ),
                0
            ) - func.coalesce(
                func.sum(
                    case(
                        [(JournalEntryLine.type == 'credit', JournalEntryLine.amount)],
                        else_=0
                    )
                ),
                0
            )
        ).filter(
            JournalEntryLine.account_id == account_id,
            JournalEntryLine.is_active == True
        )
        
        # Apply date filter if provided
        if as_of_date:
            query = query.filter(JournalEntryLine.entry_date <= as_of_date)
        
        return query

    def get_account_balance(self, account_id: UUID, as_of_date: date = None) -> Decimal:
        """Get Account Balance."""
        """Get the current balance of an account."""
        account = self.db.query(ChartOfAccounts).get(account_id)
        if not account or not account.is_active:
            raise NotFoundException(f"Account {account_id} not found")
        
        balance = self._get_account_balance_query(account_id, as_of_date).scalar() or Decimal('0')
        
        # For parent accounts, include children balances
        if not account.is_leaf:
            children_balance = self.get_children_balance(account_id, as_of_date)
            balance += children_balance
        
        return balance.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def get_children_balance(self, parent_id: UUID, as_of_date: date = None) -> Decimal:
        """Get Children Balance."""
        """Calculate the total balance of all child accounts."""
        children = self.db.query(ChartOfAccounts.id).filter(
            ChartOfAccounts.parent_id == parent_id,
            ChartOfAccounts.is_active == True
        ).all()
        
        total_balance = Decimal('0')
        for child in children:
            child_balance = self.get_account_balance(child.id, as_of_date)
            total_balance += child_balance
        
        return total_balance.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def get_account_hierarchy(self, company_id: UUID) -> List[Dict[str, Any]]:
        """Get Account Hierarchy."""
        """Get the complete account hierarchy for a company."""
        accounts = self.db.query(ChartOfAccounts).filter(
            ChartOfAccounts.company_id == company_id,
            ChartOfAccounts.is_active == True
        ).order_by(ChartOfAccounts.code).all()
        
        # Build account map and root accounts list
        account_map = {}
            
    def create_account(self, account_data: AccountCreate, created_by: UUID) -> AccountResponse:
        """Create Account."""
        """Create a new account in the chart of accounts."""
        # Validate account data
        self._validate_account_creation(account_data)
        
        # Validate account code uniqueness
        self._validate_account_code(account_data.code, account_data.company_id)
        
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
        
        # Prepare account data with default values
        account_dict = account_data.dict(exclude_unset=True)
        account_dict.update({
            "created_by": created_by,
            "updated_by": created_by,
            "status": account_dict.get("status", AccountStatus.ACTIVE),
            "is_leaf": True,  # Default to leaf, will be updated if children added
            "opening_balance": account_dict.get("opening_balance", Decimal('0.00')),
            "current_balance": Decimal('0.00'),  # Will be calculated
            "balance_as_of": datetime.utcnow().date()
        })
        
        # Create the account
        account = ChartOfAccounts(**account_dict)
        self.db.add(account)
        self.db.flush()  # Flush to get the account ID
        
        # Update parent's is_leaf status if applicable
        if account.parent_id:
            self._update_parent_leaf_status(account.parent_id, is_leaf=False)
        
        # Update account hierarchy path
        self._update_account_hierarchy_path(account)
        
        # Calculate initial balance
        self._update_account_balance(account.id)
        
        self.db.commit()
        self.db.refresh(account)
        
        return AccountResponse.from_orm(account)
    
    def _update_parent_leaf_status(self, account_id: UUID, is_leaf: bool) -> None:
        """ Update Parent Leaf Status."""
        """Update the is_leaf status of a parent account."""
        account = self.db.query(ChartOfAccounts).get(account_id)
        if account and account.is_leaf != is_leaf:
            account.is_leaf = is_leaf
            account.updated_at = datetime.utcnow()
            self.db.add(account)
            self.db.flush()
    
    def _update_account_hierarchy_path(self, account: ChartOfAccounts) -> None:
        """ Update Account Hierarchy Path."""
        """Update the hierarchy path for an account."""
        if account.parent_id:
            parent = self.db.query(ChartOfAccounts).get(account.parent_id)
            account.hierarchy_path = f"{parent.hierarchy_path}.{account.id}"
        else:
            account.hierarchy_path = str(account.id)
        
        account.updated_at = datetime.utcnow()
        self.db.add(account)
        self.db.flush()
        
        # Update all descendants
        self._update_descendants_hierarchy_path(account)
    
    def _update_descendants_hierarchy_path(self, account: ChartOfAccounts) -> None:
        """ Update Descendants Hierarchy Path."""
        """Update hierarchy paths for all descendants of an account."""
        children = self.db.query(ChartOfAccounts).filter(
            ChartOfAccounts.parent_id == account.id,
            ChartOfAccounts.is_active == True
        ).all()
        
        for child in children:
            child.hierarchy_path = f"{account.hierarchy_path}.{child.id}"
            self.db.add(child)
            self._update_descendants_hierarchy_path(child)
    
    def _update_account_balance(self, account_id: UUID) -> None:
        """ Update Account Balance."""
        """Update the current balance of an account."""
        account = self.db.query(ChartOfAccounts).get(account_id)
        if not account:
            return
        
        # Calculate new balance
        new_balance = self.get_account_balance(account_id)
        
        # Update account
        account.current_balance = new_balance
        account.balance_as_of = datetime.utcnow().date()
        self.db.add(account)
        
        # Update parent accounts
        if account.parent_id:
            self._update_account_balance(account.parent_id)
    
    def update_account(
        """Update Account."""
        self, 
        account_id: UUID, 
        account_data: AccountUpdate, 
        updated_by: UUID
    ) -> AccountResponse:
        """Update Account."""
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
        """Delete Account."""
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
        """Get Account Tree."""
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
        """Get Account Balance."""
        self, 
        account_id: UUID, 
        as_of_date: Optional[datetime] = None,
        include_children: bool = False
    ) -> AccountBalanceResponse:
        """Get Account Balance."""
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
        """ Is Descendant."""
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
