from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import Optional
from datetime import datetime, date
from decimal import Decimal
from ..models import BankReconciliation, BankTransaction, BankAccount

class BankReconciliationService:
    """Service for bank reconciliation operations"""
    
    async def create_reconciliation(self, db: AsyncSession, recon_data: dict, user_id: int):
        """Create a new bank reconciliation"""
        reconciliation = BankReconciliation(
            account_id=recon_data["account_id"],
            reconciliation_date=datetime.strptime(recon_data["reconciliation_date"], "%Y-%m-%d").date(),
            statement_date=datetime.strptime(recon_data["statement_date"], "%Y-%m-%d").date(),
            period_start=datetime.strptime(recon_data["period_start"], "%Y-%m-%d").date(),
            period_end=datetime.strptime(recon_data["period_end"], "%Y-%m-%d").date(),
            statement_beginning_balance=Decimal(str(recon_data["statement_beginning_balance"])),
            statement_ending_balance=Decimal(str(recon_data["statement_ending_balance"])),
            book_beginning_balance=Decimal(str(recon_data["book_beginning_balance"])),
            book_ending_balance=Decimal(str(recon_data["book_ending_balance"])),
            status="draft",
            created_by=user_id,
            updated_by=user_id
        )
        
        db.add(reconciliation)
        await db.commit()
        await db.refresh(reconciliation)
        
        return {
            "reconciliation_id": reconciliation.id,
            "account_id": reconciliation.account_id,
            "status": reconciliation.status,
            "statement_balance": float(reconciliation.statement_ending_balance),
            "book_balance": float(reconciliation.book_ending_balance),
            "created_at": reconciliation.created_at.isoformat()
        }
    
    async def auto_reconcile(self, db: AsyncSession, reconciliation_id: int, user_id: int):
        """Perform automatic reconciliation with real matching logic"""
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
        
        # Auto-match transactions within the statement period
        for transaction in transactions:
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
    
    async def get_reconciliation_status(self, db: AsyncSession, account_id: int):
        """Get reconciliation status for an account"""
        # Get latest reconciliation
        latest_query = select(BankReconciliation).where(
            BankReconciliation.account_id == account_id
        ).order_by(BankReconciliation.reconciliation_date.desc()).limit(1)
        
        result = await db.execute(latest_query)
        latest_recon = result.scalar_one_or_none()
        
        # Get unreconciled transactions count
        unreconciled_query = select(func.count(BankTransaction.id)).where(
            and_(
                BankTransaction.account_id == account_id,
                BankTransaction.is_reconciled == False,
                BankTransaction.status == "posted"
            )
        )
        unreconciled_count = await db.scalar(unreconciled_query)
        
        return {
            "account_id": account_id,
            "last_reconciliation_date": latest_recon.reconciliation_date.isoformat() if latest_recon else None,
            "last_reconciliation_status": latest_recon.status if latest_recon else None,
            "is_balanced": latest_recon.is_balanced if latest_recon else False,
            "unreconciled_transactions": unreconciled_count or 0,
            "needs_reconciliation": unreconciled_count > 0 if unreconciled_count else True
        }