<<<<<<< HEAD:backend/crud/journal_entry.py
"""
CRUD operations for Journal Entries
"""
from datetime import date, datetime
from typing import List, Optional, Dict, Any, Tuple, Union
from uuid import UUID, uuid4
from decimal import Decimal

from sqlalchemy import select, func, and_, or_, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from models.general_ledger import (
    JournalEntry as JournalEntryModel,
    JournalEntryItem as JournalEntryItemModel,
    ChartOfAccounts as ChartOfAccountsModel
)
from schemas.journal_entry import (
    JournalEntryCreate,
    JournalEntryUpdate,
    JournalEntryStatus,
    JournalEntryItemCreate,
    JournalEntryFilter
)
from core.exceptions import (
    NotFoundException, 
    BadRequestException,
    ValidationException
)

class CRUDJournalEntry:
    """CRUD operations for Journal Entries"""
    
    async def get_by_id(
        self, 
        db: AsyncSession, 
        id: UUID,
        include_void: bool = False
    ) -> Optional[JournalEntryModel]:
        """Get a journal entry by ID with its items."""
        query = (
            select(JournalEntryModel)
            .options(
                selectinload(JournalEntryModel.items)
                .joinedload(JournalEntryItemModel.account)
            )
            .where(JournalEntryModel.id == id)
        )
        
        if not include_void:
            query = query.where(JournalEntryModel.status != JournalEntryStatus.VOID)
            
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_by_entry_number(
        self, 
        db: AsyncSession, 
        entry_number: str,
        include_void: bool = False
    ) -> Optional[JournalEntryModel]:
        """Get a journal entry by its entry number."""
        query = (
            select(JournalEntryModel)
            .options(
                selectinload(JournalEntryModel.items)
                .joinedload(JournalEntryItemModel.account)
            )
            .where(JournalEntryModel.entry_number == entry_number)
        )
        
        if not include_void:
            query = query.where(JournalEntryModel.status != JournalEntryStatus.VOID)
            
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_multi(
        self, 
        db: AsyncSession, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[JournalEntryFilter] = None,
        include_void: bool = False
    ) -> Tuple[List[JournalEntryModel], int]:
        """Get multiple journal entries with optional filtering and pagination."""
        # Base query
        query = (
            select(JournalEntryModel)
            .options(
                selectinload(JournalEntryModel.items)
                .joinedload(JournalEntryItemModel.account)
            )
            .order_by(JournalEntryModel.date_posted.desc(), 
                     JournalEntryModel.entry_number.desc())
        )
        
        # Apply filters
        filter_conditions = []
        
        if filters:
            if filters.start_date:
                filter_conditions.append(JournalEntryModel.date_posted >= filters.start_date)
            if filters.end_date:
                filter_conditions.append(JournalEntryModel.date_posted <= filters.end_date)
            if filters.status:
                filter_conditions.append(JournalEntryModel.status == filters.status)
            if filters.reference:
                filter_conditions.append(JournalEntryModel.reference.ilike(f"%{filters.reference}%"))
            if filters.is_adjusting is not None:
                filter_conditions.append(JournalEntryModel.is_adjusting == filters.is_adjusting)
            if filters.is_recurring is not None:
                filter_conditions.append(JournalEntryModel.is_recurring == filters.is_recurring)
            if filters.created_by_id:
                filter_conditions.append(JournalEntryModel.created_by_id == filters.created_by_id)
            
            # Filter by account code (requires joining with items)
            if filters.account_code:
                subq = (
                    select(JournalEntryItemModel.journal_entry_id)
                    .join(JournalEntryItemModel.account)
                    .where(ChartOfAccountsModel.code == filters.account_code)
                    .distinct()
                ).scalar_subquery()
                filter_conditions.append(JournalEntryModel.id.in_(subq))
        
        # Apply void filter
        if not include_void:
            filter_conditions.append(JournalEntryModel.status != JournalEntryStatus.VOID)
        
        # Apply all filters
        if filter_conditions:
            query = query.where(and_(*filter_conditions))
        
        # Get total count for pagination
        count_query = select(func.count()).select_from(JournalEntryModel)
        if filter_conditions:
            count_query = count_query.where(and_(*filter_conditions))
            
        total = (await db.execute(count_query)).scalar()
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        entries = result.scalars().all()
        
        return entries, total
    
    async def _generate_entry_number(self, db: AsyncSession) -> str:
        """Generate a new journal entry number."""
        # Format: JE-YYYYMMDD-XXXXX (e.g., JE-20230703-00001)
        today = datetime.utcnow().strftime("%Y%m%d")
        
        # Get the last entry number for today
        result = await db.execute(
            select(JournalEntryModel.entry_number)
            .where(JournalEntryModel.entry_number.like(f"JE-{today}-%"))
            .order_by(JournalEntryModel.entry_number.desc())
            .limit(1)
        )
        
        last_number = result.scalar_one_or_none()
        
        if last_number:
            # Increment the sequence number
            sequence = int(last_number.split("-")[2]) + 1
        else:
            # First entry of the day
            sequence = 1
            
        return f"JE-{today}-{sequence:05d}"
    
    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: JournalEntryCreate,
        created_by_id: Optional[UUID] = None
    ) -> JournalEntryModel:
        """Create a new journal entry with its items."""
        from crud.chart_of_accounts import crud_chart_of_accounts
        
        # Generate entry number
        entry_number = await self._generate_entry_number(db)
        
        # Create the journal entry
        db_obj = JournalEntryModel(
            entry_number=entry_number,
            date_posted=obj_in.date_posted or datetime.utcnow().date(),
            reference=obj_in.reference,
            memo=obj_in.memo,
            is_adjusting=obj_in.is_adjusting,
            is_recurring=obj_in.is_recurring,
            recurring_frequency=obj_in.recurring_frequency,
            recurring_end_date=obj_in.recurring_end_date,
            status=JournalEntryStatus.DRAFT,
            created_by_id=created_by_id,
            updated_by_id=created_by_id
        )
        
        db.add(db_obj)
        await db.flush()  # Get the ID for the items
        
        # Create journal entry items
        total_debit = Decimal('0.00')
        total_credit = Decimal('0.00')
        
        for item_in in obj_in.items:
            # Verify account exists and is active
            account = await crud_chart_of_accounts.get_by_code(
                db, 
                code=item_in.account_code,
                include_inactive=False
            )
            
            if not account:
                raise NotFoundException(
                    f"Account with code {item_in.account_code} not found or inactive"
                )
            
            # Calculate amounts
            amount = Decimal(str(item_in.amount))
            
            if item_in.side == 'debit':
                total_debit += amount
            else:
                total_credit += amount
            
            # Create journal entry item
            item = JournalEntryItemModel(
                journal_entry_id=db_obj.id,
                account_id=account.id,
                description=item_in.description,
                amount=amount,
                side=item_in.side,
                foreign_currency_code=item_in.foreign_currency_code,
                foreign_amount=(
                    Decimal(str(item_in.foreign_amount)) 
                    if item_in.foreign_amount is not None 
                    else None
                ),
                exchange_rate=(
                    Decimal(str(item_in.exchange_rate)) 
                    if item_in.exchange_rate is not None 
                    else None
                ),
                created_by_id=created_by_id,
                updated_by_id=created_by_id
            )
            db.add(item)
        
        # Verify that debits equal credits
        if abs(total_debit - total_credit) > Decimal('0.01'):
            raise ValidationException("Total debits must equal total credits")
        
        # Set the total amount
        db_obj.amount = total_debit
        
        await db.commit()
        await db.refresh(db_obj)
        
        return db_obj
    
    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: JournalEntryModel,
        obj_in: JournalEntryUpdate,
        updated_by_id: Optional[UUID] = None
    ) -> JournalEntryModel:
        """Update a journal entry."""
        from crud.chart_of_accounts import crud_chart_of_accounts
        
        # Only allow updates to DRAFT entries
        if db_obj.status != JournalEntryStatus.DRAFT:
            raise BadRequestException(
                "Only draft journal entries can be modified"
            )
        
        update_data = obj_in.dict(exclude_unset=True, exclude={"items"})
        
        # Update fields if provided
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        # Update items if provided
        if obj_in.items is not None:
            # Delete existing items
            await db.execute(
                delete(JournalEntryItemModel)
                .where(JournalEntryItemModel.journal_entry_id == db_obj.id)
            )
            
            # Add new items
            total_debit = Decimal('0.00')
            total_credit = Decimal('0.00')
            
            for item_in in obj_in.items:
                # Verify account exists and is active
                account = await crud_chart_of_accounts.get_by_code(
                    db, 
                    code=item_in.account_code,
                    include_inactive=False
                )
                
                if not account:
                    raise NotFoundException(
                        f"Account with code {item_in.account_code} not found or inactive"
                    )
                
                # Calculate amounts
                amount = Decimal(str(item_in.amount))
                
                if item_in.side == 'debit':
                    total_debit += amount
                else:
                    total_credit += amount
                
                # Create journal entry item
                item = JournalEntryItemModel(
                    journal_entry_id=db_obj.id,
                    account_id=account.id,
                    description=item_in.description,
                    amount=amount,
                    side=item_in.side,
                    foreign_currency_code=item_in.foreign_currency_code,
                    foreign_amount=(
                        Decimal(str(item_in.foreign_amount)) 
                        if item_in.foreign_amount is not None 
                        else None
                    ),
                    exchange_rate=(
                        Decimal(str(item_in.exchange_rate)) 
                        if item_in.exchange_rate is not None 
                        else None
                    ),
                    created_by_id=updated_by_id,
                    updated_by_id=updated_by_id
                )
                db.add(item)
            
            # Verify that debits equal credits
            if abs(total_debit - total_credit) > Decimal('0.01'):
                raise ValidationException("Total debits must equal total credits")
            
            # Update the total amount
            db_obj.amount = total_debit
        
        # Update timestamps and user
        db_obj.updated_at = datetime.utcnow()
        db_obj.updated_by_id = updated_by_id
        
        await db.commit()
        await db.refresh(db_obj)
        
        return db_obj
    
    async def delete(
        self,
        db: AsyncSession,
        *,
        db_obj: JournalEntryModel,
        deleted_by_id: Optional[UUID] = None
    ) -> JournalEntryModel:
        """Delete a journal entry (soft delete)."""
        # Only allow deletion of DRAFT entries
        if db_obj.status != JournalEntryStatus.DRAFT:
            raise BadRequestException(
                "Only draft journal entries can be deleted"
            )
        
        # Soft delete by marking as void
        db_obj.status = JournalEntryStatus.VOID
        db_obj.updated_at = datetime.utcnow()
        db_obj.updated_by_id = deleted_by_id
        
        await db.commit()
        await db.refresh(db_obj)
        
        return db_obj
    
    async def post(
        self,
        db: AsyncSession,
        *,
        db_obj: JournalEntryModel,
        posted_by_id: Optional[UUID] = None
    ) -> JournalEntryModel:
        """Post a journal entry (change status to POSTED)."""
        if db_obj.status != JournalEntryStatus.DRAFT:
            raise BadRequestException(
                "Only draft journal entries can be posted"
            )
        
        # Update status and posting info
        db_obj.status = JournalEntryStatus.POSTED
        db_obj.posted_at = datetime.utcnow()
        db_obj.posted_by_id = posted_by_id
        db_obj.updated_at = datetime.utcnow()
        db_obj.updated_by_id = posted_by_id
        
        # Ensure date_posted is set
        if not db_obj.date_posted:
            db_obj.date_posted = datetime.utcnow().date()
        
        await db.commit()
        await db.refresh(db_obj)
        
        return db_obj

# Create a singleton instance
crud_journal_entry = CRUDJournalEntry()
=======
"""
CRUD operations for Journal Entries
"""
from datetime import date, datetime
from typing import List, Optional, Dict, Any, Tuple, Union
from uuid import UUID, uuid4
from decimal import Decimal

from sqlalchemy import select, func, and_, or_, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from models.general_ledger import (
    JournalEntry as JournalEntryModel,
    JournalEntryItem as JournalEntryItemModel,
    ChartOfAccounts as ChartOfAccountsModel
)
from schemas.journal_entry import (
    JournalEntryCreate,
    JournalEntryUpdate,
    JournalEntryStatus,
    JournalEntryItemCreate,
    JournalEntryFilter
)
from app.core.exceptions import (
    NotFoundException, 
    BadRequestException,
    ValidationException
)

class CRUDJournalEntry:
    """CRUD operations for Journal Entries"""
    
    async def get_by_id(
        self, 
        db: AsyncSession, 
        id: UUID,
        include_void: bool = False
    ) -> Optional[JournalEntryModel]:
        """Get a journal entry by ID with its items."""
        query = (
            select(JournalEntryModel)
            .options(
                selectinload(JournalEntryModel.items)
                .joinedload(JournalEntryItemModel.account)
            )
            .where(JournalEntryModel.id == id)
        )
        
        if not include_void:
            query = query.where(JournalEntryModel.status != JournalEntryStatus.VOID)
            
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_by_entry_number(
        self, 
        db: AsyncSession, 
        entry_number: str,
        include_void: bool = False
    ) -> Optional[JournalEntryModel]:
        """Get a journal entry by its entry number."""
        query = (
            select(JournalEntryModel)
            .options(
                selectinload(JournalEntryModel.items)
                .joinedload(JournalEntryItemModel.account)
            )
            .where(JournalEntryModel.entry_number == entry_number)
        )
        
        if not include_void:
            query = query.where(JournalEntryModel.status != JournalEntryStatus.VOID)
            
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_multi(
        self, 
        db: AsyncSession, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[JournalEntryFilter] = None,
        include_void: bool = False
    ) -> Tuple[List[JournalEntryModel], int]:
        """Get multiple journal entries with optional filtering and pagination."""
        # Base query
        query = (
            select(JournalEntryModel)
            .options(
                selectinload(JournalEntryModel.items)
                .joinedload(JournalEntryItemModel.account)
            )
            .order_by(JournalEntryModel.date_posted.desc(), 
                     JournalEntryModel.entry_number.desc())
        )
        
        # Apply filters
        filter_conditions = []
        
        if filters:
            if filters.start_date:
                filter_conditions.append(JournalEntryModel.date_posted >= filters.start_date)
            if filters.end_date:
                filter_conditions.append(JournalEntryModel.date_posted <= filters.end_date)
            if filters.status:
                filter_conditions.append(JournalEntryModel.status == filters.status)
            if filters.reference:
                filter_conditions.append(JournalEntryModel.reference.ilike(f"%{filters.reference}%"))
            if filters.is_adjusting is not None:
                filter_conditions.append(JournalEntryModel.is_adjusting == filters.is_adjusting)
            if filters.is_recurring is not None:
                filter_conditions.append(JournalEntryModel.is_recurring == filters.is_recurring)
            if filters.created_by_id:
                filter_conditions.append(JournalEntryModel.created_by_id == filters.created_by_id)
            
            # Filter by account code (requires joining with items)
            if filters.account_code:
                subq = (
                    select(JournalEntryItemModel.journal_entry_id)
                    .join(JournalEntryItemModel.account)
                    .where(ChartOfAccountsModel.code == filters.account_code)
                    .distinct()
                ).scalar_subquery()
                filter_conditions.append(JournalEntryModel.id.in_(subq))
        
        # Apply void filter
        if not include_void:
            filter_conditions.append(JournalEntryModel.status != JournalEntryStatus.VOID)
        
        # Apply all filters
        if filter_conditions:
            query = query.where(and_(*filter_conditions))
        
        # Get total count for pagination
        count_query = select(func.count()).select_from(JournalEntryModel)
        if filter_conditions:
            count_query = count_query.where(and_(*filter_conditions))
            
        total = (await db.execute(count_query)).scalar()
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        entries = result.scalars().all()
        
        return entries, total
    
    async def _generate_entry_number(self, db: AsyncSession) -> str:
        """Generate a new journal entry number."""
        # Format: JE-YYYYMMDD-XXXXX (e.g., JE-20230703-00001)
        today = datetime.utcnow().strftime("%Y%m%d")
        
        # Get the last entry number for today
        result = await db.execute(
            select(JournalEntryModel.entry_number)
            .where(JournalEntryModel.entry_number.like(f"JE-{today}-%"))
            .order_by(JournalEntryModel.entry_number.desc())
            .limit(1)
        )
        
        last_number = result.scalar_one_or_none()
        
        if last_number:
            # Increment the sequence number
            sequence = int(last_number.split("-")[2]) + 1
        else:
            # First entry of the day
            sequence = 1
            
        return f"JE-{today}-{sequence:05d}"
    
    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: JournalEntryCreate,
        created_by_id: Optional[UUID] = None
    ) -> JournalEntryModel:
        """Create a new journal entry with its items."""
        from crud.chart_of_accounts import crud_chart_of_accounts
        
        # Generate entry number
        entry_number = await self._generate_entry_number(db)
        
        # Create the journal entry
        db_obj = JournalEntryModel(
            entry_number=entry_number,
            date_posted=obj_in.date_posted or datetime.utcnow().date(),
            reference=obj_in.reference,
            memo=obj_in.memo,
            is_adjusting=obj_in.is_adjusting,
            is_recurring=obj_in.is_recurring,
            recurring_frequency=obj_in.recurring_frequency,
            recurring_end_date=obj_in.recurring_end_date,
            status=JournalEntryStatus.DRAFT,
            created_by_id=created_by_id,
            updated_by_id=created_by_id
        )
        
        db.add(db_obj)
        await db.flush()  # Get the ID for the items
        
        # Create journal entry items
        total_debit = Decimal('0.00')
        total_credit = Decimal('0.00')
        
        for item_in in obj_in.items:
            # Verify account exists and is active
            account = await crud_chart_of_accounts.get_by_code(
                db, 
                code=item_in.account_code,
                include_inactive=False
            )
            
            if not account:
                raise NotFoundException(
                    f"Account with code {item_in.account_code} not found or inactive"
                )
            
            # Calculate amounts
            amount = Decimal(str(item_in.amount))
            
            if item_in.side == 'debit':
                total_debit += amount
            else:
                total_credit += amount
            
            # Create journal entry item
            item = JournalEntryItemModel(
                journal_entry_id=db_obj.id,
                account_id=account.id,
                description=item_in.description,
                amount=amount,
                side=item_in.side,
                foreign_currency_code=item_in.foreign_currency_code,
                foreign_amount=(
                    Decimal(str(item_in.foreign_amount)) 
                    if item_in.foreign_amount is not None 
                    else None
                ),
                exchange_rate=(
                    Decimal(str(item_in.exchange_rate)) 
                    if item_in.exchange_rate is not None 
                    else None
                ),
                created_by_id=created_by_id,
                updated_by_id=created_by_id
            )
            db.add(item)
        
        # Verify that debits equal credits
        if abs(total_debit - total_credit) > Decimal('0.01'):
            raise ValidationException("Total debits must equal total credits")
        
        # Set the total amount
        db_obj.amount = total_debit
        
        await db.commit()
        await db.refresh(db_obj)
        
        return db_obj
    
    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: JournalEntryModel,
        obj_in: JournalEntryUpdate,
        updated_by_id: Optional[UUID] = None
    ) -> JournalEntryModel:
        """Update a journal entry."""
        from crud.chart_of_accounts import crud_chart_of_accounts
        
        # Only allow updates to DRAFT entries
        if db_obj.status != JournalEntryStatus.DRAFT:
            raise BadRequestException(
                "Only draft journal entries can be modified"
            )
        
        update_data = obj_in.dict(exclude_unset=True, exclude={"items"})
        
        # Update fields if provided
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        # Update items if provided
        if obj_in.items is not None:
            # Delete existing items
            await db.execute(
                delete(JournalEntryItemModel)
                .where(JournalEntryItemModel.journal_entry_id == db_obj.id)
            )
            
            # Add new items
            total_debit = Decimal('0.00')
            total_credit = Decimal('0.00')
            
            for item_in in obj_in.items:
                # Verify account exists and is active
                account = await crud_chart_of_accounts.get_by_code(
                    db, 
                    code=item_in.account_code,
                    include_inactive=False
                )
                
                if not account:
                    raise NotFoundException(
                        f"Account with code {item_in.account_code} not found or inactive"
                    )
                
                # Calculate amounts
                amount = Decimal(str(item_in.amount))
                
                if item_in.side == 'debit':
                    total_debit += amount
                else:
                    total_credit += amount
                
                # Create journal entry item
                item = JournalEntryItemModel(
                    journal_entry_id=db_obj.id,
                    account_id=account.id,
                    description=item_in.description,
                    amount=amount,
                    side=item_in.side,
                    foreign_currency_code=item_in.foreign_currency_code,
                    foreign_amount=(
                        Decimal(str(item_in.foreign_amount)) 
                        if item_in.foreign_amount is not None 
                        else None
                    ),
                    exchange_rate=(
                        Decimal(str(item_in.exchange_rate)) 
                        if item_in.exchange_rate is not None 
                        else None
                    ),
                    created_by_id=updated_by_id,
                    updated_by_id=updated_by_id
                )
                db.add(item)
            
            # Verify that debits equal credits
            if abs(total_debit - total_credit) > Decimal('0.01'):
                raise ValidationException("Total debits must equal total credits")
            
            # Update the total amount
            db_obj.amount = total_debit
        
        # Update timestamps and user
        db_obj.updated_at = datetime.utcnow()
        db_obj.updated_by_id = updated_by_id
        
        await db.commit()
        await db.refresh(db_obj)
        
        return db_obj
    
    async def delete(
        self,
        db: AsyncSession,
        *,
        db_obj: JournalEntryModel,
        deleted_by_id: Optional[UUID] = None
    ) -> JournalEntryModel:
        """Delete a journal entry (soft delete)."""
        # Only allow deletion of DRAFT entries
        if db_obj.status != JournalEntryStatus.DRAFT:
            raise BadRequestException(
                "Only draft journal entries can be deleted"
            )
        
        # Soft delete by marking as void
        db_obj.status = JournalEntryStatus.VOID
        db_obj.updated_at = datetime.utcnow()
        db_obj.updated_by_id = deleted_by_id
        
        await db.commit()
        await db.refresh(db_obj)
        
        return db_obj
    
    async def post(
        self,
        db: AsyncSession,
        *,
        db_obj: JournalEntryModel,
        posted_by_id: Optional[UUID] = None
    ) -> JournalEntryModel:
        """Post a journal entry (change status to POSTED)."""
        if db_obj.status != JournalEntryStatus.DRAFT:
            raise BadRequestException(
                "Only draft journal entries can be posted"
            )
        
        # Update status and posting info
        db_obj.status = JournalEntryStatus.POSTED
        db_obj.posted_at = datetime.utcnow()
        db_obj.posted_by_id = posted_by_id
        db_obj.updated_at = datetime.utcnow()
        db_obj.updated_by_id = posted_by_id
        
        # Ensure date_posted is set
        if not db_obj.date_posted:
            db_obj.date_posted = datetime.utcnow().date()
        
        await db.commit()
        await db.refresh(db_obj)
        
        return db_obj

# Create a singleton instance
crud_journal_entry = CRUDJournalEntry()
>>>>>>> e96df7278ce4216131b6c65d411c0723f4de7f91:backend/app/crud/journal_entry.py
