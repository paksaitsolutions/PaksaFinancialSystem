from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Dict, Optional
from datetime import datetime, date
from decimal import Decimal

class CrossModuleIntegrationService:
    """Service for cross-module data flow and integration"""
    
    async def sync_ap_to_cash_management(self, db: AsyncSession, payment_id: int):
        """Sync AP payment to cash management"""
        from ..core_financials.accounts_payable.models import Payment as APPayment
        from ..core_financials.cash_management.models import BankTransaction
        
        # Get AP payment
        ap_payment_query = select(APPayment).where(APPayment.id == payment_id)
        result = await db.execute(ap_payment_query)
        ap_payment = result.scalar_one_or_none()
        
        if not ap_payment or ap_payment.status != "approved":
            return None
        
        # Create corresponding bank transaction
        bank_transaction = BankTransaction(
            account_id=ap_payment.bank_account_id,
            transaction_date=ap_payment.payment_date,
            transaction_type="withdrawal",
            amount=ap_payment.amount,
            reference_number=ap_payment.payment_number,
            memo=f"AP Payment: {ap_payment.payment_number}",
            status="posted",
            created_by=ap_payment.created_by
        )
        
        db.add(bank_transaction)
        await db.commit()
        
        return {
            "ap_payment_id": payment_id,
            "bank_transaction_id": bank_transaction.id,
            "amount": float(ap_payment.amount),
            "sync_status": "completed"
        }
    
    async def sync_ar_to_cash_management(self, db: AsyncSession, payment_id: int):
        """Sync AR payment to cash management"""
        from ..core_financials.accounts_receivable.models import ARPayment
        from ..core_financials.cash_management.models import BankTransaction
        
        # Get AR payment
        ar_payment_query = select(ARPayment).where(ARPayment.id == payment_id)
        result = await db.execute(ar_payment_query)
        ar_payment = result.scalar_one_or_none()
        
        if not ar_payment or ar_payment.status != "processed":
            return None
        
        # Create corresponding bank transaction
        bank_transaction = BankTransaction(
            account_id=ar_payment.bank_account_id,
            transaction_date=ar_payment.payment_date,
            transaction_type="deposit",
            amount=ar_payment.amount,
            reference_number=ar_payment.payment_number,
            memo=f"AR Payment: {ar_payment.payment_number}",
            status="posted",
            created_by=ar_payment.created_by
        )
        
        db.add(bank_transaction)
        await db.commit()
        
        return {
            "ar_payment_id": payment_id,
            "bank_transaction_id": bank_transaction.id,
            "amount": float(ar_payment.amount),
            "sync_status": "completed"
        }
    
    async def get_integrated_financial_summary(self, db: AsyncSession, company_id: int):
        """Get integrated financial summary across all modules"""
        from ..core_financials.accounts_payable.models import Payment as APPayment
        from ..core_financials.accounts_receivable.models import ARPayment
        from ..core_financials.cash_management.models import BankAccount
        from ..core_financials.budget.enhanced_models import Budget
        
        # Get AP summary
        ap_query = select(func.sum(APPayment.amount)).where(APPayment.status == "approved")
        ap_total = await db.scalar(ap_query) or 0
        
        # Get AR summary
        ar_query = select(func.sum(ARPayment.amount)).where(ARPayment.status == "processed")
        ar_total = await db.scalar(ar_query) or 0
        
        # Get cash position
        cash_query = select(func.sum(BankAccount.current_balance)).where(BankAccount.status == "active")
        cash_total = await db.scalar(cash_query) or 0
        
        # Get budget summary
        budget_query = select(func.sum(Budget.total_amount)).where(Budget.status == "approved")
        budget_total = await db.scalar(budget_query) or 0
        
        return {
            "company_id": company_id,
            "financial_summary": {
                "accounts_payable": {"total_payments": float(ap_total)},
                "accounts_receivable": {"total_receipts": float(ar_total)},
                "cash_management": {"total_cash": float(cash_total)},
                "budget_management": {"total_budgets": float(budget_total)}
            },
            "net_cash_flow": float(ar_total - ap_total),
            "integration_status": "active",
            "last_updated": datetime.utcnow().isoformat()
        }