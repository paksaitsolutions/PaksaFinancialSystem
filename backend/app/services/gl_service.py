from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.gl_account import GLAccount
from app.models.journal_entry import JournalEntry, JournalEntryLine
from typing import List, Optional
from uuid import uuid4

class GLService:
    def __init__(self, db: AsyncSession, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
    
    async def get_accounts(self) -> List[GLAccount]:
        result = await self.db.execute(
            select(GLAccount).where(GLAccount.tenant_id == self.tenant_id, GLAccount.is_active == True)
        )
        return result.scalars().all()
    
    async def create_account(self, account_data: dict) -> GLAccount:
        account = GLAccount(
            tenant_id=self.tenant_id,
            account_code=account_data['account_code'],
            account_name=account_data['account_name'],
            account_type=account_data['account_type'],
            balance=account_data.get('balance', 0)
        )
        self.db.add(account)
        await self.db.commit()
        await self.db.refresh(account)
        return account
    
    async def create_journal_entry(self, entry_data: dict) -> JournalEntry:
        entry = JournalEntry(
            tenant_id=self.tenant_id,
            entry_number=f"JE-{uuid4().hex[:8].upper()}",
            entry_date=entry_data['entry_date'],
            description=entry_data.get('description', ''),
            total_debit=sum(line.get('debit_amount', 0) for line in entry_data.get('lines', [])),
            total_credit=sum(line.get('credit_amount', 0) for line in entry_data.get('lines', [])),
            status='posted'
        )
        
        for line_data in entry_data.get('lines', []):
            line = JournalEntryLine(
                tenant_id=self.tenant_id,
                account_id=line_data['account_id'],
                description=line_data.get('description', ''),
                debit_amount=line_data.get('debit_amount', 0),
                credit_amount=line_data.get('credit_amount', 0)
            )
            entry.lines.append(line)
        
        self.db.add(entry)
        await self.db.commit()
        await self.db.refresh(entry)
        return entry
    
    async def get_trial_balance(self) -> List[dict]:
        result = await self.db.execute(
            select(GLAccount.account_code, GLAccount.account_name, GLAccount.balance)
            .where(GLAccount.tenant_id == self.tenant_id, GLAccount.is_active == True)
        )
        return [{"code": row[0], "name": row[1], "balance": float(row[2])} for row in result]