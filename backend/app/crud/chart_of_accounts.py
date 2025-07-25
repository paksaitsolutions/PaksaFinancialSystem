"""
CRUD operations for Chart of Accounts
"""
from typing import List, Optional, Dict, Any, Tuple, Union
from uuid import UUID, uuid4
from decimal import Decimal
from datetime import datetime

from sqlalchemy import select, func, and_, or_, update, delete, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from models.chart_of_accounts import ChartOfAccounts as ChartOfAccountsModel
from schemas.chart_of_accounts import (
    ChartOfAccountsCreate,
    ChartOfAccountsUpdate,
    ChartOfAccountsTree,
    ChartOfAccountsWithBalance
)
from app.core.exceptions import (
    NotFoundException,
    BadRequestException,
    ValidationException
)

class CRUDChartOfAccounts:
    """CRUD operations for Chart of Accounts."""
    
    async def get_by_id(
        self, 
        db: AsyncSession, 
        id: UUID,
        include_inactive: bool = False
    ) -> Optional[ChartOfAccountsModel]:
        """Get a Chart of Accounts entry by ID."""
        query = (
            select(ChartOfAccountsModel)
            .options(
                selectinload(ChartOfAccountsModel.parent),
                selectinload(ChartOfAccountsModel.children)
            )
            .where(ChartOfAccountsModel.id == id)
        )
        
        if not include_inactive:
            query = query.where(ChartOfAccountsModel.is_active.is_(True))
            
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_by_code(
        self, 
        db: AsyncSession, 
        code: str,
        include_inactive: bool = False
    ) -> Optional[ChartOfAccountsModel]:
        """Get a Chart of Accounts entry by code."""
        query = (
            select(ChartOfAccountsModel)
            .options(
                selectinload(ChartOfAccountsModel.parent),
                selectinload(ChartOfAccountsModel.children)
            )
            .where(ChartOfAccountsModel.code == code)
        )
        
        if not include_inactive:
            query = query.where(ChartOfAccountsModel.is_active.is_(True))
            
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_multi(
        self, 
        db: AsyncSession, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        include_inactive: bool = False,
        category: Optional[str] = None,
        account_type: Optional[str] = None,
        parent_id: Optional[UUID] = None
    ) -> Tuple[List[ChartOfAccountsModel], int]:
        """Get multiple Chart of Accounts entries with filtering and pagination."""
        # Base query
        query = select(ChartOfAccountsModel)
        
        # Apply filters
        filters = []
        
        if not include_inactive:
            filters.append(ChartOfAccountsModel.is_active.is_(True))
            
        if category:
            filters.append(ChartOfAccountsModel.category == category)
            
        if account_type:
            filters.append(ChartOfAccountsModel.account_type == account_type)
            
        if parent_id is not None:
            if parent_id:
                filters.append(ChartOfAccountsModel.parent_id == parent_id)
            else:
                filters.append(ChartOfAccountsModel.parent_id.is_(None))
        
        if filters:
            query = query.where(and_(*filters))
        
        # Get total count for pagination
        count_query = select(func.count()).select_from(ChartOfAccountsModel)
        if filters:
            count_query = count_query.where(and_(*filters))
            
        total = (await db.execute(count_query)).scalar()
        
        # Apply pagination and ordering
        query = (
            query.order_by(ChartOfAccountsModel.code)
            .offset(skip)
            .limit(limit)
            .options(
                selectinload(ChartOfAccountsModel.parent),
                selectinload(ChartOfAccountsModel.children)
            )
        )
        
        result = await db.execute(query)
        accounts = result.scalars().all()
        
        return accounts, total
    
    async def get_tree(
        self, 
        db: AsyncSession, 
        parent_id: Optional[UUID] = None,
        include_inactive: bool = False
    ) -> List[ChartOfAccountsTree]:
        """Get Chart of Accounts as a hierarchical tree."""
        # Get all accounts that are either root or children of the specified parent
        query = select(ChartOfAccountsModel)
        
        if parent_id:
            query = query.where(ChartOfAccountsModel.parent_id == parent_id)
        else:
            query = query.where(ChartOfAccountsModel.parent_id.is_(None))
            
        if not include_inactive:
            query = query.where(ChartOfAccountsModel.is_active.is_(True))
            
        query = query.order_by(ChartOfAccountsModel.code)
        result = await db.execute(query)
        accounts = result.scalars().all()
        
        # Convert to tree structure
        tree = []
        for account in accounts:
            # Get balance information
            balance_info = await self.calculate_account_balance(db, account.id)
            
            # Recursively get children
            children = await self.get_tree(
                db, 
                parent_id=account.id, 
                include_inactive=include_inactive
            )
            
            # Create account node
            account_data = account.to_dict()
            account_data.update({
                'balance': float(balance_info['balance']),
                'balance_debit': float(balance_info['debit']),
                'balance_credit': float(balance_info['credit']),
                'children': children
            })
            
            tree.append(ChartOfAccountsTree(**account_data))
            
        return tree
    
    async def create(
        self, 
        db: AsyncSession, 
        *, 
        obj_in: ChartOfAccountsCreate,
        created_by_id: Optional[UUID] = None
    ) -> ChartOfAccountsModel:
        """Create a new Chart of Accounts entry."""
        # Check if code already exists
        existing = await self.get_by_code(db, obj_in.code, include_inactive=True)
        if existing:
            raise ValidationException(f"Account with code {obj_in.code} already exists")
            
        # Get parent if specified
        parent = None
        if obj_in.parent_code:
            parent = await self.get_by_code(db, obj_in.parent_code, include_inactive=True)
            if not parent:
                raise NotFoundException(f"Parent account with code {obj_in.parent_code} not found")
        
        # Create the account
        db_obj = ChartOfAccountsModel(
            **obj_in.dict(exclude={"parent_code"}),
            parent_id=parent.id if parent else None,
            created_by_id=created_by_id,
            updated_by_id=created_by_id
        )
        
        db.add(db_obj)
        await db.flush()  # Get the ID for updating full_code
        
        # Update full_code based on parent
        await self._update_full_code(db, db_obj)
        
        await db.commit()
        await db.refresh(db_obj)
        
        return db_obj
    
    async def update(
        self, 
        db: AsyncSession, 
        *, 
        db_obj: ChartOfAccountsModel,
        obj_in: ChartOfAccountsUpdate,
        updated_by_id: Optional[UUID] = None
    ) -> ChartOfAccountsModel:
        """Update a Chart of Accounts entry."""
        update_data = obj_in.dict(exclude_unset=True, exclude={"parent_code"})
        
        # Check if code is being changed and if it already exists
        if "code" in update_data and update_data["code"] != db_obj.code:
            existing = await self.get_by_code(db, update_data["code"], include_inactive=True)
            if existing and existing.id != db_obj.id:
                raise ValidationException(f"Account with code {update_data['code']} already exists")
        
        # Handle parent change if needed
        if "parent_code" in obj_in.dict(exclude_unset=True):
            parent_code = obj_in.parent_code
            if parent_code:
                # Find the new parent
                parent = await self.get_by_code(db, parent_code, include_inactive=True)
                if not parent:
                    raise NotFoundException(f"Parent account with code {parent_code} not found")
                
                # Prevent circular references
                if parent.id == db_obj.id:
                    raise ValidationException("An account cannot be its own parent")
                    
                # Check if the new parent is a descendant of this account
                current_parent = parent
                while current_parent:
                    if current_parent.id == db_obj.id:
                        raise ValidationException("Cannot move account to one of its own descendants")
                    current_parent = await self.get(db, current_parent.parent_id)
                
                update_data["parent_id"] = parent.id
            else:
                update_data["parent_id"] = None
        
        # Update fields
        for field, value in update_data.items():
            setattr(db_obj, field, value)
            
        # Update timestamps and user
        db_obj.updated_at = datetime.utcnow()
        if updated_by_id:
            db_obj.updated_by_id = updated_by_id
        
        # If code or parent was changed, update full_code
        if "code" in update_data or "parent_id" in update_data:
            await self._update_full_code(db, db_obj)
            
            # If this account has children, update their full_codes as well
            if db_obj.children:
                await self._update_children_full_codes(db, db_obj)
        
        await db.commit()
        await db.refresh(db_obj)
        
        return db_obj
    
    async def delete(
        self, 
        db: AsyncSession, 
        *, 
        db_obj: ChartOfAccountsModel,
        deleted_by_id: Optional[UUID] = None
    ) -> ChartOfAccountsModel:
        """Delete a Chart of Accounts entry (soft delete)."""
        # Check if account has children
        if db_obj.children:
            raise BadRequestException("Cannot delete an account that has child accounts")
            
        # Check if account is used in journal entries
        from crud.journal_entry import crud_journal_entry
        has_entries = await crud_journal_entry.account_has_entries(db, db_obj.id)
        
        if has_entries:
            raise BadRequestException(
                "Cannot delete an account that has associated journal entries"
            )
        
        # Soft delete by marking as inactive
        db_obj.is_active = False
        db_obj.updated_at = datetime.utcnow()
        db_obj.updated_by_id = deleted_by_id
        
        await db.commit()
        await db.refresh(db_obj)
        
        return db_obj
    
    async def calculate_account_balance(
        self, 
        db: AsyncSession, 
        account_id: UUID,
        as_of_date: Optional[date] = None
    ) -> Dict[str, Decimal]:
        """Calculate the current balance of an account."""
        from models.general_ledger import JournalEntryItem as JournalEntryItemModel
        
        # Build the query
        query = (
            select(
                func.sum(
                    case(
                        [
                            (JournalEntryItemModel.side == 'debit', JournalEntryItemModel.amount),
                            (JournalEntryItemModel.side == 'credit', -JournalEntryItemModel.amount)
                        ],
                        else_=0
                    )
                ).label("balance"),
                func.sum(
                    case(
                        [(JournalEntryItemModel.side == 'debit', JournalEntryItemModel.amount)],
                        else_=0
                    )
                ).label("debit"),
                func.sum(
                    case(
                        [(JournalEntryItemModel.side == 'credit', JournalEntryItemModel.amount)],
                        else_=0
                    )
                ).label("credit")
            )
            .join(JournalEntryItemModel.journal_entry)
            .where(
                and_(
                    JournalEntryItemModel.account_id == account_id,
                    JournalEntryModel.status == 'posted'
                )
            )
        )
        
        # Add date filter if provided
        if as_of_date:
            query = query.where(JournalEntryModel.date_posted <= as_of_date)
        
        result = await db.execute(query)
        row = result.first()
        
        return {
            'balance': row.balance or Decimal('0.00'),
            'debit': row.debit or Decimal('0.00'),
            'credit': row.credit or Decimal('0.00')
        }
    
    async def _update_full_code(
        self, 
        db: AsyncSession, 
        account: ChartOfAccountsModel
    ) -> None:
        """Update the full_code field for an account based on its parent."""
        if account.parent_id:
            parent = await self.get_by_id(db, account.parent_id, include_inactive=True)
            if not parent:
                raise NotFoundException(f"Parent account with ID {account.parent_id} not found")
            account.full_code = f"{parent.full_code}.{account.code}"
        else:
            account.full_code = account.code
        
        await db.flush()
    
    async def _update_children_full_codes(
        self, 
        db: AsyncSession, 
        parent: ChartOfAccountsModel
    ) -> None:
        """Recursively update full_codes for all children of an account."""
        children = await db.execute(
            select(ChartOfAccountsModel)
            .where(ChartOfAccountsModel.parent_id == parent.id)
        )
        
        for child in children.scalars():
            await self._update_full_code(db, child)
            await self._update_children_full_codes(db, child)

# Create a singleton instance
crud_chart_of_accounts = CRUDChartOfAccounts()
