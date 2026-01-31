from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import JournalEntry, JournalEntryLine, ChartOfAccounts, BankAccount, BankTransaction, BankReconciliation, ReconciliationItem


class CashService:
    def __init__(self, db: AsyncSession, tenant_id: str):
        """  Init  ."""
        self.db = db
        self.tenant_id = tenant_id
    
    async def get_bank_accounts(self) -> List[BankAccount]:
        """Get Bank Accounts."""
        result = await self.db.execute(
            select(BankAccount).where(BankAccount.is_active == True)
        )
        return result.scalars().all()
    
    async def create_bank_account(self, account_data: dict) -> BankAccount:
        """Create Bank Account."""
        account = BankAccount(
            name=account_data['name'],
            account_number=account_data['account_number'],
            bank_name=account_data['bank_name'],
            account_type=account_data.get('account_type', 'checking'),
            current_balance=account_data.get('current_balance', 0)
        )
        self.db.add(account)
        await self.db.commit()
        await self.db.refresh(account)
        return account
    
    async def create_transaction(self, transaction_data: dict) -> BankTransaction:
        """Create Transaction."""
        transaction = BankTransaction(
            account_id=transaction_data['account_id'],
            transaction_date=transaction_data['transaction_date'],
            transaction_type=transaction_data['transaction_type'],
            amount=transaction_data['amount'],
            memo=transaction_data.get('memo'),
            payee=transaction_data.get('payee'),
            reference_number=transaction_data.get('reference_number')
        )
        self.db.add(transaction)
        await self.db.flush()
        
        # Auto-generate GL journal entry
        await self._create_cash_journal_entry(transaction, transaction_data)
        
        await self.db.commit()
        await self.db.refresh(transaction)
        return transaction
    
    async def _create_cash_journal_entry(self, transaction: BankTransaction, transaction_data: dict):
        """Create Cash Journal Entry."""
        """Create journal entry for cash transaction"""
        journal_entry = JournalEntry(
            company_id=transaction_data.get('company_id'),
            entry_number=f"CASH-{transaction.reference_number or transaction.id}",
            entry_date=transaction.transaction_date,
            description=f"Cash Transaction - {transaction.memo}",
            total_debit=transaction.amount if transaction.transaction_type in ['DEPOSIT', 'TRANSFER_IN'] else transaction.amount,
            total_credit=transaction.amount,
            status='posted',
            source_module='CASH'
        )
        self.db.add(journal_entry)
        await self.db.flush()
        
        if transaction.transaction_type in ['DEPOSIT', 'TRANSFER_IN']:
            # Debit cash account
            cash_line = JournalEntryLine(
                journal_entry_id=journal_entry.id,
                account_id=transaction_data.get('cash_account_id'),
                description=f"Cash Deposit - {transaction.memo}",
                debit_amount=transaction.amount,
                credit_amount=0,
                line_number=1
            )
            # Credit source account
            source_line = JournalEntryLine(
                journal_entry_id=journal_entry.id,
                account_id=transaction_data.get('source_account_id'),
                description=f"Source - {transaction.memo}",
                debit_amount=0,
                credit_amount=transaction.amount,
                line_number=2
            )
        else:
            # Credit cash account
            cash_line = JournalEntryLine(
                journal_entry_id=journal_entry.id,
                account_id=transaction_data.get('cash_account_id'),
                description=f"Cash Payment - {transaction.memo}",
                debit_amount=0,
                credit_amount=transaction.amount,
                line_number=1
            )
            # Debit expense/destination account
            dest_line = JournalEntryLine(
                journal_entry_id=journal_entry.id,
                account_id=transaction_data.get('destination_account_id'),
                description=f"Expense - {transaction.memo}",
                debit_amount=transaction.amount,
                credit_amount=0,
                line_number=2
            )
            source_line = dest_line
        
        self.db.add(cash_line)
        self.db.add(source_line)
    
    async def create_reconciliation(self, reconciliation_data: dict) -> BankReconciliation:
        """Create Reconciliation."""
        """Create a new bank reconciliation"""
        reconciliation = BankReconciliation(
            account_id=reconciliation_data['account_id'],
            reconciliation_date=reconciliation_data['reconciliation_date'],
            statement_ending_balance=reconciliation_data['statement_ending_balance'],
            book_ending_balance=reconciliation_data['book_ending_balance'],
            difference=reconciliation_data['statement_ending_balance'] - reconciliation_data['book_ending_balance']
        )
        self.db.add(reconciliation)
        await self.db.flush()
        
        # Add reconciliation items
        for item_data in reconciliation_data.get('items', []):
            item = ReconciliationItem(
                reconciliation_id=reconciliation.id,
                transaction_id=item_data.get('transaction_id'),
                item_type=item_data['item_type'],
                description=item_data['description'],
                amount=item_data['amount'],
                is_cleared=item_data.get('is_cleared', False)
            )
            self.db.add(item)
        
        await self.db.commit()
        await self.db.refresh(reconciliation)
        return reconciliation
    
    async def complete_reconciliation(self, reconciliation_id: str, reconciliation_data: dict):
        """Complete Reconciliation."""
        """Complete reconciliation and update GL balances"""
        reconciliation = await self.db.get(BankReconciliation, reconciliation_id)
        if not reconciliation:
            raise ValueError("Reconciliation not found")
        
        # Mark transactions as reconciled
        for item_data in reconciliation_data.get('cleared_items', []):
            if item_data.get('transaction_id'):
                transaction = await self.db.get(BankTransaction, item_data['transaction_id'])
                if transaction:
                    transaction.is_reconciled = True
        
        # Create adjusting journal entries for differences
        if reconciliation.difference != 0:
            await self._create_reconciliation_adjustment(reconciliation, reconciliation_data)
        
        reconciliation.status = "completed"
        reconciliation.completed_at = func.now()
        
        await self.db.commit()
    
    async def _create_reconciliation_adjustment(self, reconciliation: BankReconciliation, reconciliation_data: dict):
        """Create Reconciliation Adjustment."""
        """Create GL adjustment for reconciliation differences"""
        journal_entry = JournalEntry(
            company_id=reconciliation_data.get('company_id'),
            entry_number=f"RECON-{reconciliation.id}",
            entry_date=reconciliation.reconciliation_date,
            description=f"Bank Reconciliation Adjustment - {reconciliation.account.name}",
            total_debit=abs(reconciliation.difference),
            total_credit=abs(reconciliation.difference),
            status='posted',
            source_module='CASH'
        )
        self.db.add(journal_entry)
        await self.db.flush()
        
        if reconciliation.difference > 0:
            # Bank balance higher - debit cash, credit adjustment account
            cash_line = JournalEntryLine(
                journal_entry_id=journal_entry.id,
                account_id=reconciliation_data.get('cash_account_id'),
                description="Bank reconciliation adjustment",
                debit_amount=reconciliation.difference,
                credit_amount=0,
                line_number=1
            )
            adj_line = JournalEntryLine(
                journal_entry_id=journal_entry.id,
                account_id=reconciliation_data.get('adjustment_account_id'),
                description="Bank reconciliation adjustment",
                debit_amount=0,
                credit_amount=reconciliation.difference,
                line_number=2
            )
        else:
            # Book balance higher - credit cash, debit adjustment account
            adj_line = JournalEntryLine(
                journal_entry_id=journal_entry.id,
                account_id=reconciliation_data.get('adjustment_account_id'),
                description="Bank reconciliation adjustment",
                debit_amount=abs(reconciliation.difference),
                credit_amount=0,
                line_number=1
            )
            cash_line = JournalEntryLine(
                journal_entry_id=journal_entry.id,
                account_id=reconciliation_data.get('cash_account_id'),
                description="Bank reconciliation adjustment",
                debit_amount=0,
                credit_amount=abs(reconciliation.difference),
                line_number=2
            )
        
        self.db.add(cash_line)
        self.db.add(adj_line)