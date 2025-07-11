"""
General Ledger service layer for business logic.
"""
from datetime import date
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.services.base import BaseService
from app.modules.core_financials.general_ledger.models import Account, JournalEntry, JournalEntryLine
from app.modules.core_financials.general_ledger.schemas import (
    AccountCreate, AccountUpdate, JournalEntryCreate, TrialBalanceItem
)

class AccountService(BaseService[Account, AccountCreate, AccountUpdate]):
    def __init__(self):
        super().__init__(Account)

    async def get_by_code(self, db: AsyncSession, account_code: str) -> Optional[Account]:
        result = await db.execute(
            select(Account).where(Account.account_code == account_code)
        )
        return result.scalar_one_or_none()

    async def get_chart_of_accounts(self, db: AsyncSession) -> List[Account]:
        result = await db.execute(
            select(Account)
            .where(Account.is_active == True)
            .order_by(Account.account_code)
        )
        return result.scalars().all()

class JournalEntryService(BaseService[JournalEntry, JournalEntryCreate, None]):
    def __init__(self):
        super().__init__(JournalEntry)

    async def create_journal_entry(
        self, db: AsyncSession, *, entry_data: JournalEntryCreate
    ) -> JournalEntry:
        # Validate that debits equal credits
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

    async def _generate_entry_number(self, db: AsyncSession) -> str:
        result = await db.execute(
            select(func.count(JournalEntry.id))
        )
        count = result.scalar() or 0
        return f"JE{count + 1:06d}"

    async def get_trial_balance(
        self, db: AsyncSession, as_of_date: date
    ) -> List[TrialBalanceItem]:
        # This is a simplified trial balance calculation
        # In production, you'd want more sophisticated logic
        query = """
        SELECT 
            a.account_code,
            a.account_name,
            COALESCE(SUM(jel.debit_amount), 0) as total_debits,
            COALESCE(SUM(jel.credit_amount), 0) as total_credits
        FROM accounts a
        LEFT JOIN journal_entry_lines jel ON a.id = jel.account_id
        LEFT JOIN journal_entries je ON jel.journal_entry_id = je.id
        WHERE a.is_active = true 
        AND (je.entry_date IS NULL OR je.entry_date <= :as_of_date)
        GROUP BY a.id, a.account_code, a.account_name
        ORDER BY a.account_code
        """
        
        result = await db.execute(query, {"as_of_date": as_of_date})
        rows = result.fetchall()
        
        trial_balance = []
        for row in rows:
            debit_balance = row.total_debits - row.total_credits
            credit_balance = row.total_credits - row.total_debits
            
            trial_balance.append(TrialBalanceItem(
                account_code=row.account_code,
                account_name=row.account_name,
                debit_balance=max(debit_balance, 0),
                credit_balance=max(credit_balance, 0)
            ))
        
        return trial_balance