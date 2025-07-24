from typing import List, Optional
from decimal import Decimal
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.crud.base import CRUDBase
from app.modules.core_financials.general_ledger.models import Account, JournalEntry, JournalEntryLine, AccountType
from app.modules.core_financials.general_ledger.schemas import AccountCreate, AccountUpdate, JournalEntryCreate, TrialBalanceItem

class AccountService(CRUDBase[Account, AccountCreate, AccountUpdate]):
    def __init__(self):
        super().__init__(Account)
    
    async def get_by_code(self, db: AsyncSession, account_code: str) -> Optional[Account]:
        result = await db.execute(select(Account).where(Account.account_code == account_code))
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
    
    async def _generate_entry_number(self, db: AsyncSession) -> str:
        result = await db.execute(
            select(func.count(JournalEntry.id))
        )
        count = result.scalar() or 0
        return f"JE-{count + 1:06d}"