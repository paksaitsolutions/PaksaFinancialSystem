"""Enhanced General Ledger services with comprehensive functionality"""
from typing import List, Optional
from decimal import Decimal
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, text
from app.modules.core_financials.general_ledger.models import Account, JournalEntry, JournalEntryLine, AccountType
from app.modules.core_financials.general_ledger.schemas import AccountCreate, AccountUpdate, JournalEntryCreate, TrialBalanceItem
from app.modules.core_financials.general_ledger.services import AccountService as BaseAccountService, JournalEntryService as BaseJournalService

class EnhancedAccountService(BaseAccountService):
    """Enhanced account service with additional functionality"""
    
    async def get_accounts_filtered(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100,
        account_type: Optional[str] = None,
        active_only: bool = True,
        search: Optional[str] = None
    ) -> List[Account]:
        """Get accounts with filtering options"""
        query = select(Account)
        
        if active_only:
            query = query.where(Account.is_active == True)
        
        if account_type:
            query = query.where(Account.account_type == account_type)
        
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    Account.account_code.ilike(search_term),
                    Account.account_name.ilike(search_term)
                )
            )
        
        query = query.order_by(Account.account_code).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def soft_delete(self, db: AsyncSession, account_id: int) -> None:
        """Soft delete an account"""
        account = await self.get(db, account_id)
        if account:
            account.is_active = False
            await db.commit()
    
    async def get_account_hierarchy(self, db: AsyncSession) -> List[Account]:
        """Get accounts in hierarchical order"""
        query = select(Account).where(Account.is_active == True).order_by(Account.account_code)
        result = await db.execute(query)
        return result.scalars().all()

class EnhancedJournalEntryService(BaseJournalService):
    """Enhanced journal entry service with additional functionality"""
    
    async def get_journal_entries_filtered(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        status_filter: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> List[JournalEntry]:
        """Get journal entries with filtering"""
        query = select(JournalEntry)
        
        if status_filter:
            query = query.where(JournalEntry.status == status_filter)
        
        if date_from:
            query = query.where(JournalEntry.entry_date >= date_from)
        
        if date_to:
            query = query.where(JournalEntry.entry_date <= date_to)
        
        query = query.order_by(desc(JournalEntry.entry_date)).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_with_lines(self, db: AsyncSession, entry_id: int) -> Optional[JournalEntry]:
        """Get journal entry with line items"""
        query = select(JournalEntry).where(JournalEntry.id == entry_id)
        result = await db.execute(query)
        entry = result.scalar_one_or_none()
        
        if entry:
            # Load line items
            lines_query = select(JournalEntryLine).where(JournalEntryLine.journal_entry_id == entry_id)
            lines_result = await db.execute(lines_query)
            entry.lines = lines_result.scalars().all()
        
        return entry
    
    async def post_entry(self, db: AsyncSession, entry_id: int) -> JournalEntry:
        """Post a journal entry"""
        entry = await self.get(db, entry_id)
        if not entry:
            raise ValueError("Journal entry not found")
        
        if entry.status != 'draft':
            raise ValueError("Only draft entries can be posted")
        
        # Validate entry is balanced
        if entry.total_debit != entry.total_credit:
            raise ValueError("Entry is not balanced")
        
        entry.status = 'posted'
        entry.posted_at = datetime.utcnow()
        
        # Update account balances
        await self._update_account_balances(db, entry_id, post=True)
        
        await db.commit()
        return entry
    
    async def unpost_entry(self, db: AsyncSession, entry_id: int) -> JournalEntry:
        """Unpost a journal entry"""
        entry = await self.get(db, entry_id)
        if not entry:
            raise ValueError("Journal entry not found")
        
        if entry.status != 'posted':
            raise ValueError("Only posted entries can be unposted")
        
        entry.status = 'draft'
        entry.posted_at = None
        
        # Reverse account balance updates
        await self._update_account_balances(db, entry_id, post=False)
        
        await db.commit()
        return entry
    
    async def reverse_entry(self, db: AsyncSession, entry_id: int, reversal_date: date, reason: str) -> JournalEntry:
        """Create a reversal entry"""
        original_entry = await self.get_with_lines(db, entry_id)
        if not original_entry:
            raise ValueError("Original entry not found")
        
        if original_entry.status != 'posted':
            raise ValueError("Only posted entries can be reversed")
        
        # Generate reversal entry number
        reversal_number = await self._generate_entry_number(db)
        
        # Create reversal entry
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
        for line in original_entry.lines:
            reversal_line = JournalEntryLine(
                journal_entry_id=reversal_entry.id,
                account_id=line.account_id,
                description=f"Reversal: {line.description}",
                debit_amount=line.credit_amount,
                credit_amount=line.debit_amount
            )
            db.add(reversal_line)
        
        # Mark original as reversed
        original_entry.status = 'reversed'
        original_entry.reversed_at = datetime.utcnow()
        
        await db.commit()
        return reversal_entry
    
    async def get_account_balance(self, db: AsyncSession, account_id: int, as_of_date: date) -> Decimal:
        """Get account balance as of specific date"""
        query = select(
            func.coalesce(func.sum(JournalEntryLine.debit_amount), 0) - 
            func.coalesce(func.sum(JournalEntryLine.credit_amount), 0)
        ).select_from(
            JournalEntryLine.__table__.join(JournalEntry.__table__)
        ).where(
            and_(
                JournalEntryLine.account_id == account_id,
                JournalEntry.entry_date <= as_of_date,
                JournalEntry.status == 'posted'
            )
        )
        
        result = await db.execute(query)
        return result.scalar() or Decimal('0')
    
    async def get_gl_summary(self, db: AsyncSession, date_from: date, date_to: date) -> dict:
        """Get GL summary report"""
        query = select(
            Account.account_type,
            func.count(JournalEntryLine.id).label('transaction_count'),
            func.sum(JournalEntryLine.debit_amount).label('total_debits'),
            func.sum(JournalEntryLine.credit_amount).label('total_credits')
        ).select_from(
            JournalEntryLine.__table__.join(JournalEntry.__table__).join(Account.__table__)
        ).where(
            and_(
                JournalEntry.entry_date >= date_from,
                JournalEntry.entry_date <= date_to,
                JournalEntry.status == 'posted'
            )
        ).group_by(Account.account_type)
        
        result = await db.execute(query)
        rows = result.fetchall()
        
        summary = {}
        for row in rows:
            summary[row.account_type.value] = {
                'transaction_count': row.transaction_count,
                'total_debits': float(row.total_debits or 0),
                'total_credits': float(row.total_credits or 0)
            }
        
        return summary
    
    async def get_gl_detail(self, db: AsyncSession, account_id: Optional[int], date_from: date, date_to: date) -> List[dict]:
        """Get GL detail report"""
        query = select(
            JournalEntry.entry_number,
            JournalEntry.entry_date,
            JournalEntry.description,
            Account.account_code,
            Account.account_name,
            JournalEntryLine.description.label('line_description'),
            JournalEntryLine.debit_amount,
            JournalEntryLine.credit_amount
        ).select_from(
            JournalEntryLine.__table__.join(JournalEntry.__table__).join(Account.__table__)
        ).where(
            and_(
                JournalEntry.entry_date >= date_from,
                JournalEntry.entry_date <= date_to,
                JournalEntry.status == 'posted'
            )
        )
        
        if account_id:
            query = query.where(JournalEntryLine.account_id == account_id)
        
        query = query.order_by(JournalEntry.entry_date, JournalEntry.entry_number)
        
        result = await db.execute(query)
        rows = result.fetchall()
        
        return [
            {
                'entry_number': row.entry_number,
                'entry_date': row.entry_date.isoformat(),
                'description': row.description,
                'account_code': row.account_code,
                'account_name': row.account_name,
                'line_description': row.line_description,
                'debit_amount': float(row.debit_amount or 0),
                'credit_amount': float(row.credit_amount or 0)
            }
            for row in rows
        ]
    
    async def _update_account_balances(self, db: AsyncSession, entry_id: int, post: bool = True) -> None:
        """Update account balances when posting/unposting"""
        lines_query = select(JournalEntryLine).where(JournalEntryLine.journal_entry_id == entry_id)
        lines_result = await db.execute(lines_query)
        lines = lines_result.scalars().all()
        
        for line in lines:
            account_query = select(Account).where(Account.id == line.account_id)
            account_result = await db.execute(account_query)
            account = account_result.scalar_one()
            
            if post:
                # Add to balance when posting
                balance_change = line.debit_amount - line.credit_amount
            else:
                # Subtract from balance when unposting
                balance_change = -(line.debit_amount - line.credit_amount)
            
            account.balance = (account.balance or Decimal('0')) + balance_change