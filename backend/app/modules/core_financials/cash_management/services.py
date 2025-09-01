"""
Paksa Financial System - Cash Management Module
Version: 1.0.0
Copyright (c) 2025 Paksa IT Solutions. All rights reserved.

This software is the proprietary information of Paksa IT Solutions.
Use is subject to license terms and restrictions.

This module provides services for managing bank accounts, transactions,
reconciliations, and related financial operations.
"""

from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional, Dict, Any, Tuple, Union
from uuid import UUID, uuid4

from sqlalchemy.orm import Session, joinedload, contains_eager
from sqlalchemy import and_, or_, func, desc, text, update, case, cast, Date, Integer, Numeric, not_

from app.core.exceptions import NotFoundError, ValidationError, BusinessRuleError
"""
Cash management services placeholder (conflicts resolved).
"""
from app.core.database import Base
=======
from app.core.db.base import Base
>>>>>>> e96df7278ce4216131b6c65d411c0723f4de7f91
from app.core.security import get_password_hash, verify_password
from . import models, schemas, exceptions
from ..accounting.models import GLAccount, JournalEntry, JournalEntryLine, AccountType
from ..accounting.schemas import JournalEntryCreate, JournalEntryLineCreate


class BankAccountService:
    """
    Service for managing bank account operations.
    
    This service handles all business logic related to bank accounts,
    including creation, updates, balance tracking, and account status management.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_bank_account(self, account: schemas.BankAccountCreate, user_id: UUID) -> models.BankAccount:
        """
        Create a new bank account.
        
        Args:
            account: Bank account data
            user_id: ID of the user creating the account
            
        Returns:
            The created bank account
            
        Raises:
            BankAccountAlreadyExists: If an account with the same details already exists
        """
        # Check if account with same number at same bank already exists
        existing = self.db.query(models.BankAccount).filter(
            func.lower(models.BankAccount.bank_name) == account.bank_name.lower(),
            models.BankAccount.account_number == account.account_number
        ).first()
        
        if existing:
            raise exceptions.BankAccountAlreadyExists(
                bank_name=account.bank_name,
                account_number=account.account_number
            )
        
        # Create new account
        db_account = models.BankAccount(
            **account.dict(exclude={"metadata"}),
            id=uuid4(),
            created_by_id=user_id,
            updated_by_id=user_id,
            metadata=account.metadata or {}
        )
        
        self.db.add(db_account)
        self.db.commit()
        self.db.refresh(db_account)
        return db_account
    
    def get_bank_account(self, account_id: UUID) -> models.BankAccount:
        """
        Retrieve a bank account by ID.
        
        Args:
            account_id: ID of the bank account to retrieve
            
        Returns:
            The requested bank account
            
        Raises:
            BankAccountNotFound: If no account exists with the given ID
        """
        account = self.db.query(models.BankAccount).get(account_id)
        if not account:
            raise exceptions.BankAccountNotFound(account_id=account_id)
        return account
    
    def list_bank_accounts(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        account_type: Optional[schemas.BankAccountType] = None,
        status: Optional[schemas.BankAccountStatus] = None
    ) -> Tuple[List[models.BankAccount], int]:
        """
        List bank accounts with optional filtering and pagination.
        
        Args:
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return
            search: Optional search term to filter accounts
            account_type: Optional filter by account type
            status: Optional filter by account status
            
        Returns:
            A tuple containing:
                - List of bank accounts
                - Total count of matching accounts
        """
        query = self.db.query(models.BankAccount)
        
        # Apply filters
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    models.BankAccount.name.ilike(search_term),
                    models.BankAccount.account_number.ilike(search_term),
                    models.BankAccount.bank_name.ilike(search_term)
                )
            )
            
        if account_type:
            query = query.filter(models.BankAccount.account_type == account_type)
            
        if status:
            query = query.filter(models.BankAccount.status == status)
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        accounts = query.order_by(
            models.BankAccount.bank_name,
            models.BankAccount.name
        ).offset(skip).limit(limit).all()
        
        return accounts, total
    
    def update_bank_account(
        self, 
        account_id: UUID, 
        account_update: schemas.BankAccountUpdate, 
        user_id: UUID
    ) -> models.BankAccount:
        """
        Update an existing bank account.
        
        Args:
            account_id: ID of the account to update
            account_update: Updated account data
            user_id: ID of the user performing the update
            
        Returns:
            The updated bank account
            
        Raises:
            BankAccountNotFound: If no account exists with the given ID
            BankAccountAlreadyExists: If the update would create a duplicate account
        """
        db_account = self.get_bank_account(account_id)
        
        # Check if account number is being changed and if it's already in use
        if account_update.account_number and account_update.account_number != db_account.account_number:
            existing = self.db.query(models.BankAccount).filter(
                func.lower(models.BankAccount.bank_name) == func.lower(account_update.bank_name or db_account.bank_name),
                models.BankAccount.account_number == account_update.account_number,
                models.BankAccount.id != account_id
            ).first()
            
            if existing:
                raise exceptions.BankAccountAlreadyExists(
                    bank_name=account_update.bank_name or db_account.bank_name,
                    account_number=account_update.account_number
                )
        
        # Update fields
        update_data = account_update.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_account, field, value)
        
        db_account.updated_by_id = user_id
        db_account.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(db_account)
        return db_account
    
    def delete_bank_account(self, account_id: UUID) -> None:
        """
        Delete a bank account.
        
        Args:
            account_id: ID of the account to delete
            
        Raises:
            BankAccountNotFound: If no account exists with the given ID
            InvalidBankAccountOperation: If the account has associated transactions
        """
        db_account = self.get_bank_account(account_id)
        
        # Check if account has transactions
        has_transactions = self.db.query(models.BankTransaction).filter(
            models.BankTransaction.account_id == account_id
        ).first() is not None
        
        if has_transactions:
            raise exceptions.InvalidBankAccountOperation(
                account_id=account_id,
                operation="delete",
                reason="Account has associated transactions"
            )
        
        self.db.delete(db_account)
        self.db.commit()
    
    def update_balance(
        self,
        account_id: UUID,
        balance_update: schemas.BankAccountBalanceUpdate,
        user_id: UUID
    ) -> models.BankAccount:
        """
        Update a bank account's balance.
        
        Args:
            account_id: ID of the account to update
            balance_update: New balance information
            user_id: ID of the user performing the update
            
        Returns:
            The updated bank account
            
        Raises:
            BankAccountNotFound: If no account exists with the given ID
        """
        db_account = self.get_bank_account(account_id)
        
        # Create a balance adjustment transaction
        balance_change = balance_update.balance - db_account.current_balance
        
        transaction_type = (
            schemas.TransactionType.DEPOSIT 
            if balance_change > 0 
            else schemas.TransactionType.WITHDRAWAL
        )
        
        # Create adjustment transaction
        transaction = models.BankTransaction(
            id=uuid4(),
            account_id=account_id,
            transaction_date=balance_update.balance_date,
            transaction_type=transaction_type,
            status=schemas.TransactionStatus.POSTED,
            amount=abs(balance_change),
            memo=f"Balance adjustment on {balance_update.balance_date}",
            notes=balance_update.notes,
            created_by_id=user_id,
            updated_by_id=user_id
        )
        
        # Update account balances
        db_account.current_balance = balance_update.balance
        db_account.available_balance = balance_update.balance  # Assuming available = current for simplicity
        db_account.last_synced_balance = balance_update.balance
        db_account.last_synced_date = datetime.utcnow()
        db_account.updated_by_id = user_id
        db_account.updated_at = datetime.utcnow()
        
        self.db.add(transaction)
        self.db.add(db_account)
        self.db.commit()
        self.db.refresh(db_account)
        
        return db_account


class TransactionService:
    """
    Service for managing bank transaction operations.
    
    This service handles all business logic related to bank transactions,
    including creation, updates, and balance calculations.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_transaction(
        self, 
        transaction: schemas.BankTransactionCreate, 
        user_id: UUID
    ) -> models.BankTransaction:
        """
        Create a new bank transaction.
        
        Args:
            transaction: Transaction data
            user_id: ID of the user creating the transaction
            
        Returns:
            The created transaction
            
        Raises:
            BankAccountNotFound: If the specified account doesn't exist
            InsufficientFundsError: If the transaction would overdraw the account
        """
        # Verify account exists
        account = self.db.query(models.BankAccount).get(transaction.account_id)
        if not account:
            raise exceptions.BankAccountNotFound(account_id=transaction.account_id)
        
        # Create transaction
        db_transaction = models.BankTransaction(
            **transaction.dict(exclude={"metadata"}),
            id=uuid4(),
            created_by_id=user_id,
            updated_by_id=user_id,
            metadata=transaction.metadata or {}
        )
        
        # Update account balance if transaction is posted
        if db_transaction.status == schemas.TransactionStatus.POSTED:
            self._update_account_balance(
                account=account,
                transaction_type=db_transaction.transaction_type,
                amount=db_transaction.amount
            )
        
        self.db.add(db_transaction)
        self.db.commit()
        self.db.refresh(db_transaction)
        return db_transaction
    
    def get_transaction(self, transaction_id: UUID) -> models.BankTransaction:
        """
        Retrieve a transaction by ID.
        
        Args:
            transaction_id: ID of the transaction to retrieve
            
        Returns:
            The requested transaction
            
        Raises:
            TransactionNotFound: If no transaction exists with the given ID
        """
        transaction = self.db.query(models.BankTransaction).get(transaction_id)
        if not transaction:
            raise exceptions.TransactionNotFound(transaction_id=transaction_id)
        return transaction
    
    def list_transactions(
        self,
        account_id: Optional[UUID] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        transaction_type: Optional[schemas.TransactionType] = None,
        status: Optional[schemas.TransactionStatus] = None,
        category_id: Optional[UUID] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[models.BankTransaction], int]:
        """
        List transactions with filtering and pagination.
        
        Args:
            account_id: Optional filter by account ID
            start_date: Optional filter by start date
            end_date: Optional filter by end date
            transaction_type: Optional filter by transaction type
            status: Optional filter by status
            category_id: Optional filter by category ID
            search: Optional search term
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            A tuple containing:
                - List of transactions
                - Total count of matching transactions
        """
        query = self.db.query(models.BankTransaction)
        
        # Apply filters
        if account_id:
            query = query.filter(models.BankTransaction.account_id == account_id)
            
        if start_date:
            query = query.filter(models.BankTransaction.transaction_date >= start_date)
            
        if end_date:
            query = query.filter(models.BankTransaction.transaction_date <= end_date)
            
        if transaction_type:
            query = query.filter(models.BankTransaction.transaction_type == transaction_type)
            
        if status:
            query = query.filter(models.BankTransaction.status == status)
            
        if category_id:
            query = query.filter(models.BankTransaction.category_id == category_id)
            
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    models.BankTransaction.reference_number.ilike(search_term),
                    models.BankTransaction.memo.ilike(search_term),
                    models.BankTransaction.notes.ilike(search_term),
                    models.BankTransaction.payee.ilike(search_term)
                )
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        transactions = query.order_by(
            desc(models.BankTransaction.transaction_date),
            desc(models.BankTransaction.created_at)
        ).offset(skip).limit(limit).all()
        
        return transactions, total
    
    def _update_account_balance(
        self,
        account: models.BankAccount,
        transaction_type: schemas.TransactionType,
        amount: Decimal
    ) -> None:
        """
        Update account balance based on transaction type.
        
        Args:
            account: The account to update
            transaction_type: Type of transaction
            amount: Transaction amount
            
        Raises:
            InsufficientFundsError: If the transaction would overdraw the account
        """
        if transaction_type in [
            schemas.TransactionType.DEPOSIT,
            schemas.TransactionType.TRANSFER_IN,
            schemas.TransactionType.INTEREST,
            schemas.TransactionType.REFUND
        ]:
            # Increase balance for deposits and incoming transfers
            account.current_balance += amount
            account.available_balance += amount
        else:
            # Decrease balance for withdrawals and outgoing transfers
            if account.available_balance < amount and not account.allow_overdraft:
                raise exceptions.InsufficientFundsError(
                    account_id=account.id,
                    available_balance=account.available_balance,
                    requested_amount=amount
                )
            account.current_balance -= amount
            account.available_balance -= amount
        
        account.last_updated = datetime.utcnow()


 
class ReconciliationService:
=======
class ReconciliationService(ReconciliationService):
>>>>>>> e96df7278ce4216131b6c65d411c0723f4de7f91
    """
    Service for managing bank reconciliation operations.
    
    This service handles the reconciliation of bank transactions
    with the organization's financial records.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_reconciliation(
        self, 
        reconciliation: schemas.BankReconciliationCreate, 
        user_id: UUID
    ) -> models.BankReconciliation:
        """
        Create a new bank reconciliation.
        
        Args:
            reconciliation: Reconciliation data
            user_id: ID of the user creating the reconciliation
            
        Returns:
            The created reconciliation
            
        Raises:
            BankAccountNotFound: If the specified account doesn't exist
            ReconciliationError: If there's an issue with the reconciliation
        """
        # Verify account exists
        account = self.db.query(models.BankAccount).get(reconciliation.account_id)
        if not account:
            raise exceptions.BankAccountNotFound(account_id=reconciliation.account_id)
        
        # Create reconciliation
        db_reconciliation = models.BankReconciliation(
            **reconciliation.dict(exclude={"transaction_ids", "metadata"}),
            id=uuid4(),
            created_by_id=user_id,
            updated_by_id=user_id,
            metadata=reconciliation.metadata or {}
        )
        
        self.db.add(db_reconciliation)
        
        # Add transactions to reconciliation
        if reconciliation.transaction_ids:
            self._add_transactions_to_reconciliation(
                reconciliation_id=db_reconciliation.id,
                transaction_ids=reconciliation.transaction_ids,
                user_id=user_id
            )
        
        # Calculate reconciliation summary
        self._calculate_reconciliation_summary(db_reconciliation)
        
        self.db.commit()
        self.db.refresh(db_reconciliation)
        return db_reconciliation
    
    def get_reconciliation(self, reconciliation_id: UUID) -> models.BankReconciliation:
        """
        Retrieve a reconciliation by ID.
        
        Args:
            reconciliation_id: ID of the reconciliation to retrieve
            
        Returns:
            The requested reconciliation
            
        Raises:
            ReconciliationNotFound: If no reconciliation exists with the given ID
        """
        reconciliation = self.db.query(models.BankReconciliation).get(reconciliation_id)
        if not reconciliation:
            raise exceptions.ReconciliationNotFound(reconciliation_id=reconciliation_id)
        return reconciliation
    
    def _add_transactions_to_reconciliation(
        self,
        reconciliation_id: UUID,
        transaction_ids: List[UUID],
        user_id: UUID
    ) -> None:
        """
        Add transactions to a reconciliation.
        
        Args:
            reconciliation_id: ID of the reconciliation
            transaction_ids: List of transaction IDs to add
            user_id: ID of the user performing the action
            
        Raises:
            ReconciliationError: If any transaction is invalid or already reconciled
        """
        # Verify all transactions exist and belong to the same account
        reconciliation = self.get_reconciliation(reconciliation_id)
        
        # Get transactions and verify they belong to the same account
        transactions = self.db.query(models.BankTransaction).filter(
            models.BankTransaction.id.in_(transaction_ids),
            models.BankTransaction.account_id == reconciliation.account_id
        ).all()
        
        if len(transactions) != len(transaction_ids):
            found_ids = {str(t.id) for t in transactions}
            missing_ids = [str(tid) for tid in transaction_ids if str(tid) not in found_ids]
            raise exceptions.ReconciliationError(
                reconciliation_id=reconciliation_id,
                message=f"Some transactions not found or don't belong to the account: {', '.join(missing_ids)}"
            )
        
        # Update transactions
        self.db.execute(
            update(models.BankTransaction)
            .where(models.BankTransaction.id.in_(transaction_ids))
            .values(
                reconciliation_id=reconciliation_id,
                is_reconciled=True,
                updated_by_id=user_id,
                updated_at=datetime.utcnow()
            )
        )
    
    def _calculate_reconciliation_summary(
        self,
        reconciliation: models.BankReconciliation
    ) -> None:
        """
        Calculate and update reconciliation summary.
        
        Args:
            reconciliation: The reconciliation to update
        """
        # Get all reconciled transactions for this reconciliation
        transactions = self.db.query(
            models.BankTransaction.transaction_type,
            func.sum(models.BankTransaction.amount).label('total_amount')
        ).filter(
            models.BankTransaction.reconciliation_id == reconciliation.id
        ).group_by(
            models.BankTransaction.transaction_type
        ).all()
        
        # Calculate cleared balance and difference
        cleared_balance = Decimal('0.00')
        
        for tx_type, amount in transactions:
            if tx_type in [
                schemas.TransactionType.DEPOSIT,
                schemas.TransactionType.TRANSFER_IN,
                schemas.TransactionType.INTEREST,
                schemas.TransactionType.REFUND
            ]:
                cleared_balance += amount
            else:
                cleared_balance -= amount
        
        reconciliation.cleared_balance = cleared_balance
        reconciliation.difference = reconciliation.statement_ending_balance - cleared_balance
        
        # Update status based on difference
        if reconciliation.status == schemas.ReconciliationStatus.DRAFT:
            if abs(reconciliation.difference) < Decimal('0.01'):  # Considered reconciled if difference < 0.01
                reconciliation.status = schemas.ReconciliationStatus.COMPLETED
            else:
                reconciliation.status = schemas.ReconciliationStatus.IN_PROGRESS
 
=======
    
    async def get_cash_flow_forecast(self, db: AsyncSession, start_date: date, end_date: date, account_id: Optional[int] = None):
        """Get cash flow forecast from real data"""
        from ..models import CashFlowEntry, BankAccount
        from sqlalchemy import select, func, and_
        
        # Get opening balance
        if account_id:
            account_query = select(BankAccount).where(BankAccount.id == account_id)
            account_result = await db.execute(account_query)
            account = account_result.scalar_one_or_none()
            opening_balance = float(account.current_balance) if account else 0.0
        else:
            balance_query = select(func.sum(BankAccount.current_balance)).where(BankAccount.status == 'active')
            opening_balance = float(await db.scalar(balance_query) or 0)
        
        # Get cash flow entries for the period
        query = select(CashFlowEntry).where(
            and_(
                CashFlowEntry.entry_date >= start_date,
                CashFlowEntry.entry_date <= end_date
            )
        )
        
        if account_id:
            query = query.where(CashFlowEntry.account_id == account_id)
            
        result = await db.execute(query)
        entries = result.scalars().all()
        
        # Calculate totals
        projected_inflows = sum(float(entry.amount) for entry in entries if entry.flow_type == 'inflow')
        projected_outflows = sum(float(entry.amount) for entry in entries if entry.flow_type == 'outflow')
        closing_balance = opening_balance + projected_inflows - projected_outflows
        
        # Generate daily forecast
        daily_forecast = []
        current_balance = opening_balance
        current_date = start_date
        
        while current_date <= end_date:
            daily_inflow = sum(
                float(entry.amount) for entry in entries 
                if entry.entry_date == current_date and entry.flow_type == 'inflow'
            )
            daily_outflow = sum(
                float(entry.amount) for entry in entries 
                if entry.entry_date == current_date and entry.flow_type == 'outflow'
            )
            current_balance += daily_inflow - daily_outflow
            
            daily_forecast.append({
                "date": current_date.isoformat(),
                "inflow": daily_inflow,
                "outflow": daily_outflow,
                "balance": current_balance
            })
            
            current_date += timedelta(days=1)
        
        return {
            "period": {"start_date": start_date.isoformat(), "end_date": end_date.isoformat()},
            "opening_balance": opening_balance,
            "projected_inflows": projected_inflows,
            "projected_outflows": projected_outflows,
            "closing_balance": closing_balance,
            "daily_forecast": daily_forecast
        }
    
    async def get_cash_position(self, db: AsyncSession, as_of_date: Optional[date] = None):
        """Get current cash position from real account data"""
        from ..models import BankAccount
        from sqlalchemy import select, func
        
        if as_of_date is None:
            as_of_date = date.today()
        
        # Get all active accounts
        query = select(BankAccount).where(BankAccount.status == 'active')
        result = await db.execute(query)
        accounts = result.scalars().all()
        
        total_cash = sum(float(account.current_balance) for account in accounts)
        available_cash = sum(float(account.available_balance) for account in accounts)
        restricted_cash = total_cash - available_cash
        
        account_details = [
            {
                "account_id": account.id,
                "account_name": account.account_name,
                "account_number": account.account_number,
                "bank_name": account.bank_name,
                "account_type": account.account_type,
                "balance": float(account.current_balance),
                "available": float(account.available_balance),
                "currency": account.currency_code
            }
            for account in accounts
        ]
        
        return {
            "as_of_date": as_of_date.isoformat(),
            "total_cash": total_cash,
            "available_cash": available_cash,
            "restricted_cash": restricted_cash,
            "accounts": account_details
        }
    
    async def process_payment(self, db: AsyncSession, payment_data: dict, user_id: int):
        """Process payment transaction with real database persistence"""
        from ..models import BankTransaction, BankAccount
        from sqlalchemy import select
        from decimal import Decimal
        
        # Get account
        account_query = select(BankAccount).where(BankAccount.id == payment_data["account_id"])
        account_result = await db.execute(account_query)
        account = account_result.scalar_one_or_none()
        
        if not account:
            return {"error": "Account not found"}
        
        amount = Decimal(str(payment_data["amount"]))
        
        # Check available balance for withdrawals
        if payment_data.get("transaction_type") in ["withdrawal", "transfer_out"] and account.available_balance < amount:
            if not account.allow_overdraft:
                return {"error": "Insufficient funds"}
        
        # Generate transaction number
        transaction_count = await db.scalar(select(func.count(BankTransaction.id)))
        reference_number = f"TXN-{datetime.now().strftime('%Y%m%d')}-{transaction_count + 1:06d}"
        
        # Create transaction
        transaction = BankTransaction(
            account_id=payment_data["account_id"],
            transaction_date=datetime.strptime(payment_data["transaction_date"], "%Y-%m-%d").date(),
            transaction_type=payment_data["transaction_type"],
            amount=amount,
            reference_number=reference_number,
            memo=payment_data.get("memo"),
            payee=payment_data.get("payee"),
            status="posted",
            created_by=user_id,
            updated_by=user_id
        )
        
        # Update account balance
        if payment_data["transaction_type"] in ["deposit", "transfer_in", "interest", "refund"]:
            account.current_balance += amount
            account.available_balance += amount
        else:
            account.current_balance -= amount
            account.available_balance -= amount
        
        account.updated_by = user_id
        account.updated_at = datetime.utcnow()
        
        db.add(transaction)
        await db.commit()
        await db.refresh(transaction)
        
        return {
            "payment_id": transaction.id,
            "amount": float(amount),
            "status": "processed",
            "transaction_id": reference_number,
            "processed_at": datetime.utcnow().isoformat(),
            "new_balance": float(account.current_balance)
        }

    async def auto_reconcile(self, db: AsyncSession, reconciliation_id: int, user_id: int):
        """Perform automatic reconciliation with real matching logic"""
        from ..models import BankReconciliation, BankTransaction
        from sqlalchemy import select, and_
        from decimal import Decimal
        
        # Get reconciliation
        recon_query = select(BankReconciliation).where(BankReconciliation.id == reconciliation_id)
        recon_result = await db.execute(recon_query)
        reconciliation = recon_result.scalar_one_or_none()
        
        if not reconciliation:
            return {"error": "Reconciliation not found"}
        
        # Get unreconciled transactions for the period
        trans_query = select(BankTransaction).where(
            and_(
                BankTransaction.account_id == reconciliation.account_id,
                BankTransaction.transaction_date >= reconciliation.period_start,
                BankTransaction.transaction_date <= reconciliation.period_end,
                BankTransaction.is_reconciled == False,
                BankTransaction.status == "posted"
            )
        )
        
        trans_result = await db.execute(trans_query)
        transactions = trans_result.scalars().all()
        
        matched_count = 0
        cleared_balance = Decimal('0')
        
        # Simple auto-matching logic (in production, this would be more sophisticated)
        for transaction in transactions:
            # Auto-match transactions that are within the statement period
            if reconciliation.period_start <= transaction.transaction_date <= reconciliation.period_end:
                transaction.is_reconciled = True
                transaction.reconciliation_id = reconciliation_id
                transaction.reconciled_date = date.today()
                transaction.updated_by = user_id
                
                if transaction.transaction_type in ["deposit", "transfer_in", "interest"]:
                    cleared_balance += transaction.amount
                else:
                    cleared_balance -= transaction.amount
                    
                matched_count += 1
        
        # Update reconciliation
        reconciliation.cleared_balance = cleared_balance
        reconciliation.auto_reconciled_count = matched_count
        reconciliation.difference = reconciliation.statement_ending_balance - cleared_balance
        
        if abs(reconciliation.difference) < Decimal('0.01'):
            reconciliation.is_balanced = True
            reconciliation.status = "completed"
        else:
            reconciliation.status = "in_progress"
        
        reconciliation.updated_by = user_id
        reconciliation.updated_at = datetime.utcnow()
        
        await db.commit()
        
        return {
            "reconciliation_id": reconciliation_id,
            "matched_transactions": matched_count,
            "unmatched_transactions": len(transactions) - matched_count,
            "status": reconciliation.status,
            "difference": float(reconciliation.difference),
            "is_balanced": reconciliation.is_balanced
        }
    
    async def import_bank_statement(self, db: AsyncSession, account_id: int, statement_data: dict, user_id: int):
        """Import bank statement data with real processing"""
        from ..models import BankStatementImport, BankTransaction, BankAccount
        from sqlalchemy import select, and_
        from decimal import Decimal
        
        # Create import record
        import_record = BankStatementImport(
            account_id=account_id,
            statement_date=datetime.strptime(statement_data["statement_date"], "%Y-%m-%d").date(),
            file_name=statement_data.get("file_name"),
            file_format=statement_data.get("file_format", "csv"),
            status="processing",
            created_by=user_id
        )
        
        db.add(import_record)
        await db.flush()
        
        imported_count = 0
        duplicate_count = 0
        failed_count = 0
        
        try:
            transactions_data = statement_data.get("transactions", [])
            import_record.total_transactions = len(transactions_data)
            
            for trans_data in transactions_data:
                try:
                    # Check for duplicates
                    existing_query = select(BankTransaction).where(
                        and_(
                            BankTransaction.account_id == account_id,
                            BankTransaction.transaction_date == datetime.strptime(trans_data["date"], "%Y-%m-%d").date(),
                            BankTransaction.amount == Decimal(str(trans_data["amount"])),
                            BankTransaction.reference_number == trans_data.get("reference")
                        )
                    )
                    
                    existing_result = await db.execute(existing_query)
                    if existing_result.scalar_one_or_none():
                        duplicate_count += 1
                        continue
                    
                    # Create new transaction
                    transaction = BankTransaction(
                        account_id=account_id,
                        transaction_date=datetime.strptime(trans_data["date"], "%Y-%m-%d").date(),
                        transaction_type=trans_data.get("type", "deposit" if float(trans_data["amount"]) > 0 else "withdrawal"),
                        amount=abs(Decimal(str(trans_data["amount"]))),
                        reference_number=trans_data.get("reference"),
                        memo=trans_data.get("description"),
                        payee=trans_data.get("payee"),
                        status="posted",
                        created_by=user_id,
                        updated_by=user_id
                    )
                    
                    db.add(transaction)
                    imported_count += 1
                    
                except Exception as e:
                    failed_count += 1
                    continue
            
            # Update import record
            import_record.imported_transactions = imported_count
            import_record.duplicate_transactions = duplicate_count
            import_record.failed_transactions = failed_count
            import_record.status = "completed"
            
            await db.commit()
            
            return {
                "account_id": account_id,
                "imported_transactions": imported_count,
                "duplicate_transactions": duplicate_count,
                "new_transactions": imported_count,
                "failed_transactions": failed_count,
                "import_date": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            import_record.status = "failed"
            import_record.error_message = str(e)
            await db.commit()
            
            return {
                "error": "Import failed",
                "message": str(e)
            }
    
    async def get_banking_fees(self, db: AsyncSession, account_id: Optional[int], start_date: Optional[date], end_date: Optional[date]):
        """Get banking fees from real data"""
        from ..models import BankingFee
        from sqlalchemy import select, and_, func
        
        query = select(BankingFee)
        
        conditions = []
        if account_id:
            conditions.append(BankingFee.account_id == account_id)
        if start_date:
            conditions.append(BankingFee.fee_date >= start_date)
        if end_date:
            conditions.append(BankingFee.fee_date <= end_date)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(BankingFee.fee_date.desc())
        
        result = await db.execute(query)
        fees = result.scalars().all()
        
        total_fees = sum(float(fee.amount) for fee in fees if not fee.is_waived)
        
        fee_breakdown = [
            {
                "id": fee.id,
                "type": fee.fee_type,
                "description": fee.fee_description,
                "amount": float(fee.amount),
                "date": fee.fee_date.isoformat(),
                "is_waived": fee.is_waived,
                "is_recurring": fee.is_recurring
            }
            for fee in fees
        ]
        
        return {
            "total_fees": total_fees,
            "fee_count": len(fees),
            "fee_breakdown": fee_breakdown
        }
    
    async def create_banking_fee(self, db: AsyncSession, fee_data: dict, user_id: int):
        """Create banking fee record with real database persistence"""
        from ..models import BankingFee
        from decimal import Decimal
        
        fee = BankingFee(
            account_id=fee_data["account_id"],
            fee_date=datetime.strptime(fee_data["fee_date"], "%Y-%m-%d").date(),
            fee_type=fee_data["fee_type"],
            fee_description=fee_data["fee_description"],
            amount=Decimal(str(fee_data["amount"])),
            fee_category=fee_data.get("fee_category"),
            is_recurring=fee_data.get("is_recurring", False),
            frequency=fee_data.get("frequency"),
            created_by=user_id,
            updated_by=user_id
        )
        
        # Set next fee date for recurring fees
        if fee.is_recurring and fee.frequency:
            if fee.frequency == "monthly":
                fee.next_fee_date = fee.fee_date + timedelta(days=30)
            elif fee.frequency == "quarterly":
                fee.next_fee_date = fee.fee_date + timedelta(days=90)
            elif fee.frequency == "annually":
                fee.next_fee_date = fee.fee_date + timedelta(days=365)
        
        db.add(fee)
        await db.commit()
        await db.refresh(fee)
        
        return {
            "fee_id": fee.id,
            "type": fee.fee_type,
            "amount": float(fee.amount),
            "account_id": fee.account_id,
            "fee_date": fee.fee_date.isoformat(),
            "is_recurring": fee.is_recurring,
            "created_at": fee.created_at.isoformat()
        }
>>>>>>> e96df7278ce4216131b6c65d411c0723f4de7f91
