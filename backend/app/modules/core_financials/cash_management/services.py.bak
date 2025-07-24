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
from app.core.database import Base
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
