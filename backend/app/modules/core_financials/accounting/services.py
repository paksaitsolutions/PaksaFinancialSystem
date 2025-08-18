import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, func

from . import models, schemas
from .exceptions import (
    AccountNotFoundException,
    UnbalancedJournalEntryException,
    InvalidJournalEntryPostException,
    JournalEntryNotFoundException,
    InvalidAccountOperationException
)

class AccountService:
    """Service layer for managing the Chart of Accounts."""

    def __init__(self, db_session: Session):
        self.db = db_session

    async def get_account_by_id(self, account_id: uuid.UUID) -> models.Account:
        account = await self.db.get(models.Account, account_id)
        if not account:
            raise AccountNotFoundException(str(account_id))
        return account

    async def create_account(self, account_create: schemas.AccountCreate) -> models.Account:
        if account_create.parent_id:
            await self.get_account_by_id(account_create.parent_id) # Ensure parent exists
        
        new_account = models.Account(**account_create.dict())
        self.db.add(new_account)
        await self.db.commit()
        await self.db.refresh(new_account)
        return new_account

    async def get_all_accounts(self) -> List[models.Account]:
        result = await self.db.execute(select(models.Account).order_by(models.Account.code))
        return result.scalars().all()

    async def update_account(self, account_id: uuid.UUID, account_update: schemas.AccountUpdate) -> models.Account:
        account = await self.get_account_by_id(account_id)
        
        update_data = account_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(account, key, value)
            
        await self.db.commit()
        await self.db.refresh(account)
        return account

    async def delete_account(self, account_id: uuid.UUID):
        account = await self.get_account_by_id(account_id)
        if account.is_system_account:
            raise InvalidAccountOperationException("Cannot delete a system account.")
        # Add check for associated journal entries before deletion
        # ...
        await self.db.delete(account)
        await self.db.commit()

class JournalEntryService:
    """Service layer for managing Journal Entries."""

    def __init__(self, db_session: Session):
        self.db = db_session

    async def get_journal_entry_by_id(self, entry_id: uuid.UUID) -> models.JournalEntry:
        result = await self.db.execute(
            select(models.JournalEntry)
            .options(joinedload(models.JournalEntry.lines))
            .where(models.JournalEntry.id == entry_id)
        )
        entry = result.scalars().first()
        if not entry:
            raise JournalEntryNotFoundException(str(entry_id))
        return entry

    async def create_journal_entry(self, entry_create: schemas.JournalEntryCreate) -> models.JournalEntry:
        total_debit = sum(line.debit for line in entry_create.lines)
        total_credit = sum(line.credit for line in entry_create.lines)

        if total_debit != total_credit:
            raise UnbalancedJournalEntryException(total_debit, total_credit)

        # Create the main entry
        new_entry = models.JournalEntry(
            **entry_create.dict(exclude={'lines'}),
            entry_number=self._generate_entry_number(),
            total_debit=total_debit,
            total_credit=total_credit
        )
        self.db.add(new_entry)
        await self.db.flush() # Flush to get the new_entry.id

        # Create line items
        for i, line_data in enumerate(entry_create.lines):
            line = models.JournalEntryLine(
                **line_data.dict(),
                journal_entry_id=new_entry.id,
                line_number=i + 1
            )
            self.db.add(line)

        await self.db.commit()
        await self.db.refresh(new_entry)
        return new_entry

    async def post_journal_entry(self, entry_id: uuid.UUID) -> models.JournalEntry:
        entry = await self.get_journal_entry_by_id(entry_id)
        if entry.status != models.JournalEntryStatus.DRAFT:
            raise InvalidJournalEntryPostException(f"Entry is not in DRAFT status (current: {entry.status}).")
        
        # Here you would typically update account balances.
        # This logic can be complex and will be added later.
        # For now, we just update the status.
        
        entry.status = models.JournalEntryStatus.POSTED
        entry.posted_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(entry)
        return entry

    def _generate_entry_number(self) -> str:
        # This is a placeholder. In a real system, this would be a more robust sequence.
        return f"JE-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:4].upper()}"
