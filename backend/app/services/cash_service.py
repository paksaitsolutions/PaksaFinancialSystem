from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.cash_account import CashAccount, CashTransaction
from typing import List

class CashService:
    def __init__(self, db: AsyncSession, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
    
    async def get_cash_accounts(self) -> List[CashAccount]:
        result = await self.db.execute(
            select(CashAccount).where(CashAccount.tenant_id == self.tenant_id, CashAccount.is_active == True)
        )
        return result.scalars().all()
    
    async def create_cash_account(self, account_data: dict) -> CashAccount:
        account = CashAccount(
            tenant_id=self.tenant_id,
            account_name=account_data['account_name'],
            account_number=account_data.get('account_number'),
            bank_name=account_data.get('bank_name'),
            account_type=account_data.get('account_type', 'checking'),
            current_balance=account_data.get('current_balance', 0)
        )
        self.db.add(account)
        await self.db.commit()
        await self.db.refresh(account)
        return account
    
    async def create_transaction(self, transaction_data: dict) -> CashTransaction:
        transaction = CashTransaction(
            tenant_id=self.tenant_id,
            cash_account_id=transaction_data['cash_account_id'],
            transaction_date=transaction_data['transaction_date'],
            description=transaction_data['description'],
            amount=transaction_data['amount'],
            transaction_type=transaction_data['transaction_type'],
            reference=transaction_data.get('reference')
        )
        self.db.add(transaction)
        await self.db.commit()
        await self.db.refresh(transaction)
        return transaction