from typing import List, Optional
from decimal import Decimal
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, text
from app.crud.base import CRUDBase
from app.modules.core_financials.general_ledger.models import Account, JournalEntry, JournalEntryLine, AccountType
from app.modules.core_financials.general_ledger.schemas import AccountCreate, AccountUpdate, JournalEntryCreate, TrialBalanceItem
from app.core.security.input_validation import AccountCodeValidator, sanitize_sql_input
from app.core.logging.config import get_logger

logger = get_logger("gl_services")

class AccountService(CRUDBase[Account, AccountCreate, AccountUpdate]):
    def __init__(self):
        super().__init__(Account)
    
    async def get_by_code(self, db: AsyncSession, account_code: str) -> Optional[Account]:
        # Validate and sanitize input to prevent SQL injection
        validated_code = AccountCodeValidator.validate(account_code)
        sanitized_code = sanitize_sql_input(validated_code)
        
        # Use parameterized query
        result = await db.execute(
            select(Account).where(Account.account_code == sanitized_code)
        )
        return result.scalar_one_or_none()
    
    async def get_chart_of_accounts(self, db: AsyncSession) -> List[Account]:
        result = await db.execute(
            select(Account)
            .where(Account.is_active == True)
            .order_by(Account.account_code)
        )
        return result.scalars().all()

class JournalEntryService(CRUDBase[JournalEntry, JournalEntryCreate, None]):
    def __init__(self):
        super().__init__(JournalEntry)
    
    async def create_journal_entry(self, db: AsyncSession, entry_data: JournalEntryCreate) -> JournalEntry:
        # Validate debits equal credits
        total_debits = sum(line.debit_amount for line in entry_data.lines)
        total_credits = sum(line.credit_amount for line in entry_data.lines)
        
        if total_debits != total_credits:
            raise ValueError("Total debits must equal total credits")
        
        # Generate entry number
        entry_number = await self._generate_entry_number(db)
        
        # Create journal entry
        journal_entry = JournalEntry(
            entry_number=entry_number,
            entry_date=entry_data.entry_date,
            description=entry_data.description,
            reference=entry_data.reference,
            total_debit=total_debits,
            total_credit=total_credits
        )
        
        db.add(journal_entry)
        await db.flush()
        
        # Create journal entry lines
        for line_data in entry_data.lines:
            line = JournalEntryLine(
                journal_entry_id=journal_entry.id,
                account_id=line_data.account_id,
                description=line_data.description,
                debit_amount=line_data.debit_amount,
                credit_amount=line_data.credit_amount
            )
            db.add(line)
        
        await db.commit()
        await db.refresh(journal_entry)
        return journal_entry
    
    async def get_trial_balance(self, db: AsyncSession, as_of_date: date) -> List[TrialBalanceItem]:
        # Get account balances
        query = select(
            Account.account_code,
            Account.account_name,
            func.coalesce(func.sum(JournalEntryLine.debit_amount), 0).label('total_debits'),
            func.coalesce(func.sum(JournalEntryLine.credit_amount), 0).label('total_credits')
        ).select_from(
            Account.__table__.outerjoin(
                JournalEntryLine.__table__.join(JournalEntry.__table__)
            )
        ).where(
            and_(
                Account.is_active == True,
                JournalEntry.entry_date <= as_of_date
            )
        ).group_by(
            Account.id, Account.account_code, Account.account_name
        ).order_by(Account.account_code)
        
        result = await db.execute(query)
        rows = result.fetchall()
        
        trial_balance_items = []
        for row in rows:
            net_balance = row.total_debits - row.total_credits
            debit_balance = net_balance if net_balance > 0 else Decimal('0')
            credit_balance = abs(net_balance) if net_balance < 0 else Decimal('0')
            
            trial_balance_items.append(TrialBalanceItem(
                account_code=row.account_code,
                account_name=row.account_name,
                debit_balance=debit_balance,
                credit_balance=credit_balance
            ))
        
        return trial_balance_items
    
    async def post_entry(self, db: AsyncSession, entry_id: int) -> JournalEntry:
        logger.info(f"Attempting to post journal entry: {entry_id}")
        
        entry = await self.get(db, entry_id)
        if not entry:
            logger.error(f"Journal entry not found for posting: {entry_id}")
            raise ValueError("Journal entry not found")
        if entry.status != 'draft':
            logger.warning(f"Cannot post entry {entry_id} - status is {entry.status}, expected 'draft'")
            raise ValueError("Only draft entries can be posted")
        
        try:
            entry.status = 'posted'
            entry.posted_at = func.now()
            await db.commit()
            await db.refresh(entry)
            logger.info(f"Journal entry posted successfully: {entry_id}")
            return entry
        except Exception as e:
            logger.error(f"Failed to post journal entry {entry_id}: {str(e)}")
            await db.rollback()
            raise
    
    async def unpost_entry(self, db: AsyncSession, entry_id: int) -> JournalEntry:
        entry = await self.get(db, entry_id)
        if not entry:
            raise ValueError("Journal entry not found")
        if entry.status != 'posted':
            raise ValueError("Only posted entries can be unposted")
        
        entry.status = 'draft'
        entry.posted_at = None
        await db.commit()
        await db.refresh(entry)
        return entry
    
    async def reverse_entry(self, db: AsyncSession, entry_id: int, reversal_date: date, reason: str) -> JournalEntry:
        logger.info(f"Attempting to reverse journal entry: {entry_id}, reason: {reason}")
        
        original_entry = await self.get(db, entry_id)
        if not original_entry:
            logger.error(f"Journal entry not found for reversal: {entry_id}")
            raise ValueError("Journal entry not found")
        if original_entry.status != 'posted':
            logger.warning(f"Cannot reverse entry {entry_id} - status is {original_entry.status}, expected 'posted'")
            raise ValueError("Only posted entries can be reversed")
        
        # Create reversal entry
        reversal_number = await self._generate_entry_number(db)
        reversal_entry = JournalEntry(
            entry_number=reversal_number,
            entry_date=reversal_date,
            description=f"Reversal of {original_entry.entry_number}: {reason}",
            reference=original_entry.reference,
            total_debit=original_entry.total_credit,
            total_credit=original_entry.total_debit,
            status='posted'
        )
        
        db.add(reversal_entry)
        await db.flush()
        
        # Create reversed line items
        result = await db.execute(
            select(JournalEntryLine).where(JournalEntryLine.journal_entry_id == entry_id)
        )
        original_lines = result.scalars().all()
        
        for line in original_lines:
            reversed_line = JournalEntryLine(
                journal_entry_id=reversal_entry.id,
                account_id=line.account_id,
                description=f"Reversal: {line.description}",
                debit_amount=line.credit_amount,
                credit_amount=line.debit_amount
            )
            db.add(reversed_line)
        
        # Update original entry
        original_entry.status = 'reversed'
        original_entry.reversed_at = func.now()
        
        try:
            await db.commit()
            await db.refresh(reversal_entry)
            logger.info(f"Journal entry reversed successfully: {entry_id} -> {reversal_entry.id}")
            return reversal_entry
        except Exception as e:
            logger.error(f"Failed to reverse journal entry {entry_id}: {str(e)}")
            await db.rollback()
            raise
    
    async def validate_period_close(self, db: AsyncSession, period_end_date: date) -> dict:
        """Validate period can be closed"""
        logger.info(f"Validating period close for: {period_end_date}")
        
        # Check for unposted entries
        unposted = await db.execute(
            select(func.count(JournalEntry.id))
            .where(and_(
                JournalEntry.entry_date <= period_end_date,
                JournalEntry.status == 'draft'
            ))
        )
        unposted_count = unposted.scalar() or 0
        
        # Check trial balance
        accounts = await db.execute(select(Account))
        total_debits = sum(acc.balance for acc in accounts.scalars().all() if acc.balance > 0)
        total_credits = sum(abs(acc.balance) for acc in accounts.scalars().all() if acc.balance < 0)
        
        is_balanced = abs(total_debits - total_credits) < 0.01
        
        return {
            "can_close": unposted_count == 0 and is_balanced,
            "unposted_entries": unposted_count,
            "trial_balance_balanced": is_balanced,
            "total_debits": total_debits,
            "total_credits": total_credits
        }
    
    async def _generate_entry_number(self, db: AsyncSession) -> str:
        result = await db.execute(
            select(func.count(JournalEntry.id))
        )
        count = result.scalar() or 0
        return f"JE-{count + 1:06d}"