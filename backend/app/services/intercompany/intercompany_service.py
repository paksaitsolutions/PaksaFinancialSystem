"""
Intercompany transaction service.
"""
from datetime import date, datetime
from typing import List, Optional, Dict, Any

from decimal import Decimal
from sqlalchemy import and_, or_, func, desc
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.exceptions import NotFoundException, ValidationException
from app.models.intercompany import (
from app.models.journal_entry import JournalEntry, JournalEntryLine, JournalEntryStatus



    IntercompanyTransaction, 
    IntercompanyTransactionType, 
    IntercompanyTransactionStatus,
    IntercompanyReconciliation
)


class IntercompanyService:
    """Service for managing intercompany transactions."""
    
    def __init__(self, db: Session):
        """  Init  ."""
        self.db = db
    
    def create_transaction(self, transaction_data: Dict[str, Any], created_by: UUID) -> IntercompanyTransaction:
        """Create Transaction."""
        """Create a new intercompany transaction."""
        transaction_number = self._generate_transaction_number()
        
        transaction = IntercompanyTransaction(
            transaction_number=transaction_number,
            transaction_type=IntercompanyTransactionType(transaction_data['transaction_type']),
            source_company_id=transaction_data['source_company_id'],
            target_company_id=transaction_data['target_company_id'],
            amount=Decimal(str(transaction_data['amount'])),
            currency_id=transaction_data['currency_id'],
            transaction_date=transaction_data['transaction_date'],
            due_date=transaction_data.get('due_date'),
            source_account_id=transaction_data['source_account_id'],
            target_account_id=transaction_data['target_account_id'],
            description=transaction_data.get('description'),
            reference_number=transaction_data.get('reference_number'),
            created_by=created_by,
            updated_by=created_by
        )
        
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        
        return transaction
    
    def approve_transaction(self, transaction_id: UUID, approved_by: UUID) -> IntercompanyTransaction:
        """Approve Transaction."""
        """Approve an intercompany transaction."""
        transaction = self.get_transaction(transaction_id)
        if not transaction:
            raise NotFoundException(f"Transaction {transaction_id} not found")
        
        if transaction.status != IntercompanyTransactionStatus.PENDING:
            raise ValidationException("Only pending transactions can be approved")
        
        transaction.status = IntercompanyTransactionStatus.APPROVED
        transaction.approved_by = approved_by
        transaction.approved_at = datetime.utcnow()
        transaction.updated_by = approved_by
        transaction.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(transaction)
        
        return transaction
    
    def post_transaction(self, transaction_id: UUID, posted_by: UUID) -> IntercompanyTransaction:
        """Post Transaction."""
        """Post an intercompany transaction by creating journal entries."""
        transaction = self.get_transaction(transaction_id)
        if not transaction:
            raise NotFoundException(f"Transaction {transaction_id} not found")
        
        if transaction.status != IntercompanyTransactionStatus.APPROVED:
            raise ValidationException("Only approved transactions can be posted")
        
        # Create journal entries for both companies
        source_je = self._create_journal_entry(
            transaction, 
            transaction.source_company_id, 
            transaction.source_account_id,
            is_source=True,
            created_by=posted_by
        )
        
        target_je = self._create_journal_entry(
            transaction, 
            transaction.target_company_id, 
            transaction.target_account_id,
            is_source=False,
            created_by=posted_by
        )
        
        # Update transaction
        transaction.source_journal_entry_id = source_je.id
        transaction.target_journal_entry_id = target_je.id
        transaction.status = IntercompanyTransactionStatus.POSTED
        transaction.updated_by = posted_by
        transaction.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(transaction)
        
        return transaction
    
    def get_transaction(self, transaction_id: UUID) -> Optional[IntercompanyTransaction]:
        """Get Transaction."""
        """Get an intercompany transaction by ID."""
        return self.db.query(IntercompanyTransaction).filter(
            IntercompanyTransaction.id == transaction_id
        ).first()
    
    def list_transactions(
        """List Transactions."""
        self, 
        company_id: Optional[UUID] = None,
        status: Optional[IntercompanyTransactionStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[IntercompanyTransaction]:
        """List Transactions."""
        """List intercompany transactions with filters."""
        query = self.db.query(IntercompanyTransaction)
        
        if company_id:
            query = query.filter(
                or_(
                    IntercompanyTransaction.source_company_id == company_id,
                    IntercompanyTransaction.target_company_id == company_id
                )
            )
        
        if status:
            query = query.filter(IntercompanyTransaction.status == status)
        
        return query.order_by(desc(IntercompanyTransaction.transaction_date))\
                   .offset(skip).limit(limit).all()
    
    def _create_journal_entry(
        """ Create Journal Entry."""
        self, 
        transaction: IntercompanyTransaction, 
        company_id: UUID,
        account_id: UUID,
        is_source: bool,
        created_by: UUID
    ) -> JournalEntry:
        """ Create Journal Entry."""
        """Create a journal entry for an intercompany transaction."""
        is_debit = self._determine_debit_credit(transaction.transaction_type, is_source)
        
        je = JournalEntry(
            entry_number=f"IC-{transaction.transaction_number}-{'S' if is_source else 'T'}",
            entry_date=transaction.transaction_date,
            description=f"Intercompany {transaction.transaction_type.value}: {transaction.description}",
            reference=transaction.reference_number,
            status=JournalEntryStatus.POSTED,
            created_by=created_by,
            updated_by=created_by
        )
        
        self.db.add(je)
        self.db.flush()
        
        je_line = JournalEntryLine(
            journal_entry_id=je.id,
            account_id=account_id,
            description=transaction.description,
            amount=transaction.amount,
            is_debit=is_debit,
            created_by=created_by,
            updated_by=created_by
        )
        
        self.db.add(je_line)
        
        return je
    
    def _determine_debit_credit(self, transaction_type: IntercompanyTransactionType, is_source: bool) -> bool:
        """ Determine Debit Credit."""
        """Determine if the entry should be a debit based on transaction type and source/target."""
        debit_rules = {
            IntercompanyTransactionType.SALE: is_source,
            IntercompanyTransactionType.PURCHASE: not is_source,
            IntercompanyTransactionType.LOAN: is_source,
            IntercompanyTransactionType.EXPENSE_ALLOCATION: not is_source,
            IntercompanyTransactionType.REVENUE_SHARING: is_source,
            IntercompanyTransactionType.TRANSFER: is_source,
        }
        
        return debit_rules.get(transaction_type, is_source)
    
    def _generate_transaction_number(self) -> str:
        """ Generate Transaction Number."""
        """Generate a unique transaction number."""
        last_transaction = self.db.query(IntercompanyTransaction)\
            .order_by(desc(IntercompanyTransaction.created_at))\
            .first()
        
        if last_transaction and last_transaction.transaction_number.startswith('IC'):
            try:
                last_num = int(last_transaction.transaction_number.split('-')[1])
                next_num = last_num + 1
            except (IndexError, ValueError):
                next_num = 1
        else:
            next_num = 1
        
        return f"IC-{next_num:06d}"